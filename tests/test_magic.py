import pytest

from kebab import literal, config
from kebab.magic import KebabConfigMeta, Field


@config
class NestedConfig:
    field_name_same_as_key_name = Field(required=True)


# noinspection DuplicatedCode
class CustomConfig(metaclass=KebabConfigMeta):
    required_key = Field("simple", required=True)
    auto_cast_key = Field("auto_cast", expected_type=int)
    nonexist_with_default_value = Field("nonexist", default_value=1)
    nonexist_with_default = Field("nonexist1", default=1)
    nonexist_no_default = Field("nonexist2")
    nested_key = Field("layer1.layer2")
    nested_config = Field(expected_type=NestedConfig)


# noinspection DuplicatedCode
@config
class CustomConfig2:
    required_key = Field("simple", required=True)
    auto_cast_key = Field("auto_cast", expected_type=int)
    nonexist_with_default_value = Field("nonexist", default_value=1)
    nonexist_with_default = Field("nonexist1", default=1)
    nonexist_no_default = Field("nonexist2")
    nested_key = Field("layer1.layer2")
    nested_config = Field(expected_type=NestedConfig)


@pytest.fixture
def source():
    return literal(
        simple="a great news",
        auto_cast="20",
        layer1={"layer2": 100},
        nested_config={"field_name_same_as_key_name": "we need nesting"},
    )


def _assert_conf(conf):
    assert conf.required_key == "a great news"
    assert conf.auto_cast_key == 20
    # non exist with default value
    assert conf.nonexist_with_default_value == 1
    assert conf.nonexist_with_default == 1
    # non exist without default
    assert conf.nonexist_no_default is None
    assert conf.nested_key == 100

    assert conf.nested_config.field_name_same_as_key_name == "we need nesting"


# noinspection PyArgumentList
def test_meta_class(source):
    _assert_conf(CustomConfig(source))


def test_kebab_config(source):
    _assert_conf(CustomConfig2(source))


def test_cast(source):
    _assert_conf(source.get(expected_type=CustomConfig2))


@config(auto_repr=True)
class CustomConfig3:
    nested_config = Field(expected_type=CustomConfig)


@pytest.fixture
def source3(source):
    return literal(nested_config=source.get())


def test_nested_cast(source3):
    config3 = source3.get(expected_type=CustomConfig3)
    assert hasattr(config3, "nested_config")
    _assert_conf(config3.nested_config)
