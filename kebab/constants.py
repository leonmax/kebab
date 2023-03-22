import os
from pathlib import Path

DEFAULT_URL_ENVVAR = "CONF_URL"
DISABLE_RELOAD = -1
# 以下目录 `~/.config` 遵从 XDG Base Directory Specification
# 参考: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
XDG_CONFIG_HOME = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config').expanduser()


def find_config(app_name: str = 'app', filename: str = None):
    if not filename:
        filename = app_name
    default_config_paths = [
        Path.cwd() / filename,                  # ./config.ini
        XDG_CONFIG_HOME / app_name / filename,  # ~/.config/kebab/config.ini
        Path('/etc') / app_name / filename      # /etc/kebab/config.ini
    ]

    for default in default_config_paths:
        if default.exists():
            return default

    return None
