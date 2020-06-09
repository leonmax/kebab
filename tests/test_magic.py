import pytest

from kebab.magic import KebabConfigMeta, Field
from kebab import kebab_config
from kebab import literal


class CustomConfig(metaclass=KebabConfigMeta):
    groundtruth = Field('groundtruth', expected_type=int)
    input_bucket_name = Field("hello")
    output_bucket_name = Field("nonexist", default_value=1)
    nonexist2 = Field("nonexist2")
    nested_key = Field("level1.level2")


@kebab_config
class CustomConfig2:
    groundtruth = Field('groundtruth', expected_type=int)
    input_bucket_name = Field("hello")
    output_bucket_name = Field("nonexist", default_value=1)
    nonexist2 = Field("nonexist2")
    nested_key = Field("level1.level2")


@pytest.fixture
def conf(request):
    source = literal(
        groundtruth='20',
        hello="world",
        level1={
            "level2": 100
        }
    )
    return request.param(source=source)


@pytest.mark.parametrize(
    'conf',
    (CustomConfig, CustomConfig2),
    indirect=True
)
def test_kebab_config(conf):
    assert conf.groundtruth == 20
    assert conf.input_bucket_name == 'world'
    assert conf.output_bucket_name == 1
    assert conf.nonexist2 is None
    assert conf.nested_key == 100
