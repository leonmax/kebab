import time


def timed_open(opener, url, i):
    start = time.time()
    result = opener.open(url).read()
    end = time.time()
    print(f"{i}: {end - start} secs to open {url}")

    assert len(result)
