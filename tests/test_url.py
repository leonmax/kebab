import json
import os
import tempfile

import pytest

from kebab.sources import load_source, UrlSource
from tests.tools import mock_opener


@pytest.fixture
def file_name():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as fp:
        json.dump({"name": 1}, fp)
        file_name = fp.name
    yield file_name
    os.remove(file_name)


def test_url_with_source():
    s = load_source(default_urls="mock://", opener=mock_opener({"name": 1}))
    assert s.get("name") == 1


def test_url():
    s = UrlSource("mock://", opener=mock_opener({"name": 1}))
    assert s.get("name") == 1


def test_filename_with_load_source(file_name):
    s = load_source(default_urls=file_name)
    assert s.get("name") == 1


def test_filename_only(file_name):
    s = UrlSource(file_name)
    assert s.get("name") == 1
