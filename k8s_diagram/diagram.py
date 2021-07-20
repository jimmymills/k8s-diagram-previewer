import os
import io
import inspect

from diagrams import Node
from yaml import load, load_all, FullLoader
from pathlib import Path
import argparse

from .kinds import map_kind, module_names

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
    