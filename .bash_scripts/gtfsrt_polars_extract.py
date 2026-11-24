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
from datetime import datetime as dt

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
        "output_path", help="Path to output parquet file."
    )
    return parser.parse_args(argv)


def parse_date(date: str) -> dt.DateTime:
    if not (date == ''):
        return dt.strptime(date, "%Y%m%d").date()
    return None

def parse_time(time: str) -> dt.DateTime:
    if not (time == ''):
        return dt.strptime(time, "%H:%M:%S").time()
    return None


def process_feed_string(feed) -> pl.DataFrame:
    schema={
        "id": pl.datatypes.String,
        "trip_id": pl.datatypes.String,
        "start_date": pl.datatypes.Date,
        "start_time": pl.datatypes.Time,
        "route_id": pl.datatypes.String,
        "latitude": pl.datatypes.Float64,
        "longitude": pl.datatypes.Float64,
        "timestamp": pl.datatypes.Time,
        "vehicle_id": pl.datatypes.String
    }

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
            v.timestamp,
            v.vehicle.id or None,
        ))

    return pl.DataFrame(rows,schema=schema,orient="row")


def main(argv=None):
    args = parse_args(argv)

    dfs = []
    for path in glob(args.glob_path):
        print(path)
        feed = gtfs_realtime_pb2.FeedMessage()
        with zipfile.ZipFile(path, "r") as f:
            feed.ParseFromString(f.read("gtfsrt.bin"))

        dfs.append(process_feed_string(feed))

    df = pl.concat(dfs)
    df.write_parquet(args.output_path)


if __name__ == "__main__":
    main()

