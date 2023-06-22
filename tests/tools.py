import json
import time
from dataclasses import dataclass
from io import StringIO
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl

from kebab import config, Field


@config(auto_repr=True)
class SubKebabConfig:
    sub_field_one = Field("key_four", required=True, expected_type=int)
    sub_field_two = Field("key_five", required=True, expected_type=str, masked=True)


@config(auto_repr=True)
class KebabConfig:
    field_one = Field("key_one", required=True, expected_type=int)
    field_two = Field("key_two", required=True, expected_type=str, masked=True)
    field_three = Field("key_three", required=True, expected_type=SubKebabConfig)


@dataclass
class SubDataConfig:
    key_four: int
    key_five: str


@dataclass
class DataConfig:
    key_one: int
    key_two: str
    key_three: SubDataConfig


def timed_open(opener, url, i):
    start = time.time()
    result = opener.open(url).read()
    end = time.time()
    print(f"{i}: {end - start} secs to open {url}")

    assert len(result)


def mock_opener(dictionary):
    return build_opener(MockHandler(dictionary))


class MockHandler(BaseHandler):
    def __init__(self, dictionary=None):
        self._dictionary = dictionary or {}

    # noinspection PyMethodMayBeStatic
    def mock_open(self, req):
        _content = json.dumps(self._dictionary)
        return addinfourl(StringIO(_content), [], req.get_full_url())
