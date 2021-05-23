import os
import io
import inspect

from diagrams import Node
from yaml import load, load_all, FullLoader
from pathlib import Path
import argparse

from kinds import map_kind, module_names

class K8sDiagram:
  def __init__(self, folder_path, nw_only=False):
    self.nodes = []
    self.folder_path = folder_path
    self.spacer = '    '
    self.nw_only = nw_only

  def write(self, string):
    self.file.write(string)

  def write_ln(self, string, include_space=True):
    self.write(f'{self.spacer if include_space else ""}{string}\n')

  def process_file(self, path):
    with open(path) as file:
      content = file.read()
      if '---' in content:
        resources = load_all(content, Loader=FullLoader)
      else:
        resources = [load(content, Loader=FullLoader)]
      
      for resource in resources:
        self.process_resource(resource)

  def process_resource(self, data):
    if not data or 'kind' not in data:
      return

    if data['kind'] == 'List':
      for item in data['items']:
        self.process_resource(item)
    
    kind = map_kind(data['kind'])
    if not kind or not inspect.isclass(kind):
      return

    if issubclass(kind, Node):
      self.write_ln(f"{kind.__name__}('{data['metadata']['name']}')")
    else:
      self.nodes.append(kind(data, self))

  def lookup_var_name(self, kinds, name):
    for node in self.nodes:
      if node.data['kind'] in kinds and node.name == name:
        return node.var_name

  def run(self, show, image_format, save_py):
    with io.StringIO() as file:
      self.file = file
      for name in module_names:
        self.write_ln(f'from {name} import *', include_space=False)
      self.write_ln(f'with Diagram("Kubernetes", show={show}, direction="TB", outformat="{image_format}"):', include_space=False)
      paths = Path(self.folder_path).glob('*.yaml')
      for path in paths:
        self.process_file(path)
      for node in self.nodes:
        node.link(self)
      file.seek(0)
      if save_py:
        with open('create_diagram.py', 'w') as f:
          f.write(file.read())
        if show:
          os.popen('python3 create_diagram.py')
      else:
        exec(file.read())
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create preview diagram of K8s YAML')
  parser.add_argument(
    'folder_path', 
    metavar='Folder Path', 
    type=str, 
    nargs=1, 
    help='Path to the target definitions'
  )
  parser.add_argument(
    '-s',
    '--show', 
    dest='show',
    action='store_true',
    help='Show the diagram when finished'
  )
  parser.add_argument(
    '-f',
    '--image-format',
    dest='format',
    choices=['png', 'jpg', 'pdf', 'svg'],
    default='png',
    help='Output diagram as png, jpg, svg or pdf.'
  )
  parser.add_argument(
    '-p',
    '--diagram-py',
    dest='save_py',
    action='store_true',
    help='Save a python script at create_diagram.py that can be edited to add more to the diagram.'
  )
  parser.add_argument(
    '-n',
    '--networking-only',
    action='store_true',
    help='Only draw diagram edges to display networking, ignore storage links, etc.'
  )
  parser.add_argument(
    '--helm',
    action='store_true',
    help='Indicates that the path given is a helm chart that needs to be templated.'
  )
  parser.add_argument(
    '--helm-args',
    nargs=1,
    help='String of arguments to use with helm template. Ex: "--set ingress.enabled=true"'
  )
  parser.add_argument(
    '--cluster-context',
    help='Indicates a cluster to pull current definitions from. YAML of the current state will be stored at the target path.'
  )
  args = parser.parse_args()
  if args.helm:
    TMP_PATH = '/tmp/helm_preview_yaml'
    os.popen(f'mkdir -p {TMP_PATH} && helm template {args.helm_args[0] if args.helm_args else ""} {args.folder_path[0]} > {TMP_PATH}/chart.yaml').read()
    args.folder_path[0] = TMP_PATH
  elif args.cluster_context:
    os.popen(f'''
      mkdir -p {args.folder_path[0]}
      for kind in "deploy svc ing cm secret pvc job cronjob ds sts"; do
        kubectl --context={args.cluster_context} get $kind -o yaml > ${{kind}}.yaml
      done
    ''')
  K8sDiagram(args.folder_path[0], nw_only=args.networking_only).run(args.show, args.format, args.save_py)
