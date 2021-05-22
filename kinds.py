import importlib

from diagrams import Cluster, Edge
from diagrams.k8s.compute import Pod, Cronjob
from diagrams.k8s.network import SVC, Ing

modules = [importlib.import_module(m) for m in (
  'diagrams.k8s.compute', 
  'diagrams.k8s.network', 
  'diagrams.k8s.clusterconfig',
  'diagrams.k8s.group',
  'diagrams.k8s.others',
  'diagrams.k8s.podconfig',
  'diagrams.k8s.rbac',
  'diagrams.k8s.storage'
)]

def get_name(data):
  return data['metadata']['name']

def map_kind(kind):
  if kind in KIND_MAPPING:
    return KIND_MAPPING[kind]
  else:
    for module in modules:
      try:
        return getattr(module, kind)
      except AttributeError:
        pass

class Deployment:
  def __init__(self, data):
    self.data = data
    self.name = get_name(data)
    containers = data['spec']['template']['spec']['containers']
    self.ports = [port for container in containers for port in container['ports']]
    self.labels = data['spec']['template']['metadata'].get('labels')
    with Cluster(f'Deployment: {self.name}'):
      with Cluster(f'ReplicaSet: {self.name}'):
        self.node = [
            Pod(f'{self.name}-{i}') for i in range(data['spec']['replicas'])
        ]

  def link(self, context):
    pass


class K8sPod:
  def __init__(self, data):
    self.data = data
    self.name = get_name(data)
    self.labels = data['metadata'].get('labels')
    self.node = Pod(self.name)

  def link(self, context):
    pass


class Service:
  def __init__(self, data):
    self.data = data
    self.name = get_name(data)
    self.node = SVC(self.name)
    self.ports = data['spec']['ports']
    self.labels = data['metadata'].get('labels')

  def link(self, context):
    selector = self.data['spec']['selector']
    for node in context.nodes:
      if not node.labels or node.data['kind'] not in ('Pod', 'Deployment'):
        continue
      for k in selector.keys():
        if node.labels.get(k) != selector[k]:
          break
      else:
        port_label = ""
        # port_label is too sloppy, leaving commented until
        # a better method is found for denoting port mapping
        # for port in self.ports:
        #   port_label += f"{port['port']} -> {port['targetPort']}\n"
        self.node >> Edge(label=port_label) >> node.node


class Ingress:
  def __init__(self, data):
    self.data = data
    self.name = get_name(data)
    self.node = Ing(self.name)
    self.labels = data['metadata'].get('labels')

  def link(self, context):
    rules = self.data['spec']['rules']
    paths = [path for rule in rules for path in rule['http']['paths']]
    for path in paths:
      svc = path['backend'].get('serviceName') or path['backend']['service']['name']
      port = path['backend'].get('servicePort') or path['backend']['service']['port']['number']
      for node in context.nodes:
        if node.data['kind'] == 'Service' and node.name == svc:
          self.node >> Edge(label=f'{path["path"]} -> {port}') >> node.node



KIND_MAPPING = {
  'Deployment': Deployment,
  'Service': Service,
  'Ingress': Ingress,
  'Pod': K8sPod,
  'CronJob': Cronjob
}