import json
import logging
import os
import tempfile
import time

import pytest

from kebab.sources import load_source, literal


@pytest.fixture
def file_name():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as fp:
        json.dump({"dynamic": 1}, fp)
        file_name = fp.name
    yield file_name
    os.remove(file_name)


def test_reload(file_name):
    s = load_source(default_urls=file_name, reload_interval_in_secs=.02)
    assert s.get("dynamic") == 1

    with open(file_name, "w+") as fp:
        json.dump({"dynamic": 2}, fp)
    time.sleep(.025)
    assert s.get("dynamic") == 2


def test_reload_extension(file_name):
    s = literal(
        __reload__={"reload_interval_in_secs": .02},
        __import__=[file_name]
    )
    assert s.get("dynamic") == 1

    with open(file_name, "w+") as fp:
        json.dump({"dynamic": 2}, fp)
    time.sleep(.025)
    assert s.get("dynamic") == 2
