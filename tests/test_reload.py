import logging.config
import time

import pytest

from kebab.openers import DEFAULT_OPENER
from kebab.sources import literal
from tests.tools import (
    MockFileHandler,
    DataConfig,
    SubDataConfig,
    SubKebabConfig,
    KebabConfig,
    PydanticConfig,
    SubPydanticConfig,
    mock_source,
)


@pytest.fixture
def reloading(context):
    return mock_source(context)


@pytest.mark.parametrize(
    "expected_type,nested_type",
    [
        (DataConfig, SubDataConfig),
        (KebabConfig, SubKebabConfig),
        (PydanticConfig, SubPydanticConfig),
    ],
)
def test_reload_dataclass(reloading, context, expected_type, nested_type):
    dconf = reloading.get(expected_type=expected_type, update_after_reload=True)
    prof1 = dconf.prof
    prof2 = reloading.get("prof", expected_type=nested_type, update_after_reload=True)
    level = reloading.get("prof.level", expected_type=int, update_after_reload=True)
    assert isinstance(level, int)

    # eval obj, nested obj, primitive type
    assert prof1.level == 3
    assert prof2.level == 3
    # primitive types are not updated
    assert level == 3
    assert dconf.extra["height"] == 1
    logging.config.dictConfig(dconf.logging)

    # change value and wait for reload
    context["prof"]["level"] = 2
    reloading.reload()
    assert reloading.get("prof.level") == 2

    # re-eval obj, nested obj, primitive type after reload
    assert prof1.level == 2
    assert prof2.level == 2
    # primitive types are not updated
    assert level == 3


@pytest.mark.parametrize(
    "failed_to_reload, value_after_reload", [(False, "new"), (True, "old")]
)
def test_reload(failed_to_reload, value_after_reload):
    context = {"dynamic": "old"}
    s = mock_source(context, only_once=failed_to_reload)
    assert s.get("dynamic") == "old"

    # change content and reload
    context["dynamic"] = "new"
    time.sleep(0.1)  # reload will fail if only_once=True
    assert (
        s.get("dynamic") == value_after_reload
    )  # old value will be used if reload failed


def test_reload_extension():
    context = {"dynamic": 1}
    DEFAULT_OPENER.add_handler(MockFileHandler(context))
    s = literal(__reload__={"reload_interval_in_secs": 0.01}, __import__=["mock:"])
    assert s.get("dynamic") == 1

    context["dynamic"] = 2
    time.sleep(0.1)
    assert s.get("dynamic") == 2
