import os
import sys
from io import BufferedIOBase
from urllib.error import URLError
from urllib.request import (
    build_opener,
    BaseHandler,
    FileHandler,
    HTTPHandler,
    HTTPSHandler,
)
from urllib.response import addinfourl


class _FileLikeKey(BufferedIOBase):
    def __init__(self, key):
        self.read = key.read


class PythonPathHandler(BaseHandler):
    """
    a filename with relative path to the pythonpath
    """

    def __init__(self):
        pass

    def pythonpath_open(self, req):
        pathname = req.get_full_url()[len(req.type + ":") :].lstrip("/")
        full_path = self._find(pathname)

        return addinfourl(open(full_path, "r"), [], req.get_full_url())

    @staticmethod
    def _find(pathname):
        for dirname in sys.path:
            full_path = os.path.join(dirname, pathname)
            if os.path.isfile(full_path):
                return full_path
        raise URLError("Can't find file %s on $PYTHONPATH" % pathname)


handlers = [
    FileHandler,
    HTTPHandler,
    HTTPSHandler,
    PythonPathHandler,
]

try:
    # noinspection PyUnresolvedReferences
    from . import k8s

    handlers.append(k8s.K8SHandler)
except ImportError:
    pass

try:
    # noinspection PyUnresolvedReferences
    from . import aws

    handlers.append(aws.S3Handler)
    handlers.append(aws.SecretsManagerHandler)
except ImportError:
    pass

try:
    # noinspection PyUnresolvedReferences
    from . import ali

    handlers.append(ali.OSSHandler)
except ImportError:
    pass

DEFAULT_OPENER = build_opener(*handlers)
