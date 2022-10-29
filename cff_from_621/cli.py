import argparse
import sys
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from cff_from_621.lib import generate_cff_file
from cff_from_621.version import VERSION

B_ = "\033[1m"
_B = "\033[22m"
U_ = "\033[4m"
_U = "\033[24m"

log = logging.getLogger("cff_from_621")
console_handler = logging.StreamHandler(sys.stderr)
log.addHandler(console_handler)


def parse_args(args: list[str]) -> Namespace:
    parser = ArgumentParser(
        description=f"""
Derives a citation file from the {U_}[project]{_U} table in a `pyproject.toml`.

Additionally, fixed values can be defined in the table {U_}[tool.cff-from-621.static]{_U}
and the string values in {U_}[tool.cff-from-621.template]{_U} are formatted with Python's
{B_}str.format(){_B} while all available data is passed as source mapping for extrapolation.
{B_}setuptool's{_B} dynamic field references are resolved.

The contents of the resulting metadata is gathered in this order, where later stages
override values from previous ones:
- data mapped from the {U_}[project]{_U} table
- fixed data from the table {U_}[tool.cff-from-621.static]{_U}
- data generated from the templates in the {U_}[tool.cff-from-621.template]{_U} table

The order of fields can be defined in a list of field names provided for the key `order`
in the table {U_}[tool.cff-from-621]{_U}.

In doubt, mind these resources:
- https://peps.python.org/pep-0621/
- https://citation-file-format.github.io/
- https://docs.python.org/3/library/stdtypes.html#str.format
- https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#dynamic-metadata

Program version: {VERSION}
    """,  # noqa: E501
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument(
        "--destination",
        nargs="?",
        type=Path,
        metavar="FILE",
        default=Path.cwd() / "CITATION.cff",
        help="Destination file path, defaults to CITATION.cff in the current "
        "directory.",
    )

    parser.add_argument(
        "--source",
        nargs="?",
        type=Path,
        metavar="FILE",
        default=Path.cwd() / "pyproject.toml",
        help="Source file path, defaults to pyproject.toml in the current directory.",
    )

    parser.add_argument(
        "--width",
        nargs="?",
        type=int,
        metavar="INTEGER",
        default=79,
        help="Maximum number of characters per line in the resulting file, "
        "defaults to 79.",
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
