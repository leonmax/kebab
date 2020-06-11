#!/usr/bin/env bash

# this will create/apply the changes in the demo.yaml to configmap kebab under default namespace
kubectl create cm kebab --from-file=./demo.yaml --dry-run=client -o yaml | kubectl apply -f -

# show the content of it (should be identical to the original ./demo.yaml)
kubectl get -ndefault cm/kebab -o json | jq -r '.data."demo.yaml"'