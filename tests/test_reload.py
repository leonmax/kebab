import time

from kebab.openers import DEFAULT_OPENER
from kebab.sources import load_source, literal
from tests.tools import mock_opener, MockHandler


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
