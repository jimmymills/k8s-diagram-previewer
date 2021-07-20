# K8s Diagram Previewer

This project exists to help developers take some of the guesswork
out of deploying Kubernetes definitions by providing a preview of
what will actually be deployed with a set of YAML definitions.

## Installation

Clone the repo and run `pip install k8s-diagram`

  You may also need to install [graphviz](https://graphviz.org/download/).

## Running

This script takes one argument, a path to a folder containing K8s 
YAML definitions and outputs a PNG diagram at kubernetes.png 
representing those definitions, as well as a python file at 
create_diagram.py if you would like to extend the diagram with 
other infrastructure surrounding your project. To automatically
open the image upon completion, add the `--show` flag.

`python app.py <path_to_folder>`

To try out the example, run `python3 diagram.py ./example_yaml`

For Helm Charts, simply run with the --helm flag and your chart will be
templated and placed into `/tmp/helm_preview_yaml/chart.yaml` before the script runs.

You can also pass in a context from kubeconfig with the `--cluster-context` flag to pull in all supported resources from
the target context prior to diagram generation.

Run `python diagram.py -h` to see other available options.

```
usage: diagram.py [-h] [-s] [-f {png,jpg,pdf,svg}] [-p] [-n] [--helm] [--helm-args HELM_ARGS] Folder Path

Create preview diagram of K8s YAML

positional arguments:
  Folder Path           Path to the target definitions

optional arguments:
  -h, --help            show this help message and exit
  -s, --show            Show the diagram when finished
  -f {png,jpg,pdf,svg}, --image-format {png,jpg,pdf,svg}
                        Output diagram as png, jpg, svg or pdf.
  -p, --diagram-py      Save a python script at create_diagram.py that can be edited to add more to the diagram.
  -n, --networking-only
                        Only draw diagram edges to display networking, ignore storage links, etc.
  --helm                Indicates that the path given is a helm chart that needs to be templated.
  --helm-args HELM_ARGS
                        String of arguments to use with helm template. Ex: "--set ingress.enabled=true"
```

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