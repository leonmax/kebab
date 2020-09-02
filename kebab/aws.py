import json
import re

# noinspection PyCompatibility
from builtins import str
from io import StringIO
from urllib.error import URLError
from urllib.parse import parse_qsl
from urllib.request import BaseHandler, urlopen
from urllib.response import addinfourl

import boto3
from botocore.exceptions import ClientError, BotoCoreError, UnknownServiceError

from kebab.exceptions import KebabException
from kebab.openers import _FileLikeKey


class S3Handler(BaseHandler):
    def __init__(self):
        self.s3 = boto3.resource("s3")

    def s3_open(self, req):
        try:
            selector = req.selector
        except AttributeError:
            selector = req.get_selector()
        key_name = selector.lstrip("/")
        bucket_name = req.host

        if key_name is None:
            raise URLError(f"No such resource: {req.get_full_url()}")
        if not bucket_name or not key_name:
            raise URLError("URL must be in the format s3://<bucket>/<key>")

        obj = self.s3.Object(bucket_name, key_name)

        try:
            headers = [
                ("Content-type", obj.content_type),
                ("Content-length", obj.content_length),
                ("Etag", obj.e_tag),
                ("Last-modified", obj.last_modified),
            ]
        except (BotoCoreError, ClientError) as e:
            raise URLError(str(e))

        return addinfourl(_FileLikeKey(obj.get()["Body"]), headers, req.get_full_url())


class SecretsManagerHandler(BaseHandler):
    def __init__(self):
        session = boto3.Session()
        self.default_region_name = session.region_name
        if not self.default_region_name:
            try:
                resp = urlopen(
                    "http://169.254.169.254/latest/dynamic/instance-identity/document",
                    timeout=0.1,
                )
                self.default_region_name = json.loads(resp.read())["region"]
            except URLError:
                # no default region_name available
                pass

        self.pattern = re.compile(
            r"awssecret://(?P<secret_name>[.\w/-]+)(\?(?P<query_string>.*))?"
        )

    def awssecret_open(self, req):
        m = self.pattern.match(req.get_full_url())
        if not m:
            raise URLError(f"URL {req.get_full_url()} is not parsable")
        secret_name = m.group("secret_name")
        query_string = m.group("query_string")

        query_dict = dict(parse_qsl(query_string or ""))
        query_dict["region_name"] = self.default_region_name

        response = self._get_secret_value(secret_name, **query_dict)
        if "SecretString" in response:
            secret_value = response["SecretString"]
        else:
            raise KebabException(
                "Currently only string secret is supported for secrets manager"
            )

        return addinfourl(StringIO(secret_value), [], req.get_full_url())

    def _get_secret_value(self, secret_name, **kwargs):
        try:
            client = boto3.client(
                service_name="secretsmanager",
                region_name=kwargs.get("Region", self.default_region_name),
            )
        except UnknownServiceError:
            raise URLError(
                "awssecret url is not supported, secretsmanager service requires "
                "boto3>=1.7.84 "
            )

        try:
            if "VersionId" in kwargs:
                return client.get_secret_value(
                    SecretId=secret_name, VersionId=kwargs.get("VersionId")
                )
            elif "VersionStage" in kwargs:
                return client.get_secret_value(
                    SecretId=secret_name,
                    VersionStage=kwargs.get("VersionStage"),
                )
            else:
                return client.get_secret_value(SecretId=secret_name)
        except (BotoCoreError, ClientError) as e:
            raise URLError(str(e))
