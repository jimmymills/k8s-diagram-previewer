#!/usr/bin/env bash

mkdir -p $1
kinds="deploy svc ing cm secret pvc job cronjob ds sts"
for kind in $kinds; do
  kubectl --context=$2 get $kind -o yaml > "${1}/${kind}.yaml"
done