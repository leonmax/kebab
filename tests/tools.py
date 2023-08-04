import json
import time
from dataclasses import dataclass
from io import StringIO
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl

from pydantic import BaseModel

from kebab import config, Field, load_source


@config(auto_repr=True)
class SubKebabConfig:
    level = Field("level", required=True, expected_type=int)
    renamed = Field("title", required=True, expected_type=str, masked=True)


@config(auto_repr=True)
class KebabConfig:
    age = Field("age", required=True, expected_type=int)
    name = Field("name", required=True, expected_type=str, masked=True)
    prof = Field("prof", required=True, expected_type=SubKebabConfig)
    nested = Field("prof", required=True, expected_type=SubKebabConfig)
    extra: dict = Field("extra", required=False, expected_type=dict)
    scores: list = Field("scores", required=False, expected_type=list)
    logging: dict = Field("logging", required=False, expected_type=dict)


@dataclass
class SubDataConfig:
    level: int
    title: str


@dataclass
class DataConfig:
    age: int
    name: str
    prof: SubDataConfig
    extra: dict
    scores: list
    logging: dict


class SubPydanticConfig(BaseModel):
    level: int
    title: str


class PydanticConfig(BaseModel):
    age: int
    name: str
    prof: SubPydanticConfig
    extra: dict
    scores: list
    logging: dict


def timed_open(opener, url, i):
    start = time.time()
    result = opener.open(url).read()
    end = time.time()
    print(f"{i}: {end - start} secs to open {url}")

    assert len(result)


def mock_opener(dictionary, only_once=False):
    return build_opener(MockFileHandler(dictionary, only_once=only_once))


def mock_source(dictionary, only_once=False, reload_interval_in_secs=0.001):
    return load_source(
        default_urls="mock:",
        opener=mock_opener(dictionary, only_once=only_once),
        reload_interval_in_secs=reload_interval_in_secs,
    )


class MockFileHandler(BaseHandler):
    def __init__(self, dictionary=None, only_once=False):
        self._dictionary = dictionary or {}
        self._only_once = only_once
        self.loaded = False

    # noinspection PyMethodMayBeStatic
    def mock_open(self, req):
        if self._only_once and self.loaded:
            raise Exception("Already loaded")
        self.loaded = True
        _content = json.dumps(self._dictionary)
        return addinfourl(StringIO(_content), [], req.get_full_url())
