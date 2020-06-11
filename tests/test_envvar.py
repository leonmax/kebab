import os

import pytest

from kebab.sources import load_source, literal


@pytest.fixture
def env_var_map():
    # setup environment variables
    os.environ["XDG_CONFIG_HOME"] = "/home/kebab/.config"
    os.environ["XDG_DATA_HOME"] = "/home/kebab/.local/share"

    yield {
        "XDG_CONFIG_HOME": "xdg.config_home",
        "XDG_DATA_HOME": "xdg.data_home"
    }

    # remove it when done
    del os.environ["XDG_CONFIG_HOME"]
    del os.environ["XDG_DATA_HOME"]


def test_env_var_extension(env_var_map):
    s = literal(
        hello="world",
        __env_map__=env_var_map
    )

    assert os.environ["XDG_CONFIG_HOME"] == s.get("xdg.config_home")
    assert s.get("xdg.cache_home") is None
    assert "world" == s.get("hello")


def test_env_var_map_in_load_source(env_var_map):
    s = load_source(
        default_urls=(),
        fallback_dict={"hello": "world"},
        env_var_map=env_var_map
    )

    assert os.environ["XDG_CONFIG_HOME"] == s.get("xdg.config_home")
    assert s.get("xdg.cache_home") is None
    assert "world" == s.get("hello")
