import logging

import pytest
from mock import patch

from kebab import literal


@pytest.fixture
def source():
    return literal(
        key1='123',
        key2=2,
        key3=[3.0, 4.0, 5.0],
        key4={
            "nested": 1,
            "more": {
                "layer": "is better"
            }
        }
    )


def test_dict_like(source):
    d = source

    assert d['key1'] == '123'
    assert d['key3'] == [3.0, 4.0, 5.0]
    assert d['key4.nested'] == 1
    assert d['key4']['nested'] == 1
    assert d['key4.more.layer'] == "is better"
    assert len(d) == 4

    for k, v in d.items():
        assert k.startswith("key")
        assert v is not None


@patch('logging.Logger.debug')
def test_masked(logger_mock, source):
    logging.getLogger("kebab.sources").setLevel("DEBUG")
    assert source.get("key1", masked=True) == "123"
    logger_mock.assert_called_with('read config: key1 = ***')
