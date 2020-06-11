import os
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import build_opener

import pytest

from tests.tools import timed_open

try:
    # noinspection PyUnresolvedReferences
    from kubernetes import client, config
    # noinspection PyUnresolvedReferences
    from kebab.k8s import K8SHandler
except ImportError:
    pytest.skip("Failed to import kubernetes and K8SHandler, will skip k8s test",
                allow_module_level=True)


@pytest.fixture
def opener():
    return build_opener(K8SHandler)


@pytest.fixture
def secret_url():
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    api = client.CoreV1Api()
    namespace = "default"
    for secret in api.list_namespaced_secret(namespace).items:
        secret_name = secret.metadata.name
        if secret_name.startswith("default-token-"):
            return f"k8s://secret/{namespace}/{secret_name}"


def test_k8s_secret(opener, secret_url):
    result = opener.open(secret_url).read()
    assert "token" in result


def test_k8s_secret_with_key(opener, secret_url):
    result = opener.open(secret_url).read()
    assert len(result)


def test_k8s_configmap(opener):
    url = "k8s://configmap/kube-public/cluster-info/"

    result = opener.open(url).read()
    assert "kubeconfig" in result


def test_k8s_configmap_with_key(opener):
    url = "k8s://configmap/kube-public/cluster-info/kubeconfig"

    result = opener.open(url).read()
    assert "apiVersion" in result


@pytest.mark.skip
def test_k8s_opener_with_load(opener):
    url = "k8s://configmap/kube-public/cluster-info/kubeconfig"

    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(2):
            executor.submit(timed_open, opener, url, i)
