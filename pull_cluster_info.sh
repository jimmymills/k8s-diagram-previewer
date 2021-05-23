#!/bin/bash

mkdir -p $1
kinds="deploy svc ing cm secret pvc job cronjob ds sts"
for kind in $kinds; do
  kubectl --context=$2 get $kind -o yaml > ${kind}.yaml
done