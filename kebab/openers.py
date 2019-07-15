import json
import os
import re
import sys
from io import BufferedIOBase, StringIO

import boto3
import pkg_resources
# noinspection PyCompatibility
from builtins import str
from botocore.exceptions import ClientError, BotoCoreError, UnknownServiceError
from urllib.error import URLError
from urllib.parse import parse_qsl
from urllib.request import (
    build_opener, urlopen, BaseHandler, FileHandler, HTTPHandler, HTTPSHandler
)
from urllib.response import addinfourl

from kebab.exceptions import KebabException


class _FileLikeKey(BufferedIOBase):
    def __init__(self, key):
        self.read = key.read


class S3Handler(BaseHandler):
    def __init__(self):
        self.s3 = boto3.resource('s3')

    def s3_open(self, req):
        try:
            selector = req.selector
        except AttributeError:
            selector = req.get_selector()
        key_name = selector.lstrip('/')
        bucket_name = req.host

        if key_name is None:
            raise URLError('no such resource: {}'.format(req.get_full_url()))
        if not bucket_name or not key_name:
            raise URLError('url must be in the format s3://<bucket>/<key>')

        obj = self.s3.Object(bucket_name, key_name)

        try:
            headers = [
                ('Content-type', obj.content_type),
                ('Content-length', obj.content_length),
                ('Etag', obj.e_tag),
                ('Last-modified', obj.last_modified),
            ]
        except (BotoCoreError, ClientError) as e:
            raise URLError(str(e))

        return addinfourl(_FileLikeKey(obj.get()['Body']), headers, req.get_full_url())


class ResourceHandler(BaseHandler):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def resource_open(self, req):
        try:
            selector = req.selector
        except AttributeError:
            selector = req.get_selector()
        resource_name = selector.lstrip('/')
        pkg_name = req.host

        stream = pkg_resources.resource_stream(pkg_name, resource_name)

        return addinfourl(_FileLikeKey(stream), [], req.get_full_url())


class PythonPathHandler(BaseHandler):
    """
    a filename with relative path to the pythonpath
    """
    def __init__(self):
        pass

    def pythonpath_open(self, req):
        pathname = req.get_full_url()[len(req.type + ':'):].lstrip('/')
        full_path = self._find(pathname)

        return addinfourl(open(full_path, 'r'), [], req.get_full_url())

    @staticmethod
    def _find(pathname):
        for dirname in sys.path:
            full_path = os.path.join(dirname, pathname)
            if os.path.isfile(full_path):
                return full_path
        raise URLError("Can't find file %s on $PYTHONPATH" % pathname)


class SecretsManagerHandler(BaseHandler):
    def __init__(self):
        session = boto3.Session()
        self.default_region_name = session.region_name
        if not self.default_region_name:
            try:
                resp = urlopen('http://169.254.169.254/latest/dynamic/instance-identity/document', timeout=0.1)
                self.default_region_name = json.loads(resp.read())['region']
            except URLError:
                # no default region_name available
                pass

        self.pattern = re.compile('awssecret://(?P<secret_name>[.\w/-]+)(\?(?P<query_string>.*))?')

    def awssecret_open(self, req):
        m = self.pattern.match(req.get_full_url())
        if not m:
            raise URLError('url {} is not parsable'.format(req.get_full_url()))
        secret_name = m.group('secret_name')
        query_string = m.group('query_string')

        query_dict = dict(parse_qsl(query_string or ''))
        query_dict['region_name'] = self.default_region_name

        response = self._get_secret_value(secret_name, **query_dict)
        if 'SecretString' in response:
            secret_value = response['SecretString']
        else:
            raise KebabException('Currently only string secret is supported for secrets manager')

        return addinfourl(StringIO(secret_value), [], req.get_full_url())

    def _get_secret_value(self, secret_name, **kwargs):
        try:
            client = boto3.client(
                service_name='secretsmanager',
                region_name=kwargs.get('Region', self.default_region_name)
            )
        except UnknownServiceError:
            raise URLError('awssecret url is not supported, secretsmanager service requires boto3>=1.7.84')

        try:
            if 'VersionId' in kwargs:
                return client.get_secret_value(SecretId=secret_name, VersionId=kwargs.get('VersionId'))
            elif 'VersionStage' in kwargs:
                return client.get_secret_value(SecretId=secret_name, VersionStage=kwargs.get('VersionStage'))
            else:
                return client.get_secret_value(SecretId=secret_name)
        except (BotoCoreError, ClientError) as e:
            raise URLError(str(e))


DEFAULT_OPENER = build_opener(
    FileHandler, HTTPHandler, HTTPSHandler, PythonPathHandler,
    ResourceHandler, S3Handler, SecretsManagerHandler
)
