import os
import sys
from io import BufferedIOBase
from urllib.error import URLError
from urllib.request import (
    OpenerDirector,
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


DEFAULT_OPENER = build_opener(*handlers)


def add_k8s_handlers(opener: OpenerDirector):
    # noinspection PyUnresolvedReferences
    from . import k8s

    opener.add_handler(k8s.K8SHandler())
    return opener


def add_aws_handlers(opener: OpenerDirector):
    # noinspection PyUnresolvedReferences
    from . import aws

    opener.add_handler(aws.S3Handler())
    opener.add_handler(aws.SecretsManagerHandler())
    return opener
