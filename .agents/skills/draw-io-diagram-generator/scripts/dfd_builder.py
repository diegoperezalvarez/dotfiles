#!/usr/bin/env python3
"""
dfd_builder.py: build Yourdon / DeMarco data flow diagrams (.drawio) from Python.

Standard library only. Import it from a spec script, or run it to regenerate the template:

    python scripts/dfd_builder.py --example assets/templates/data-flow-diagram.drawio

Minimal spec:

    import sys; sys.path.insert(0, ".agents/skills/draw-io-diagram-generator/scripts")
    from dfd_builder import DfdDocument

    doc = DfdDocument()
    dfd = doc.page("dfd", "Data flow diagram", 1400, 900)
    dfd.title("Order system: data flow diagram")
    dfd.boundary("Order system", 260, 120, 1000, 600)
    dfd.external("customer", "Customer", 40, 260, kind="user")
    dfd.process("take-order", "Take order", 420, 300)
    dfd.flow("customer", "take-order", "Order request", "customer's basket")
    dfd.flow("take-order", "customer", "Order confirmation", "order id and status", via=[(330, 230)])
    doc.write("docs/order-dfd.drawio")   # writes, then runs dfd_lint and prints the findings

Every vertex carries a custom style key `dfd=<role>` (external, process, store, boundary, note) and
flows carry `dfd=flow`, so scripts/dfd_lint.py can check the diagram without guessing. draw.io keeps
unknown style keys, so the file still opens normally.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

STYLES = {
    # title style must contain text; and fontSize=18 to satisfy validate-drawio.py
    "title": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=18;fontStyle=1;whiteSpace=wrap;",
    "subtitle": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=11;whiteSpace=wrap;fontColor=#333333;",
    "external": "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=11;dfd=external;",
    "process": "ellipse;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;fontSize=11;dfd=process;",
    # Yourdon / DeMarco store: two parallel horizontal lines (open both ends)
    "store": "shape=partialRectangle;left=0;right=0;top=1;bottom=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#000000;strokeWidth=2;fontSize=11;dfd=store;",
    "boundary": "rounded=1;arcSize=2;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;strokeWidth=2;dashed=1;dashPattern=8 4;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;fontStyle=1;fontSize=13;fontColor=#444444;dfd=boundary;",
    "note": "shape=note;size=14;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;align=left;verticalAlign=top;spacing=8;fontSize=10;dfd=note;",
    "flow": "edgeStyle=none;rounded=1;html=1;endArrow=classic;endFill=1;strokeWidth=1.5;fontSize=9;labelBackgroundColor=#ffffff;dfd=flow;",
}

_SIDES = {"left": (0, 0.5), "right": (1, 0.5), "top": (0.5, 0), "bottom": (0.5, 1)}

LEGEND = ("<b>Notation</b><br>"
          "Grey oval = process<br>"
          "Two parallel lines = data store<br>"
          "Blue rectangle = external user or service, outside the system<br>"
          "Arrow = one dataset moving, labelled with its content and form<br>"
          "Dashed box = system boundary<br>"
          "* = store drawn again to avoid crossing lines")


class DfdPage:
    def __init__(self, pid: str, name: str, width: int, height: int):
        self.diagram = ET.Element("diagram", id=pid, name=name)
        model = ET.SubElement(
            self.diagram, "mxGraphModel", dx="1600", dy="1000", grid="1", gridSize="10", guides="1",
            tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1",
            pageWidth=str(width), pageHeight=str(height), math="0", shadow="0",
        )
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.ids = {"0", "1"}
        self._dup = {}
        self._n = 0

    # -- vertices -------------------------------------------------------------------------------
    def _v(self, cid, label, style, x, y, w, h):
        if cid in self.ids:
            raise ValueError(f"duplicate cell id {cid!r}")
        self.ids.add(cid)
        c = ET.SubElement(self.root, "mxCell", id=cid, value=label, style=style, vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        return cid

    def title(self, text, x=40, y=20, w=1000, h=40):
        return self._v("title", text, STYLES["title"], x, y, w, h)

    def subtitle(self, text, x=40, y=60, w=1000, h=40):
        return self._v("subtitle", text, STYLES["subtitle"], x, y, w, h)

    def boundary(self, name, x, y, w, h):
        return self._v("boundary", name, STYLES["boundary"], x, y, w, h)

    def external(self, eid, name, x, y, kind="service", sub="", w=200, h=70):
        """kind: 'user' (person or team) or 'service' (system outside the boundary)."""
        label = (f"<b>{name}</b><br><i style='font-size:9px'>External {kind}</i>"
                 + (f"<br><font style='font-size:9px'>{sub}</font>" if sub else ""))
        return self._v(eid, label, STYLES["external"] + f"dfdId={eid};", x, y, w, h)

    def process(self, pid, name, x, y, d=150, sub=""):
        """Grey oval. Use a plain verb phrase for the name; sub is an optional small line (e.g. '<<Lambda>>')."""
        label = f"<b>{name}</b>" + (f"<br><font style='font-size:9px'>{sub}</font>" if sub else "")
        return self._v(pid, label, STYLES["process"] + f"dfdId={pid};", x, y, d, d)

    def store(self, did, name, x, y, w=220, h=44, sub="", duplicate=False, io=""):
        """Data store. duplicate=True draws a '*' copy; io='sink'|'source' marks a store fed or read outside."""
        n = self._dup.get(did, 0)
        cid = did if not duplicate else f"{did}-dup{n + 1}"
        self._dup[did] = n + (1 if duplicate else 0)
        label = f"<b>{name}{' *' if duplicate else ''}</b>" + (
            f"<br><font style='font-size:9px'>{sub}</font>" if sub else "")
        style = STYLES["store"] + f"dfdId={did};" + (f"dfdIo={io};" if io else "")
        return self._v(cid, label, style, x, y, w, h)

    def note(self, cid, html_text, x, y, w, h):
        return self._v(cid, html_text, STYLES["note"], x, y, w, h)

    def legend(self, x, y, w=380, h=170):
        return self.note("legend", LEGEND, x, y, w, h)

    # -- flows ----------------------------------------------------------------------------------
    def flow(self, src, tgt, name, detail="", via=None, exit=None, entry=None):
        """name: short plain-English name for the dataset. detail: short note on content and form, drawn under it.
        via: list of (x, y) waypoints the arrow passes through.
        exit / entry: 'left' | 'right' | 'top' | 'bottom' | (fx, fy) to pin the attachment point."""
        if src not in self.ids or tgt not in self.ids:
            raise ValueError(f"unknown endpoint in flow {src} -> {tgt}")
        self._n += 1
        cid = f"f{self._n}"
        style = STYLES["flow"]
        for key, side in (("exit", exit), ("entry", entry)):
            if side:
                fx, fy = _SIDES[side] if isinstance(side, str) else side
                style += f"{key}X={fx};{key}Y={fy};{key}Dx=0;{key}Dy=0;"
        self.ids.add(cid)
        label = name + (f"<br><font style='font-size:8px'>{detail}</font>" if detail else "")
        c = ET.SubElement(self.root, "mxCell", id=cid, value=label, style=style, edge="1", parent="1",
                          source=src, target=tgt)
        g = ET.SubElement(c, "mxGeometry", relative="1", **{"as": "geometry"})
        if via:
            arr = ET.SubElement(g, "Array", **{"as": "points"})
            for px, py in via:
                ET.SubElement(arr, "mxPoint", x=str(px), y=str(py))
        return cid


class DfdDocument:
    def __init__(self):
        self.pages: list[DfdPage] = []

    def page(self, pid, name, width=1654, height=1169) -> DfdPage:
        p = DfdPage(pid, name, width, height)
        self.pages.append(p)
        return p

    def write(self, path, lint=True) -> int:
        """Write the .drawio file. With lint=True, run dfd_lint and return its error count."""
        mxfile = ET.Element("mxfile", host="Electron", version="26.0.0",
                            modified=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        for p in self.pages:
            mxfile.append(p.diagram)
        ET.indent(mxfile, space="  ")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=False)
        print(f"written {path}")
        if not lint:
            return 0
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from dfd_lint import lint as run_lint
        errors, warns = run_lint(Path(path))
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warns:
            print(f"  WARN:  {w}")
        print(f"dfd_lint: {len(errors)} error(s), {len(warns)} warning(s)")
        return len(errors)


# ------------------------------------------------------------------------------------------------
def build_example() -> DfdDocument:
    """Small order-system example: one data flow diagram page."""
    doc = DfdDocument()

    dfd = doc.page("dfd", "Data flow diagram", 1700, 1000)
    dfd.title("Order system: data flow diagram", w=800)
    dfd.boundary("Order system", 260, 120, 1160, 700)
    dfd.external("customer", "Customer", 40, 260, kind="user")
    dfd.external("payments", "Payment provider", 1470, 260)
    dfd.process("take-order", "Take order", 420, 300)
    dfd.process("take-payment", "Take payment", 1000, 300)
    dfd.store("orders", "Orders", 700, 560, w=200)
    dfd.flow("customer", "take-order", "Order request", "customer's basket")
    dfd.flow("take-order", "customer", "Order confirmation", "order id and status", via=[(330, 230)])
    dfd.flow("take-order", "orders", "Order record", "one row per order", exit="bottom", entry="left")
    dfd.flow("orders", "take-payment", "Order total", "amount due", exit="top", entry="bottom")
    dfd.flow("take-payment", "payments", "Payment request", "amount and card token")
    dfd.flow("payments", "take-payment", "Payment result", "approved or declined",
            via=[(1300, 450)], exit="left", entry="bottom")
    dfd.legend(40, 860, w=420, h=130)
    return doc


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--example":
        sys.exit(1 if build_example().write(sys.argv[2]) else 0)
    print(__doc__)
    sys.exit(1)
