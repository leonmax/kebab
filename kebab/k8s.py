import base64
import json
import os
import re
from io import StringIO, BytesIO
from urllib.error import URLError
from urllib.request import BaseHandler
from urllib.response import addinfourl

from kubernetes import client, config


K8S_URL_PATTERN = re.compile(
    r'k8s://%(ns)s/%(type)s/%(name)s(/%(key)s*)?' % {
        "ns":   r"(?P<ns>[\.\w-]*)",
        "type": r"(?P<type>\w+)",
        "name": r"(?P<name>[\w-]+)",
        "key":  r"(?P<key>[^\/]+)"
    }
)


class _ParsedUrl:
    def __init__(self, url):
        self.url = url
        m = K8S_URL_PATTERN.match(url)
        if not m:
            raise URLError('url {} is not parsable'.format(url))
        self.resource_type = 'configmap' if m.group('type') in 'cm' else m.group('type')
        self.resource_name = m.group('name')
        self.namespace = 'default' if m.group('ns') in ['', '.'] else m.group('ns')
        self.key = m.group('key')


class K8SHandler(BaseHandler):
    @staticmethod
    def get_api_client():
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            config.load_incluster_config()
        else:
            config.load_kube_config()

        return client.CoreV1Api()

    def __init__(self):
        self.api = self.get_api_client()

    def k8s_open(self, req):
        url = req.get_full_url()
        pu = _ParsedUrl(url)

        if pu.resource_type == 'secret':
            stream = self._read_secret(pu)
        elif pu.resource_type == 'configmap':
            stream = self._read_configmap(pu)
        else:
            raise URLError('url {} is not parsable'.format(pu.url))

        return addinfourl(stream, [], url)

    def _read_configmap(self, pu: _ParsedUrl):
        resource = self.api.read_namespaced_config_map(pu.resource_name, pu.namespace)
        if pu.key:
            content = resource.data[pu.key]
            return StringIO(content)
        else:
            return StringIO(json.dumps(resource.data))

    def _read_secret(self, pu: _ParsedUrl):
        resource = self.api.read_namespaced_secret(pu.resource_name, pu.namespace)
        if pu.key:
            content = resource.data[pu.key]
            return BytesIO(base64.b64decode(content.encode('utf8')))
        else:
            content = {
                k: base64.b64decode(v.encode('utf8')).decode('utf8')
                for k, v in resource.data.items()
            }
            return StringIO(json.dumps(content))
