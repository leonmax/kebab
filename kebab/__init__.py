import threading

from kebab.sources import (
    DictSource,
    EnvVarSource,
    KebabSource,
    UnionSource,
    UrlSource,
    StrSource,
    literal,
    union,
    load_source,
)
from kebab.magic import config, Field


# region default_source function for convenience.
_LOCK = threading.Lock()
_CONF = None


def default_source():
    """
    This function return default source if not present, otherwise
    :return: the default source cached by this module
    """
    global _CONF
    with _LOCK:
        if _CONF is None:
            _CONF = load_source()
    return _CONF


# endregion


__all__ = [
    "DictSource",
    "EnvVarSource",
    "KebabSource",
    "UnionSource",
    "UrlSource",
    "StrSource",
    "Field",
    "config",
    "literal",
    "union",
    "load_source",
    "default_source",
]
