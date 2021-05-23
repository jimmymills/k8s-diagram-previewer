# K8s Diagram Previewer

This project exists to help developers take some of the guesswork
out of deploying Kubernetes definitions by providing a preview of
what will actually be deployed with a set of YAML definitions.

## Installation

Clone the repo and run `pip install -r requirements.txt`

  You will also need to install [graphviz](https://graphviz.org/download/).

## Running

This script takes one argument, a path to a folder containing K8s 
YAML definitions and outputs a PNG diagram at kubernetes.png 
representing those definitions, as well as a python file at 
create_diagram.py if you would like to extend the diagram with 
other infrastructure surrounding your project. To automatically
open the image upon completion, add the `--show` flag.

`python diagram.py <path_to_folder>`

To try out the example, run `python3 diagram.py ./example_yaml`

For Helm Charts, simply run with the --helm flag and your chart will be
templated and placed into `/tmp/helm_preview_yaml/chart.yaml` before the script runs.

Run `python diagram.py -h` to see other available options.

```
usage: diagram.py [-h] [-s] [-f {png,jpg,pdf,svg}] [-p] [-n] Folder Path

Create preview diagram of K8s YAML

positional arguments:
  Folder Path           Path to a folder containing K8s YAML Files

optional arguments:
  -h, --help            show this help message and exit
  -s, --show            Show the diagram when finished
  -f {png,jpg,pdf,svg}, --image-format {png,jpg,pdf,svg}
                        Output diagram as png, jpg, svg or pdf.
  -p, --diagram-py      Save a python script at create_diagram.py that can be edited to add more to the diagram.
  -n, --networking-only
                        Only draw diagram edges to display networking, ignore storage links, etc.
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