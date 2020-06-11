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
def conf(request):
    source = literal(
        simple='a great news',
        auto_cast='20',
        layer1={
            "layer2": 100
        }
    )
    return request.param(source=source)


@pytest.mark.parametrize(
    'conf',
    (CustomConfig, CustomConfig2),
    indirect=True
)
def test_kebab_config(conf):
    assert conf.required_key == 'a great news'
    assert conf.auto_cast_key == 20
    # non exist with default value
    assert conf.nonexist_with_default == 1
    # non exist without default
    assert conf.nonexist_no_default is None
    assert conf.nested_key == 100
