import os

import pytest

from kebab.sources import load_source, literal

# Caveats!!!
# The working directory must be the root of kebab, or the relative path below won't work


def test_import():
    s = literal(__import__=["tests/data/conf1.yaml"])
    assert s.get("string_field") == "better value"


def test_import_directly_from_file():
    s = load_source(default_urls=["tests/data/conf2.json"])
    assert s.get("string_field") == "better value"


def test_recursive_import():
    s = literal(__import__=["tests/data/conf2.json"])
    # data/conf2.json import data/conf1.yaml,
    # which overwrite the "good value" from the former
    assert s.get("string_field") == "better value"
