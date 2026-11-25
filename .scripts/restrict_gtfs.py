#!/usr/bin/env python
"""Restrict a GTFS feed to a subset of its data using gtfs_kit.

Exactly one restriction is applied per run, selected by a single flag:
--area, --agencies, --dates, --routes or --trips.

ID and date lists can be given inline or read from a text file by prefixing
the file path with '@' (one value per line), e.g. --routes @routes.txt
"""

import argparse
import logging
import sys

import geopandas as gpd
import gtfs_kit as gtk

logger = logging.getLogger(__name__)

DIST_UNITS = ["m", "km", "ft", "mi"]


def restrict_area(feed, values, args):
    """Restrict the feed to stops within a boundary file."""
    boundary = gpd.read_file(values)
    if boundary.crs is None:
        logger.warning("Boundary has no CRS; assuming %s", args.crs)
        boundary = boundary.set_crs(args.crs)
    elif boundary.crs != args.crs:
        logger.info("Reprojecting boundary from %s to %s", boundary.crs, args.crs)
        boundary = boundary.to_crs(args.crs)
    return feed.restrict_to_area(boundary)


def restrict_agencies(feed, values, args):
    return feed.restrict_to_agencies(values)


def restrict_dates(feed, values, args):
    return feed.restrict_to_dates(values)


def restrict_routes(feed, values, args):
    return feed.restrict_to_routes(values)


def restrict_trips(feed, values, args):
    return feed.restrict_to_trips(values)


RESTRICTIONS = {
    "area": restrict_area,
    "agencies": restrict_agencies,
    "dates": restrict_dates,
    "routes": restrict_routes,
    "trips": restrict_trips,
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars="@",
    )
    parser.add_argument("feed", help="path to the input GTFS feed (.zip or directory)")
    parser.add_argument("output", help="path to write the restricted GTFS feed "
                        "(.zip or directory); existing output is overwritten")
    parser.add_argument("--dist-units", choices=DIST_UNITS, default="m",
                        help="distance units of the input feed (default: %(default)s)")
    parser.add_argument("--crs", default="EPSG:4326",
                        help="CRS to reproject the --area boundary to "
                        "(default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="increase log verbosity (-v for INFO, -vv for DEBUG)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--area", metavar="BOUNDARY",
                       help="restrict to stops within a single-layer boundary file "
                       "readable by geopandas")
    group.add_argument("--agencies", nargs="+", metavar="AGENCY_ID",
                       help="restrict to one or more agency_id values")
    group.add_argument("--dates", nargs="+", metavar="YYYYMMDD",
                       help="restrict to one or more service dates")
    group.add_argument("--routes", nargs="+", metavar="ROUTE_ID",
                       help="restrict to one or more route_id values")
    group.add_argument("--trips", nargs="+", metavar="TRIP_ID",
                       help="restrict to one or more trip_id values")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    level = [logging.WARNING, logging.INFO, logging.DEBUG][min(args.verbose, 2)]
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    name = next(k for k in RESTRICTIONS if getattr(args, k) is not None)
    values = getattr(args, name)
    logger.debug("Restriction: %s, values: %s", name, values)

    logger.info("Reading feed %s", args.feed)
    feed = gtk.read_feed(args.feed, dist_units=args.dist_units)

    logger.info("Restricting feed to %s", name)
    restricted = RESTRICTIONS[name](feed, values, args)

    if restricted.trips is None or restricted.trips.empty:
        logger.warning("Restricted feed contains no trips")

    logger.info("Writing restricted feed to %s", args.output)
    restricted.to_file(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
