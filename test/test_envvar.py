import os

from kebab.sources import load_source


def test_env_var_source():
    os.environ["XDG_CONFIG_HOME"] = "/home/kebab/.config"
    os.environ["XDG_DATA_HOME"] = "/home/kebab/.local/share"

    s = load_source(default_urls=(), fallback_dict={
        "__env_map__": {
            "XDG_CONFIG_HOME": "xdg.config_home",
            "XDG_DATA_HOME": "xdg.data_home"
        },
        "hello": "world"
    })

    assert os.environ["XDG_CONFIG_HOME"] == s.get("xdg.config_home")
    assert s.get("xdg.cache_home") is None
    assert "world" == s.get("hello")

