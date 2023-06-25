import time

import pytest

from kebab.openers import DEFAULT_OPENER
from kebab.sources import load_source, literal
from tests.tools import mock_opener, MockHandler, DataConfig, SubDataConfig, \
    SubKebabConfig, KebabConfig, PydanticConfig, SubPydanticConfig


@pytest.fixture
def reloading(context):
    return load_source(
        default_urls="mock:",
        opener=mock_opener(context),
        reload_interval_in_secs=0.001,
    )


@pytest.mark.parametrize('expected_type,nested_type', [
    (DataConfig, SubDataConfig),
    (KebabConfig, SubKebabConfig),
    (PydanticConfig, SubPydanticConfig)
])
def test_reload_dataclass(reloading, context, expected_type, nested_type):
    dconf = reloading.get(expected_type=expected_type, update_after_reload=True)
    prof = reloading.get('prof', expected_type=nested_type, update_after_reload=True)
    level = reloading.get("prof.level", expected_type=int, update_after_reload=True)
    assert type(level) == int

    # eval obj, nested obj, primitive type
    assert dconf.prof.level == 3
    assert prof.level == 3
    # primitive types are not updated
    assert level == 3

    # change value and wait for reload
    context["prof"]["level"] = 2
    time.sleep(0.015)
    assert reloading.get("prof.level") == 2

    # re-eval obj, nested obj, primitive type after reload
    assert dconf.prof.level == 2
    assert prof.level == 2
    # primitive types are not updated
    assert level == 3


def test_reload():
    context = {"dynamic": 1}
    s = load_source(
        default_urls="mock:",
        opener=mock_opener(context),
        reload_interval_in_secs=0.001,
    )
    assert s.get("dynamic") == 1

    context["dynamic"] = 2
    time.sleep(0.015)
    assert s.get("dynamic") == 2


def test_reload_extension():
    context = {"dynamic": 1}
    DEFAULT_OPENER.add_handler(MockHandler(context))
    s = literal(__reload__={"reload_interval_in_secs": 0.01}, __import__=["mock:"])
    assert s.get("dynamic") == 1

    context["dynamic"] = 2
    time.sleep(0.015)
    assert s.get("dynamic") == 2
