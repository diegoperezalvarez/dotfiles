#!/usr/bin/env python3
"""
dfd_lint.py: check a Yourdon / DeMarco data flow diagram (.drawio) against simple DFD rules.

Usage:
    python scripts/dfd_lint.py <diagram.drawio> [--strict]

Roles are read from the custom style key `dfd=` written by dfd_builder.py
(dfd=external|process|store|boundary|flow|note). Hand-drawn diagrams fall back to shape
heuristics: ellipse = process, partialRectangle = store, unrounded blue rectangle = external.

Rules
  ERROR  R1 every flow touches at least one process (no external-to-store or store-to-store flows)
  ERROR  R2 every flow carries a name
  ERROR  R3 every process has at least one input and one output flow
  ERROR  R4 externals sit outside the system boundary; processes and stores sit inside it
  WARN   R5 every data store is both written and read, unless it declares dfdIo=sink or dfdIo=source
  WARN   R6 no flow passes through a shape other than its own source and target

Exit codes: 0 no errors (warnings allowed unless --strict), 1 errors found.
"""
from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

def style_map(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (style or "").split(";"):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
        else:
            out[part] = "1"
    return out


def plain(value: str) -> str:
    value = re.sub(r"<br\s*/?>|<hr[^>]*>", "\n", value or "", flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).replace("\xa0", " ")


def flow_name(label: str) -> str:
    return plain(label).strip().split("\n")[0].strip()


@dataclass
class Node:
    cid: str
    role: str
    key: str
    label: str
    geo: tuple[float, float, float, float] | None
    io: str = ""


@dataclass
class Flow:
    cid: str
    src: str
    tgt: str
    name: str
    style: dict[str, str]
    points: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class PageModel:
    name: str
    nodes: dict[str, Node]
    flows: list[Flow]


def classify(style: dict[str, str]) -> str:
    if style.get("dfd"):
        return style["dfd"]
    if style.get("shape") == "partialRectangle" and style.get("left") == "0" and style.get("right") == "0":
        return "store"
    if "ellipse" in style:
        return "process"
    if style.get("rounded") == "0" and style.get("fillColor") == "#dae8fc":
        return "external"
    return ""


def node_key(style: dict[str, str], cid: str) -> str:
    return style.get("dfdId") or cid


def load(path: Path) -> list[PageModel]:
    root = ET.parse(path).getroot()
    pages = []
    for d in root.findall("diagram"):
        gm = d.find("mxGraphModel")
        if gm is None:
            continue
        nodes: dict[str, Node] = {}
        raw_edges = []
        for c in gm.find("root").findall("mxCell"):
            st = style_map(c.get("style", ""))
            label = c.get("value", "")
            g = c.find("mxGeometry")
            if c.get("vertex") == "1":
                role = classify(st)
                geo = None
                if g is not None and c.get("parent") == "1":
                    geo = tuple(float(g.get(k, 0)) for k in ("x", "y", "width", "height"))
                nodes[c.get("id")] = Node(c.get("id"), role, node_key(st, c.get("id")), label, geo,
                                          st.get("dfdIo", ""))
            elif c.get("edge") == "1" and c.get("source") and c.get("target"):
                pts = []
                if g is not None:
                    arr = g.find("Array")
                    if arr is not None:
                        pts = [(float(p.get("x", 0)), float(p.get("y", 0))) for p in arr.findall("mxPoint")]
                raw_edges.append(Flow(c.get("id"), c.get("source"), c.get("target"), flow_name(label), st, pts))
        pages.append(PageModel(d.get("name", "?"), nodes, raw_edges))
    return pages


def anchor(geo, st: dict[str, str], prefix: str):
    x, y, w, h = geo
    if f"{prefix}X" in st and f"{prefix}Y" in st:
        return (x + w * float(st[f"{prefix}X"]), y + h * float(st[f"{prefix}Y"]))
    return (x + w / 2, y + h / 2)


def seg_hits(a, b, geo, pad=4.0) -> bool:
    x, y, w, h = geo
    x, y, w, h = x + pad, y + pad, w - 2 * pad, h - 2 * pad
    for i in range(61):
        t = i / 60
        px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if x <= px <= x + w and y <= py <= y + h:
            return True
    return False


def lint(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    pages = load(path)
    store_io: dict[str, set[str]] = {}
    declared_io = {n.key for p in pages for n in p.nodes.values() if n.role == "store" and n.io}

    for p in pages:
        pre = f"[{p.name}]"
        procs = {cid for cid, n in p.nodes.items() if n.role == "process"}
        if not procs:
            continue
        ins = {cid: 0 for cid in procs}
        outs = {cid: 0 for cid in procs}
        for f in p.flows:
            s, t = p.nodes.get(f.src), p.nodes.get(f.tgt)
            if s is None or t is None:
                continue
            if s.role in ("boundary", "note", "") and t.role in ("boundary", "note", ""):
                continue
            if s.role != "process" and t.role != "process":
                errors.append(f"{pre} R1 flow {f.cid} ({s.key} -> {t.key}) does not touch a process")
            if not f.name:
                errors.append(f"{pre} R2 flow {f.cid} ({s.key} -> {t.key}) has no name")
            if s.cid in outs:
                outs[s.cid] += 1
            if t.cid in ins:
                ins[t.cid] += 1
            if s.role == "store":
                store_io.setdefault(s.key, set()).add("read")
            if t.role == "store":
                store_io.setdefault(t.key, set()).add("write")
        for cid in procs:
            k = p.nodes[cid].key
            if ins[cid] == 0:
                errors.append(f"{pre} R3 process {k} has no input data flow (miracle)")
            if outs[cid] == 0:
                errors.append(f"{pre} R3 process {k} has no output data flow (black hole)")
        bounds = [n.geo for n in p.nodes.values() if n.role == "boundary" and n.geo]
        if bounds:
            bx, by, bw, bh = bounds[0]
            for n in p.nodes.values():
                if not n.geo or n.role not in ("external", "process", "store"):
                    continue
                x, y, w, h = n.geo
                inside = bx <= x and by <= y and x + w <= bx + bw and y + h <= by + bh
                if n.role == "external" and inside:
                    errors.append(f"{pre} R4 external {n.key} is inside the system boundary")
                if n.role != "external" and not inside:
                    errors.append(f"{pre} R4 {n.role} {n.key} is outside the system boundary")

        solid = {cid: n for cid, n in p.nodes.items() if n.geo and n.role in ("external", "process", "store", "note", "")}
        for f in p.flows:
            s, t = p.nodes.get(f.src), p.nodes.get(f.tgt)
            if not (s and t and s.geo and t.geo):
                continue
            path_pts = [anchor(s.geo, f.style, "exit")] + f.points + [anchor(t.geo, f.style, "entry")]
            for a, b in zip(path_pts, path_pts[1:]):
                for cid, n in solid.items():
                    if cid in (f.src, f.tgt) or n.role == "":
                        continue
                    if seg_hits(a, b, n.geo):
                        warns.append(f"{pre} R6 flow {f.cid} ({s.key} -> {t.key}) passes through {n.key}")
                        break

    for key, io in sorted(store_io.items()):
        if io != {"read", "write"} and key not in declared_io:
            warns.append(f"R5 data store {key} is only {'written' if 'write' in io else 'read'} in this document")

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warns))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if not args:
        print(__doc__)
        return 1
    path = Path(args[0])
    print(f"DFD lint: {path}")
    errors, warns = lint(path)
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warns:
        print(f"  WARN:  {w}")
    if errors or (strict and warns):
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warning(s).")
        return 1
    print(f"PASS: 0 errors, {len(warns)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
