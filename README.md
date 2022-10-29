# cff-from-621

This tool derives a [`CITATION.cff`](https://citation-file-format.github.io/)
file from a Python project's `pyproject.toml` contents that provide
[PEP-621](https://peps.python.org/pep-0621/) compliant package metadata.

## Features

- Additional and overriding values can be provided statically or via Python
  string templates.
- Order of the resulting fields can be defined, has a non-arbitrary default.
- Dynamic fields are resolved for the `setuptools` build backend.

## Example

Given a `pyproject.toml` that includes these contents:

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "cff-from-621"
description = "Generates metadata in the Citation File Format for Python projects from their PEP-621 compliant package definition. Includes a CLI."
keywords = ["PEP-621", "CFF", "conversion"]
authors = [
    {name = "Frank Sachsenheim"}
]
dynamic = ["version"]

[tool.cff-from-621]
order = ["message", "cff-version", "title", "abstract", "version", "date-released", "authors", "keywords"]

[tool.cff-from-621.static]
date-released = "2022-09-18"
message = "🔥🌍🔥"

[tool.setuptools.dynamic]
version = {attr = "cff_from_621.version.VERSION"}
```

`cff-from-621` would derive this `CITATION.cff`:

```yaml
---
message: 🔥🌍🔥
cff-version: 1.2.0
title: cff-from-621
abstract: Generates metadata in the Citation File Format for Python projects from
  their PEP-621 compliant package definition. Includes a CLI.
version: 0.0.1
date-released: '2022-09-18'
authors:
- name: Frank Sachsenheim
keywords:
- PEP-621
- CFF
- conversion
type: software
...
```

## Installation

Add `cff-from-621` with your environment management or install it globally
with [pipx](https://pypa.github.io/pipx/):

    $ pipx install cff-from-621

## Usage

Change into your project's root folder and jump right in with:

    $ cff-from-621

The usage details can be explored with:

    $ cff-from-621 --help

### Caveats

1. Authors / maintainers are represented as [entity type](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md#definitionsentity)
   because their PEP-621 representation can't be parsed into the atomicity of the
   [person type](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md#definitionsperson).

## Development

This tool isn't supposed to cover each and every corner case that may exist.
Its implementation shall be kept simple and may be used as library for custom
extensions and alterations.
All contributions within that frame are welcome.

In a virtual environment that you set up for development, install this package
from source in editable mode and required development tools:

    $ pip install .[development]

Make use of or refer to the accompanying [`justfile`](https://just.systems/) to
run common development tasks.
