#!/usr/bin/env just --justfile

build:
  python -m build

test:
  python -m pytest tests/
