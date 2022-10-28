from __future__ import annotations

import argparse
import sys
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from cff_from_621.lib import generate_cff_file
from cff_from_621.version import VERSION


log = logging.getLogger("cff_from_621")
console_handler = logging.StreamHandler(sys.stderr)
log.addHandler(console_handler)


def parse_args(args: list[str]) -> Namespace:
    parser = ArgumentParser(
        description=f"""
Derives a citation file from the [project] table in a pyproject.toml.

Additionally, fixed values can be defined in the table [tool.cff-from-621.static] and 
the string values in [tool.cff-from-621.template] are formatted with Python's 
str.format() while all available data is passed as source mapping for extrapolation.

setuptool's dynamic field references are resolved.

The contents of the resulting metadata is gathered in this order, where later stages
override values from previous ones:

- dynamic values
- data mapped from the [project] table
- fixed data from the table [tool.cff-from-621.static]
- data generated from the templates in the [tool.cff-from-621.template] table

The order of fields can be defined in a list of field names provided for the key `order`
in the table [tool.cff-from-621].

In doubt, mind these resources:
- https://peps.python.org/pep-0621/
- https://citation-file-format.github.io/
- https://docs.python.org/3/library/stdtypes.html#str.format
- https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#dynamic-metadata

Program version: {VERSION}
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument(
        "--destination",
        nargs="?",
        type=Path,
        metavar="FILE",
        default=Path.cwd() / "CITATION.cff",
        help="Path to write to, defaults to CITATION.cff in the current directory.",
    )
    parser.add_argument(
        "--source",
        nargs="?",
        type=Path,
        metavar="FILE",
        default=Path.cwd() / "pyproject.toml",
        help="Path to read from, defaults to pyproject.toml in the current directory.",
    )

    parser.add_argument(
        "--width",
        nargs="?",
        type=int,
        metavar="INTEGER",
        default=79,
        help="Maximum number of characters per line.",
    )

    return parser.parse_args(args)


def cli():
    try:
        if sys.version_info < (3, 10):
            log.error("This tool requires Python 3.10 or later.")
            raise SystemExit(1)

        args = parse_args(sys.argv[1:])
        if args.verbose:
            log.setLevel(logging.DEBUG)
            console_handler.setLevel(logging.DEBUG)

        generate_cff_file(
            pyproject_path=args.source, cff_path=args.destination, width=args.width
        )

    except SystemExit as e:
        exit_code = e.code

    except Exception:
        log.exception("Caught unhandled exception.")
        exit_code = 3

    else:
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
