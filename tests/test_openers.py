import os
import sys

import pytest

from kebab.openers import DEFAULT_OPENER


@pytest.fixture
def opener():
    return DEFAULT_OPENER


def test_python_path(opener):
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    result = opener.open("pythonpath:data/conf1.yaml").read()
    assert result.strip() == "string_field: better value"
