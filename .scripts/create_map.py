#!/usr/bin/env python

import sys
import argparse
import platform
import subprocess
import webbrowser
from pathlib import Path

import geopandas as gpd


def ensure_path_to_file(path):
  if "microsoft" in platform.uname().release.lower():
    return subprocess.check_output(
      ["wslpath", "-w", str(path)],
      text=True
    ).strip()
  else:
    return path


def process_args():
    parser = argparse.ArgumentParser(
        description="Visualise a geospatial file in a browser using GeoPandas."
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input file readable by GeoPandas."
    )

    geom_group = parser.add_mutually_exclusive_group()

    geom_group.add_argument(
        "--geometry-column",
        default="geometry",
        metavar="COLUMN",
        help="Column containing WKT geometries (default: %(default)s)."
    )

    geom_group.add_argument(
        "--xy-columns",
        nargs=2,
        metavar=("X_COLUMN", "Y_COLUMN"),
        help="Columns containing X and Y coordinates."
    )

    parser.add_argument(
        "-c",
        "--crs",
        default="EPSG:4326",
        help="Coordinate reference system for WKT geometries (default: %(default)s)."
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML file. Defaults to <input-file>.html."
    )

    args = parser.parse_args()

    if args.output is None:
        args.output = args.input_file.with_suffix(".html")

    return args


def main():
    args = process_args()

    input_file = args.input_file
    geom_col = args.geometry_column
    crs = args.crs
    output_html = str(args.output)

    gdf = gpd.read_file(input_file)

    if not isinstance(gdf, gpd.GeoDataFrame):
        if args.xy_columns:
            x_col, y_col = args.xy_columns
            gdf = gpd.GeoDataFrame(
                gdf,
                geometry=gpd.points_from_xy(
                    gdf[x_col],
                    gdf[y_col],
                ),
                crs=args.crs,
            )
        else:
            gdf = gpd.GeoDataFrame(
                gdf.drop(columns=[args.geometry_column]),
                geometry=gpd.GeoSeries.from_wkt(
                    gdf[args.geometry_column]
                ),
                crs=args.crs,
            )

    gdf.explore(
        tiles="OpenStreetMap"
    ).save(output_html)

    webbrowser.open(
        ensure_path_to_file(Path(output_html).resolve())
    )

    print(f"Saved {output_html}")


if __name__ == "__main__":
  main()
