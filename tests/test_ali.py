import time
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import build_opener

import pytest

ali = pytest.importorskip("kebab.ali")
from kebab.ali import OSSHandler


@pytest.mark.skip
def test_ali_opener():
    opener = build_opener(OSSHandler)
    hangzhou_url = "oss://inceptio-data-collection-test/2020/05/21/23002bf9-a5ef-44be-ac0f-e69be428c434/metadata.yaml"

    def timed_open(opener, url, i):
        start = time.time()
        result = opener.open(url).read()
        end = time.time()
        print(f"{i}: {end - start} secs to open {url}")

        assert len(result)

    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(2):
            executor.submit(timed_open, opener, hangzhou_url, i)
