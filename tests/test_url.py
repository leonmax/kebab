import json
import os
import sys
import tempfile
from urllib.request import build_opener

import pytest

from kebab.sources import load_source, UrlSource
from tests.tools import mock_source, MockFileHandler

CURRENT_DIR = os.path.abspath(".")


@pytest.fixture
def file_name():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as fp:
        json.dump({"name": 1}, fp)
        file_name = fp.name
    yield file_name
    os.remove(file_name)


def test_url_with_source():
    s = mock_source({"name": 1})
    assert s.get("name") == 1


def test_url():
    s = UrlSource("mock:", opener=build_opener(MockFileHandler({"name": 1})))
    assert s.get("name") == 1


def test_filename_with_load_source(file_name):
    s = load_source(default_urls=file_name)
    assert s.get("name") == 1


def test_filename_only(file_name):
    s = UrlSource(file_name)
    assert s.get("name") == 1


@pytest.mark.skipif(sys.platform.startswith("win"), reason="requires unix systems")
@pytest.mark.parametrize(
    "path, expected_url",
    [
        (r"/Users/johndoe/config.yaml", "file:///Users/johndoe/config.yaml"),
        (r"config.yaml", f"file://{CURRENT_DIR}/config.yaml"),
        (r"file:///Users/johndoe/config.yaml", "file:///Users/johndoe/config.yaml"),
        (r"path/with/colon:", f"file://{CURRENT_DIR}/path/with/colon:"),
        (r"path:/starts/with/colon", "path:/starts/with/colon"),  # won't be converted
    ],
)
def test_path_to_url(path, expected_url):
    assert UrlSource._path_to_url(path) == expected_url


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="requires windows")
@pytest.mark.parametrize(
    "path, expected_url",
    [
        (r"C:\Users\johndoe\config.yaml", "file:///C:/Users/johndoe/config.yaml"),
        (r"\\Mounted\Home\config.yaml", "file:////Mounted/Home/config.yaml"),
        (r"file:////Mounted/Home/config.yaml", "file:////Mounted/Home/config.yaml"),
    ],
)
def test_path_to_url_for_win(path, expected_url):
    assert UrlSource._path_to_url(path) == expected_url
