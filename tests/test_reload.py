from dataclasses import dataclass
import time

from kebab.openers import DEFAULT_OPENER
from kebab.sources import load_source, literal
from tests.tools import mock_opener, MockHandler


@dataclass
class DynamicConfig:
    dynamic: int


def test_reload_dataclass():
    context = {"nested": {"dynamic": 3}}
    source = load_source(
        default_urls="mock://",
        opener=mock_opener(context),
        reload_interval_in_secs=0.001,
    ).subsource("nested")
    dconf = source.get(expected_type=DynamicConfig, update_after_reload=True)
    val = source.get("dynamic", expected_type=int, update_after_reload=True)
    assert dconf.dynamic == 3
    assert val == 3

    context["nested"]["dynamic"] = 2
    time.sleep(0.015)
    assert source.get("dynamic") == 2
    assert dconf.dynamic == 2
    # primitive types are not updated
    assert val == 3


def test_reload():
    context = {"dynamic": 1}
    s = load_source(
        default_urls="mock://",
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
    s = literal(__reload__={"reload_interval_in_secs": 0.01}, __import__=["mock://"])
    assert s.get("dynamic") == 1

    context["dynamic"] = 2
    time.sleep(0.015)
    assert s.get("dynamic") == 2
