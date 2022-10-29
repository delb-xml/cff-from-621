import logging
from datetime import date
from importlib import import_module
from itertools import chain
from pathlib import Path
from typing import Any, Sequence

import yaml
from cffconvert import Citation  # type: ignore
from jsonschema.exceptions import ValidationError  # type: ignore

try:  # DROPWITH Python3.9
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore

CONSIDERED_PROJECT_FIELDS = frozenset(
    ("authors", "description", "keywords", "license", "title", "urls", "version")
)
DEFAULT_FIELD_ORDER = (
    "cff-version",
    "type",
    "title",
    "version",
    "date-released",
    "authors",
    "license",
    "message",
    "abstract",
    "url",
    "contact",
    "repository-code",
    "keywords",
)


log = logging.getLogger("cff_from_621")


def generate_cff_contents(pyproject_contents: dict, pyproject_path: Path) -> dict:
    tool_tables = pyproject_contents.get("tool", {}).get("cff-from-621", {})
    order = tool_tables.pop("order", DEFAULT_FIELD_ORDER)
    resolve_dynamic_values(
        pyproject_contents=pyproject_contents, pyproject_path=pyproject_path
    )

    result = (
        {"cff-version": "1.2.0", "type": "software"}
        | map_621_to_cff(pyproject_contents["project"])
        | tool_tables.get("static", {})
    )
    result |= render_templates(
        templates_table=tool_tables.get("template", {}), data=result
    )

    if "date-released" not in result:
        result["date-released"] = date.today().isoformat()

    return sorted_cff_contents(order, result)


def generate_cff_file(pyproject_path: Path, cff_path: Path, width: int):
    pyproject_contents = tomllib.loads(pyproject_path.read_text())
    cff_contents = generate_cff_contents(
        pyproject_contents=pyproject_contents, pyproject_path=pyproject_path
    )
    cff_serialisat = yaml.dump(
        allow_unicode=True,
        data=cff_contents,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True,
        indent=2,
        sort_keys=False,
        width=width,
    )
    try:
        Citation(cffstr=cff_serialisat).validate()
    except ValidationError as e:
        logging.error(f"Validation error: {e.message}")
        raise SystemExit(1)
    cff_path.write_text(data=cff_serialisat)


def map_621_to_cff(data: dict) -> dict:
    result = {"title": data["name"], "version": data["version"]}

    authors_cff = {}
    for author_621 in chain(data.get("authors", ()), data.get("maintainers", ())):
        author_cff = {}
        key = None
        if "name" in author_621:
            key = author_621["name"]
            author_cff["name"] = key

        if "email" in author_621:
            if key is None:
                author_cff["email"] = key = author_621["email"]
            else:
                author_cff["email"] = author_621["email"]

        assert key is not None

        if key not in authors_cff:
            authors_cff[key] = author_cff

    if authors_cff:
        result["authors"] = list(authors_cff.values())

    for src, dst in (
        ("description", "abstract"),
        ("keywords", "keywords"),
        ("license", "license"),
    ):
        if src in data:
            result[dst] = data[src]

    urls = data.get("urls", {})

    repository = urls.get("Repository", urls.get("repository"))
    if repository is not None:
        result["repository-code"] = repository

    for key in ("Homepage", "homepage", "Documentation", "documentation"):
        if key in urls:
            result["url"] = urls[key]
            break

    return result


def render_templates(templates_table: dict, data: dict) -> dict:
    return {k: v.format(**data) for k, v in templates_table.items()}


def resolve_dynamic_setuptools_values(pyproject_contents: dict, pyproject_path: Path):
    project_table = pyproject_contents["project"]
    references_table = pyproject_contents["tool"]["setuptools"]["dynamic"]

    for field, reference in (
        (x, references_table[x])
        for x in project_table["dynamic"]
        if x in CONSIDERED_PROJECT_FIELDS
    ):
        if "file" in reference:
            project_table[field] = (
                pyproject_path.parent / reference["file"]
            ).read_text()
        elif "attr" in reference:
            project_table[field] = retrieve_object(reference["attr"])
        else:
            log.error(f"Unknown reference type for field `{field}`.")
            raise SystemExit(1)


def resolve_dynamic_values(pyproject_contents: dict, pyproject_path: Path):
    if not (
        set(pyproject_contents["project"].get("dynamic", ()))
        & CONSIDERED_PROJECT_FIELDS
    ):
        return

    if pyproject_contents["build-system"]["build-backend"].startswith("setuptools."):
        resolve_dynamic_setuptools_values(
            pyproject_contents=pyproject_contents, pyproject_path=pyproject_path
        )
    else:
        log.error(
            "Dynamic value resolution is not available for the used build backend."
        )
        raise SystemExit(1)


def retrieve_object(location: str) -> Any:
    names = location.split(".")

    for i in range(len(names) - 1, 1, -1):
        try:
            module = import_module(".".join(names[:i]))
        except ImportError:
            pass
        else:
            member_path = names[i:]
            break
    else:
        log.error(f"Couldn't import module to reach {location}")
        raise SystemExit(1)

    obj = module
    for name in member_path:
        obj = getattr(obj, name)

    return obj


def sorted_cff_contents(order: Sequence[str], data: dict) -> dict:
    result = {}
    for field in (x for x in order if x in data):
        result[field] = data.pop(field)
    return result | data
