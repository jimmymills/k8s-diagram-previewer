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

For Helm Charts, run `helm template <path_to_chart> > <file_name>` and drop the file into a folder to run the script against.

Run `python diagram.py -h` to see other available options.

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

There is partial support for all node types listed at https://diagrams.mingrammer.com/docs/nodes/k8s but links will not be formed.