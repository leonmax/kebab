import base64
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict
from urllib.request import build_opener

import pytest

from tests.tools import timed_open

try:
    # noinspection PyUnresolvedReferences
    from kubernetes import client, config  # noqa: F401

    # noinspection PyUnresolvedReferences
    from kebab.k8s import K8SHandler
except ImportError:
    pytest.skip(
        "Failed to import kubernetes and K8SHandler, will skip k8s test",
        allow_module_level=True,
    )


@pytest.fixture
def opener():
    return build_opener(K8SHandler)


@pytest.fixture
def secret_url():
    api = K8SHandler.get_api_client()
    namespace = "default"
    for secret in api.list_namespaced_secret(namespace).items:
        secret_name = secret.metadata.name

        if secret_name.startswith("default-token-"):
            yield f"k8s://{namespace}/secret/{secret_name}"
            return

    secret_name = "default-token-kebabtest"
    api.create_namespaced_secret(namespace, _create_secret(secret_name))
    yield f"k8s://{namespace}/secret/{secret_name}"
    api.delete_namespaced_secret(secret_name, namespace)


def _create_secret(secret_name):
    def _b64(content: Dict[str, str]):
        return {
            k: base64.b64encode(v.encode("utf8")).decode("utf8")
            for k, v in content.items()
        }
    body = client.V1Secret()
    body.api_version = 'v1'
    body.kind = 'Secret'
    body.type = 'Opaque'
    body.metadata = {'name': secret_name}
    body.data = _b64({
        'token': "fake_token",
        'namespace': "default"
    })
    return body


def test_k8s_secret(opener, secret_url):
    result = opener.open(secret_url).read()
    assert "token" in result


def test_k8s_secret_with_key(opener, secret_url):
    result = opener.open(f"{secret_url}/namespace").read()
    assert result.decode("utf-8") == "default"


def test_k8s_configmap(opener):
    url = "k8s://kube-public/configmap/cluster-info/"

    result = opener.open(url).read()
    assert "kubeconfig" in result


def test_k8s_configmap_with_dot(opener):
    url = "k8s://./configmap/kube-root-ca.crt/ca.crt"

    result = opener.open(url).read()
    assert "CERTIFICATE" in result


def test_k8s_configmap_with_key(opener):
    url = "k8s://kube-public/cm/cluster-info/kubeconfig"

    result = opener.open(url).read()
    assert "apiVersion" in result


@pytest.mark.skip
def test_k8s_opener_with_load(opener):
    url = "k8s://kube-public/configmap/cluster-info/kubeconfig"

    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(2):
            executor.submit(timed_open, opener, url, i)
