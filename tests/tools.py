import json
import time
from io import StringIO
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl


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
