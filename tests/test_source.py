import logging
from dataclasses import dataclass

import pytest
from mock import patch

from kebab import literal, config, Field, UrlSource


@pytest.fixture
def source():
    return literal(
        key1="123",
        key2=2,
        key3=[3.0, 4.0, 5.0],
        key4={"nested": 1, "more": {"layer": "is better"}},
    )


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


@config(auto_repr=True)
class SubConfig:
    sub_field_one = Field("key_four", required=True, expected_type=int)
    sub_field_two = Field("key_five", required=True, expected_type=str, masked=True)


@config(auto_repr=True)
class DemoConfig:
    field_one = Field("key_one", required=True, expected_type=int)
    field_two = Field("key_two", required=True, expected_type=str, masked=True)
    field_three = Field("key_three", required=True, expected_type=SubConfig)


@pytest.fixture
def source2():
    return literal(
        key_one="123",
        key_two="today",
        key_three={"key_four": 5.0, "key_five": "inside"},
    )


def test_get_config_class(source2):
    demo_config = source2.get(expected_type=DemoConfig)
    assert demo_config.field_two == "today"
    assert demo_config.field_three.sub_field_two == "inside"


def test_cast(source2):
    demo_config = source2.cast(".", DemoConfig)
    assert demo_config.field_two == "today"
    assert demo_config.field_three.sub_field_two == "inside"


def test_url_source():
    """
    string_field imported in conf1.yaml overwritten the key in conf2.json
    """
    source = UrlSource("tests/data/conf2.json")
    assert source.get("string_field") == "better value"
    assert source.get("int_field") == 100
    assert source.get("int_field", expected_type=str) == "100"


@dataclass
class SubDataClassConfig:
    key_four: int
    key_five: str


@dataclass
class DataClassConfig:
    key_one: int
    key_two: str
    key_three: SubDataClassConfig


def test_get_dataclass(source2):
    print(source2.get())
    demo_config = source2.get(expected_type=DataClassConfig)
    assert demo_config.key_two == "today"
    assert demo_config.key_three.key_five == "inside"
