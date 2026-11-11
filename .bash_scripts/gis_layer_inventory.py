#!/usr/bin/env python
"""Inventory spatial layers under a root folder as root-relative paths.

Prints one line per layer, tab-separated: path, geometry type, feature count.
Paths are relative to ROOT, use forward slashes and a leading slash, e.g.
    /Neath Port Talbot/ldp_npt_green_wedge.gpkg:ldp_green_wedge
    /Swansea/AQMA.shp
QGIS layer_styles tables are skipped. Unreadable files are reported on stderr.

Needs geopandas (and pyogrio) in the Python that runs it.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path

import geopandas as gpd
import pyogrio

SPATIAL_SUFFIXES = {".gpkg", ".shp"}
SKIP_LAYERS = {"layer_styles"}


def layers_in(path: Path) -> Iterator[tuple[str | None, str | None, int]]:
    if path.suffix.lower() == ".gpkg":
        for name, geom_type in gpd.list_layers(path).itertuples(index=False):
            if name not in SKIP_LAYERS:
                features = pyogrio.read_info(path, layer=name)["features"]
                yield name, geom_type, features
    else:
        info = pyogrio.read_info(path)
        yield None, info["geometry_type"], info["features"]


def process_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "root",
        type=Path,
        help="Root folder to search recursively for .gpkg and .shp files."
    )

    return parser.parse_args()


def main() -> None:
    args = process_args()
    root = args.root.resolve()
    for path in sorted(p for p in root.rglob("*") if p.suffix.lower() in SPATIAL_SUFFIXES):
        rel = "/" + path.relative_to(root).as_posix()
        try:
            for layer, geom_type, features in layers_in(path):
                ref = f"{rel}:{layer}" if layer else rel
                print(f"{ref}\t{geom_type}\t{features}")
        except Exception as exc:
            print(f"{rel}\tERROR\t{exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
