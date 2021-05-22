import sys

from diagrams import Diagram, Node
from yaml import load, load_all
from pathlib import Path
import argparse

from kinds import map_kind, module_names

class K8sDiagram:
  def __init__(self, folder_path):
    self.nodes = []
    self.folder_path = folder_path
    self.spacer = '    '

  def process_file(self, path):
    with open(path) as file:
      content = file.read()
      if '---' in content:
        resources = load_all(content)
      else:
        resources = [load(content)]
      
      for resource in resources:
        self.process_resource(resource)

  def process_resource(self, data):
    if not data or 'kind' not in data:
      return
    
    kind = map_kind(data['kind'])
    if not kind:
      return

    if issubclass(kind, Node):
      self.file.write(f"{kind.__name__}({data['metadata']['name']})")
    else:
      self.nodes.append(kind(data, self))

  def run(self, show=False):
    with open('create_diagram.py', 'w') as file:
      self.file = file
      for name in module_names:
        self.file.write(f'from {name} import *\n')
      self.file.write(f'with Diagram("Kubernetes", show={show}, direction="TB"):\n')
      paths = Path(self.folder_path).glob('*.yaml')
      for path in paths:
        self.process_file(path)
      for node in self.nodes:
        node.link(self)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create preview diagram of K8s YAML')
  parser.add_argument(
    'folder_path', 
    metavar='Folder Path', 
    type=str, 
    nargs=1, 
    help='Path to a folder containing K8s YAML Files'
  )
  parser.add_argument(
    '--show', 
    dest='show',
    action='store_true',
    help='Show the diagram when finished'
  )
  args = parser.parse_args()
  print(args.folder_path)
  K8sDiagram(args.folder_path[0]).run(show=args.show)