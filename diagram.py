import os
import io

from diagrams import Node
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

  def run(self, show, image_format, save_py):
    with io.StringIO() as file:
      self.file = file
      for name in module_names:
        self.file.write(f'from {name} import *\n')
      self.file.write(f'with Diagram("Kubernetes", show={show}, direction="TB", outformat="{image_format}"):\n')
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
    help='Path to a folder containing K8s YAML Files'
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
  args = parser.parse_args()
  K8sDiagram(args.folder_path[0]).run(args.show, args.format, args.save_py)