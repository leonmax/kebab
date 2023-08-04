import logging
import sys

import pytest
from mock import patch

from kebab import UrlSource
from .tools import KebabConfig, DataConfig


def test_subsource(source):
    source = source.subsource("key4")
    assert source.get("nested", expected_type=str) == "1"
    assert source.get("nested", expected_type=int) == 1
    assert source.get("nested", expected_type=bool)
    assert source.get("more", expected_type=dict) == {"layer": "is better"}


def test_dict_like(source):
    d = source

    assert d["key1"] == "123"
    assert d["key3"] == [3.0, 4.0, 5.0]
    assert d["key4.nested"] == 1
    assert d["key4"]["nested"] == 1
    assert d["key4.more.layer"] == "is better"
    assert len(d) == 4

    for k, v in d.items():
        assert k.startswith("key")
        assert v is not None


@patch("logging.Logger.debug")
def test_masked(logger_mock, source):
    logging.getLogger("kebab.sources").setLevel("DEBUG")
    assert source.get("key1", masked=True) == "123"
    logger_mock.assert_called_with("read config: key1 = ***")


def test_get_config_class(complex_source):
    demo_config = complex_source.get(expected_type=KebabConfig)
    assert demo_config.name == "today"
    assert demo_config.prof.renamed == "inside"


def test_cast(complex_source):
    demo_config = complex_source.cast(".", KebabConfig)
    assert demo_config.name == "today"
    assert demo_config.prof.renamed == "inside"


def test_url_source():
    """
    string_field imported in conf1.yaml overwritten the key in conf2.json
    """
    source = UrlSource("tests/data/conf2.json")
    assert source.get("string_field") == "better value"
    assert source.get("int_field") == 100
    assert source.get("int_field", expected_type=str) == "100"


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="requires windows")
def test_url_source_for_win():
    """
    string_field imported in conf1.yaml overwritten the key in conf2.json
    """
    assert (
        UrlSource._path_to_url(r"C:\Users\johndoe\config.yaml")
        == "file:///C:/Users/johndoe/config.yaml"
    )

    assert (
        UrlSource._path_to_url(r"\\Mounted\Home\config.yaml")
        == "file:////Mounted/Home/config.yaml"
    )


def test_get_dataclass(complex_source):
    demo_config = complex_source.get(expected_type=DataConfig)
    assert demo_config.name == "today"
    assert demo_config.prof.title == "inside"
