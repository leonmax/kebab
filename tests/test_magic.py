import pytest

from kebab.magic import KebabConfigMeta, Field
from kebab import kebab_config
from kebab import literal


class CustomConfig(metaclass=KebabConfigMeta):
    required_key = Field("simple", required=True)
    auto_cast_key = Field('auto_cast', expected_type=int)
    nonexist_with_default = Field("nonexist", default_value=1)
    nonexist_no_default = Field("nonexist2")
    nested_key = Field("layer1.layer2")


@kebab_config
class CustomConfig2:
    required_key = Field("simple", required=True)
    auto_cast_key = Field('auto_cast', expected_type=int)
    nonexist_with_default = Field("nonexist", default_value=1)
    nonexist_no_default = Field("nonexist2")
    nested_key = Field("layer1.layer2")


@pytest.fixture
def source():
    return literal(
        simple='a great news',
        auto_cast='20',
        layer1={
            "layer2": 100
        }
    )


def _assert_conf(conf):
    assert conf.required_key == 'a great news'
    assert conf.auto_cast_key == 20
    # non exist with default value
    assert conf.nonexist_with_default == 1
    # non exist without default
    assert conf.nonexist_no_default is None
    assert conf.nested_key == 100


# noinspection PyArgumentList
def test_meta_class(source):
    _assert_conf(CustomConfig(source))


def test_kebab_config(source):
    _assert_conf(CustomConfig2(source))


def test_cast(source):
    _assert_conf(source.cast(".", CustomConfig2))
