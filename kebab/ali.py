import threading
from urllib.error import URLError
from urllib.request import BaseHandler

import oss2
from alibabacloud import ClientConfig
from alibabacloud.credentials.provider import DefaultChainedCredentialsProvider

DEFAULT_OSS_ENDPOINT = "https://oss-cn-hangzhou.aliyuncs.com"


class OSSHandler(BaseHandler):
    def __init__(
        self,
        credential_provider=None,
        client_config=None,
        resolve_endpoint=True,
        prefer_internal_point=False,
    ):
        self._client_config = client_config or ClientConfig()
        self._cred_provider = credential_provider or DefaultChainedCredentialsProvider(
            client_config=client_config
        )
        self._auth = self._get_auth()
        self._resolve_endpoint = resolve_endpoint
        self._prefer_internal_point = prefer_internal_point
        self._bucket_info_cache_lock = threading.RLock()
        self._bucket_info_cache = {}

        if not self._client_config.endpoint:
            self._client_config.endpoint = DEFAULT_OSS_ENDPOINT

    def _get_auth(self):
        cred = self._cred_provider.provide()
        return oss2.Auth(cred.access_key_id, cred.access_key_secret)

    def _resolve_bucket_endpoint(self, bucket_name):
        if not self._resolve_endpoint:
            return self._client_config.endpoint

        # lookup endpoint in bucket_info, choose the endpoint and normalize
        with self._bucket_info_cache_lock:
            if bucket_name not in self._bucket_info_cache:
                bucket = oss2.Bucket(
                    self._auth, self._client_config.endpoint, bucket_name
                )
                bucket_info = bucket.get_bucket_info()
                self._bucket_info_cache[bucket_name] = bucket_info

        bucket_info = self._bucket_info_cache[bucket_name]
        return self._normalize_endpoint(
            bucket_info.internal_endpoint
            if self._prefer_internal_point
            else bucket_info.extranet_endpoint
        )

    @staticmethod
    def _normalize_endpoint(endpoint):
        """
        add https:// scheme if not present
        :param endpoint: endpoint str with or without scheme
        :return:
        """
        endpoint = endpoint.strip()
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            return "https://" + endpoint
        else:
            return endpoint

    def oss_open(self, req):
        try:
            selector = req.selector
        except AttributeError:
            selector = req.get_selector()
        key_name = selector.lstrip("/")
        bucket_name = req.host

        if key_name is None:
            raise URLError(f"No such resource: {req.get_full_url()}")
        if not bucket_name or not key_name:
            raise URLError("URL must be in the format oss://<bucket>/<key>")

        endpoint = self._resolve_bucket_endpoint(bucket_name)
        bucket = oss2.Bucket(self._auth, endpoint, bucket_name)
        return bucket.get_object(key_name)
