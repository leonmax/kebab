# kebab
[![Lint and Test](https://github.com/leonmax/kebab/actions/workflows/build-test.yml/badge.svg)](https://github.com/leonmax/kebab/actions/workflows/build-test.yml)

Kebab is a python configuration framework

Features:
- support various sources of config such as `file`, `http`, `k8s`, `oss`, `s3`, easy to expand
- mapping to config object, supports [`pydantic`](https://docs.pydantic.dev/latest/) and built-in [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- overlay multiple config, can auto-import
- config auto-reload based on interval
- cli from easier debugging

```bash
pip install pykebab
```

## Kubernetes
This extension support `k8s://` url, include secret and configmap resource

### Installation
```shell script
pip install pykebab[k8s]
```

### Add Kubernetes handler
in your code, add the code below
```python
from kebab.openers import DEFAULT_OPENER, add_k8s_handlers
add_k8s_handlers(DEFAULT_OPENER)
```
before using the `default_source`, `load_source`, `UrlSource`


### URL Pattern
```
k8s://<namespace>/<resource_type>/<resource_name>[/<data_key>]
```
- `namespace`: if . map to default namespace
in a word, the two below is equivalent
```
k8s://default/secret/default-token-rm42d
k8s://./secret/default-token-rm42d
```
- `resource_type`: either secret or configmap/cm, cm is an alias of configmap
the two below is equivalent
```
k8s://kube-public/configmap/cluster-info/kubeconfig
k8s://kube-public/cm/cluster-info/kubeconfig
```
- `resource_name`: the name of the secret/configmap
- `data_key`: the secret or configmap have a data section
```shell script
kubectl get -n kube-public secret default-token-z9z4w -ojsonpath="{.data.namespace}"
```
gives an `base64` encoded `a3ViZS1wdWJsaWM=`, when decoded, it is `kube-public`

we promote that out of other metadata, and decode it if it is secret,
so you can reference to the value directly
```shell script
kebab k8s://kube-public/secret/default-token-z9z4w/namespace
```
call the above will give you the namespace
```
"kube-public"
```

### Caveat
Note that all the `default-token-xxxxx`, the `xxxxx` part is dynamic for every cluster.


## AWS S3 support
This extension support `s3://` url
### Installation
make sure you have wheel installed, if you are not sure, install wheel with pip
```shell script
pip install -U wheel
```
Note this is required to install the aws extra, since one of the dependency won't work directly without wheel.
To install the extra:
```shell script
pip install pykebab[aws]
```
### Add S3 handler
in your code, add the code below
```python
from kebab.openers import DEFAULT_OPENER, add_aws_handlers
add_aws_handlers(DEFAULT_OPENER)
```
before using the `default_source`, `load_source`, `UrlSource`


## Release
```
./release.sh [patch|minor|major|prepatch|preminor|premajor|prerelease]
```
