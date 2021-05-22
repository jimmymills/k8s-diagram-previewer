import sys

from diagrams import Diagram, Node
from yaml import load
from pathlib import Path

from kinds import map_kind

class K8sDiagram:
  def __init__(self, folder_path):
    self.nodes = []
    self.folder_path = folder_path

  def process_file(self, path):
    with open(path) as file:
      data = load(file)
    kind = map_kind(data['kind'])
    if issubclass(kind, Node):
      kind(data['metadata']['name'])
    else:
      self.nodes.append(kind(data, self))

  def run(self):
    with Diagram("Kubernetes", show=False, direction="TB"):
      paths = Path(self.folder_path).glob('**/*.yaml')
      for path in paths:
        self.process_file(path)
      for node in self.nodes:
        node.link(self)

K8sDiagram(sys.argv[1]).run()