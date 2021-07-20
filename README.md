# K8s Diagram Previewer

This project exists to help developers take some of the guesswork
out of deploying Kubernetes definitions by providing a preview of
what will actually be deployed with a set of YAML definitions.

## Installation

Run `pip install k8s-diagram`

You may also need to install [graphviz](https://graphviz.org/download/).

## Running

This script takes one argument, a path to a folder containing K8s 
YAML definitions and outputs a PNG diagram at kubernetes.png 
representing those definitions, as well as a python file at 
create_diagram.py if you would like to extend the diagram with 
other infrastructure surrounding your project. To automatically
open the image upon completion, add the `--show` flag.

`k8s-diagram <path_to_folder>`

To try out the example, run `k8s-diagram ./example_yaml`

For Helm Charts, simply run with the --helm flag and your chart will be
templated and placed into `/tmp/helm_preview_yaml/chart.yaml` before the script runs.

You can also pass in a context from kubeconfig with the `--cluster-context` flag to pull in all supported resources from
the target context prior to diagram generation. The resources found at the context will be copied into the target folder 
prior to chart generation. 

Run `k8s-diagram --help` to see other available options.

## Support

This tool currently supports the following Kubernetes resource types:

* Deployment
* Service
* Ingress
* Pod
* CronJob
* Job
* DaemonSet
* StatefulSet
* ConfigMap
* Secret
* PersistentVolumeClaim

There is partial support for all node types listed at https://diagrams.mingrammer.com/docs/nodes/k8s but links will not be formed.