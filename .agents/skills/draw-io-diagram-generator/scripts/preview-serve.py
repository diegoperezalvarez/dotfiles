#!/usr/bin/env python3
"""
preview-serve.py: render a .drawio file and serve the preview on 127.0.0.1 for a browser visual check.

Usage:
    python scripts/preview-serve.py <diagram.drawio> [--port 8765]

Run it as an attached process and leave it running. Open http://127.0.0.1:<port>/preview.html
in the integrated browser (file:// URLs are blocked there). Stop the process with Ctrl+C or SIGTERM
to end the preview: the temporary folder is removed and the script prints that it was removed.
Do not detach it. SIGKILL cannot be trapped, so a killed run can leave its folder behind; the
folder path is printed at start so it can be removed by hand.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

RENDER = Path(__file__).resolve().parent / "render-preview.py"


def _stop(*_args) -> None:
    raise KeyboardInterrupt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("diagram")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()

    diagram = Path(a.diagram)
    if not diagram.is_file():
        print(f"not found: {diagram}", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="drawio-preview-"))
    signal.signal(signal.SIGTERM, _stop)
    print(f"Temporary folder: {tmp}", flush=True)
    try:
        rendered = subprocess.run(
            [sys.executable, str(RENDER), str(diagram), "--out", str(tmp / "preview.html")],
            check=False,
        )
        if rendered.returncode != 0:
            return rendered.returncode

        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp))
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler)
        except OSError as err:
            print(f"Cannot listen on 127.0.0.1:{a.port}: {err}. Choose another --port.", file=sys.stderr)
            return 1
        print(f"Preview of {diagram}: http://127.0.0.1:{a.port}/preview.html", flush=True)
        print("Stop this process (Ctrl+C or SIGTERM) to end the preview. Do not detach it.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Stopping preview server.", flush=True)
        finally:
            server.server_close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"Removed temporary folder: {tmp} (exists: {tmp.exists()})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
