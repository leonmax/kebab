# kebab

Kebab is a python configuration framework

Features:
- support various sources of config such as `file`, `http`, `k8s`, `oss`, `s3`, easy to expand
- mapping to config object
- overlay multiple config, can auto-import
- config auto-reload


## Kubernetes
This extension support `k8s://` url, include secret and configmap resource

### Installation
```shell script
pip install pykebab[k8s]
```
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


## Alicloud support
This extension support `oss://` url
### Installation
make sure you have wheel installed, if you are not sure, install wheel with pip
```shell script
pip install -U wheel
```
Note this is required to install the ali extra, since one of the dependency won't work directly without wheel.
To install the extra:
```shell script
pip install pykebab[ali]
```

## Release
```
poetry update
VERSION=`poetry version minor | rev | cut -d' ' -f 1 | rev`
git commit -m "release $VERSION"
git push
gh release create --generate-notes --latest "$VERSION"
```
