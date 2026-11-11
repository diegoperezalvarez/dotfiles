#!/usr/bin/env python
"""
Places multiple vector files into a single geopackage, reprojecting to a common
CRS.
"""
import os
import csv
import sys
import argparse

import geopandas as gpd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "parser_csv", help=(
        "CSV whose first three columns are an abs path, layer_name, new_layer "
        "(read by position; no header row is expected). If no gpkg_output arg "
        "is supplied, assume there is a 4th column with gpkg_output. "
        "layer_name may be blank for single-layer files (e.g. shapefiles).")
    )
    parser.add_argument(
        "--gpkg-output", default=None,
        help="Path to output geopackage. If blank read from parser_csv."
    )
    parser.add_argument(
        "--crs", default="EPSG:4326",
        help="Output CRS (default: %(default)s)"
    )
    return parser.parse_args(argv)


def gen_layer_defs(csv_path, gpkg_output=None):
    """Yields (path, layer_name/None, new_layer, gpkg) tuples."""
    with open(csv_path, newline="") as file:
        for row in csv.reader(file):
            yield row[0], row[1] or None, row[2], gpkg_output or row[3]


def main(argv=None):
    args = parse_args(argv)
    crs = args.crs

    for path, layer_name, new_layer, gpkg_output in gen_layer_defs(
            args.parser_csv, args.gpkg_output):
        try:
            gdf = gpd.read_file(path, layer=layer_name)
            gdf = gdf.to_crs(crs)
        except Exception as e:
            print(f"Error reading {path} ({layer_name}): {e}", file=sys.stderr)
            continue

        gdf.to_file(
            gpkg_output,
            layer=new_layer,
            driver="GPKG",
            FID="agg_to_gpkg_fid")
        print(f"Wrote {new_layer}: {len(gdf)} features.")


if __name__ == "__main__":
    main()
