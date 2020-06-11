from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import build_opener

import pytest

from tests.tools import timed_open

try:
    # noinspection PyUnresolvedReferences
    from kebab.ali import OSSHandler
except ImportError:
    pytest.skip("Failed to import oss2 and OSSHandler, will skip ali test",
                allow_module_level=True)


@pytest.mark.skip
def test_ali_opener_with_load():
    opener = build_opener(OSSHandler)
    hangzhou_url = "oss://inceptio-data-collection-test/2020/05/21/23002bf9-a5ef-44be-ac0f-e69be428c434/metadata.yaml"

    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(2):
            executor.submit(timed_open, opener, hangzhou_url, i)
