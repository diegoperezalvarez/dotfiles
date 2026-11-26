#!/usr/bin/env python3
"""
render-preview.py: write an HTML page that renders every page of a .drawio file, for a visual check.

Usage:
    python scripts/render-preview.py <diagram.drawio> [--out preview.html] [--zoom 1.0]

Then serve the folder and open it in a browser (file:// URLs may be blocked by the integrated browser):
    python -m http.server 8765 --bind 127.0.0.1      # from the folder holding preview.html
    open http://127.0.0.1:8765/preview.html

The page loads the draw.io viewer script from https://viewer.diagrams.net. Rendering happens in the
browser; the diagram XML is embedded in the local HTML and is not uploaded. Do not use this for
diagrams that must never touch a page with third-party script, and delete the preview afterwards.

Each diagram page is in <div id="d0">, <div id="d1">, ... so a browser tool can scroll to it.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

VIEWER = "https://viewer.diagrams.net/js/viewer-static.min.js"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("diagram")
    ap.add_argument("--out", default="preview.html")
    ap.add_argument("--zoom", type=float, default=1.0)
    a = ap.parse_args()

    xml = Path(a.diagram).read_text(encoding="utf-8")
    pages = xml.count("<diagram ")
    divs = "".join(
        f'<div id="d{i}" class="mxgraph" data-mxgraph="'
        + html.escape(json.dumps({"xml": xml, "page": i, "nav": False, "toolbar": "", "lightbox": False,
                                  "resize": True, "zoom": a.zoom}))
        + '"></div>'
        for i in range(pages)
    )
    Path(a.out).write_text(
        f'<html><body style="background:#fff;margin:0">{divs}<script src="{VIEWER}"></script></body></html>',
        encoding="utf-8",
    )
    print(f"wrote {a.out} ({pages} page(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
