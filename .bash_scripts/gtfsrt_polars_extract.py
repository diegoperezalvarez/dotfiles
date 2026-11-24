#!/usr/bin/env python
"""
Collates files from a glob-path string, compatible with the bods national
archive (https://data.datalibrary.uk/transport/BODS-ARCHIVE/).
"""
import os
import sys
import zipfile
import argparse
from glob import glob
from datetime import date, time, datetime as dt

from google.transit import gtfs_realtime_pb2
import polars as pl


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "glob_path", help="Path to glob *.zip files."
    )
    parser.add_argument(
        "output_path", help="Path to output csv file."
    )
    parser.add_argument(
        "--parquet", default=False,
        action=argparse.BooleanOptionalAction,
        help="Optionally parse the output_path to parquet."
    )
    return parser.parse_args(argv)


def parse_date(date: str) -> date | None:
    if not (date == ''):
        return dt.strptime(date, "%Y%m%d").date()
    return None


def parse_time(time: str) -> time | None:
    if not (time == ''):
        return dt.strptime(time, "%H:%M:%S").time()
    return None


SCHEMA = {
    "id": pl.datatypes.String,
    "trip_id": pl.datatypes.String,
    "start_date": pl.datatypes.Date,
    "start_time": pl.datatypes.Time,
    "route_id": pl.datatypes.String,
    "latitude": pl.datatypes.Float64,
    "longitude": pl.datatypes.Float64,
    "bearing": pl.datatypes.Float64,
    "timestamp": pl.datatypes.Int64,
    "vehicle_id": pl.datatypes.String
}


def process_feed_string(feed) -> pl.DataFrame:
    rows = []
    for entity in feed.entity:
        v = entity.vehicle
        rows.append((
            entity.id or None,
            v.trip.trip_id or None,
            parse_date(v.trip.start_date),
            parse_time(v.trip.start_time),
            v.trip.route_id or None,
            v.position.latitude,
            v.position.longitude,
            v.position.bearing,
            v.timestamp,
            v.vehicle.id or None,
        ))

    return pl.DataFrame(rows, schema=SCHEMA, orient="row")


def csv_to_parquet(csv_path) -> None:
    parquet_path = os.path.splitext(csv_path)[0] + ".parquet"
    pl.scan_csv(csv_path, schema=SCHEMA)\
        .with_columns(pl.from_epoch('timestamp', time_unit='s'))\
        .sink_parquet(parquet_path)
    os.unlink(csv_path)


def main(argv=None):
    args = parse_args(argv)
    paths = sorted(glob(args.glob_path))

    if os.path.exists(args.output_path) and args.parquet:
        csv_to_parquet(args.output_path)
        return 0

    include_header = True
    with open(args.output_path, "ab") as out_f:
        for path in paths:
            print(path)
            feed = gtfs_realtime_pb2.FeedMessage()
            with zipfile.ZipFile(path, "r") as f:
                feed.ParseFromString(f.read("gtfsrt.bin"))

            df = process_feed_string(feed)
            if df.is_empty():
                continue

            df.write_csv(out_f, include_header=include_header)
            include_header = False

    if args.parquet:
         csv_to_parquet(args.output_path)

    return 0


if __name__ == "__main__":
    main()
