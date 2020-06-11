import sys
import time
from contextlib import contextmanager


@contextmanager
def interval(secs=-1):
    try:
        yield
        if secs > 0:
            time.sleep(secs)
        else:
            sys.exit(0)
    except KeyboardInterrupt:
        raise
