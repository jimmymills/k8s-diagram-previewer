import sys

from diagrams import Diagram
from yaml import load
from pathlib import Path

from kinds import KIND_MAPPING

class K8sDiagram:
  def __init__(self, folder_path):
    self.nodes = []
    self.folder_path = folder_path

  def process_file(self, path):
    with open(path) as file:
      data = load(file)
    kind = data['kind']
    return KIND_MAPPING[kind](data, self)

  def run(self):
    with Diagram("Kubernetes", show=False, direction="TB"):
      paths = Path(self.folder_path).glob('**/*.yaml')
      for path in paths:
        self.nodes.append(self.process_file(path))
      for node in self.nodes:
        node.link(self)

K8sDiagram(sys.argv[1]).run()