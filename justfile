#!/usr/bin/env just --justfile

python_src := "cff_from_621 tests"

black:
  python -m black {{python_src}}

build:
  python -m build

lint:
  python -m flake8 --max-line-length=88 {{python_src}}

test:
  python -m pytest tests/
