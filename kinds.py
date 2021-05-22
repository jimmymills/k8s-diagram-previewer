import importlib

from diagrams.k8s.compute import Pod, Cronjob
from diagrams.k8s.network import SVC, Ing

module_names = [
  'diagrams',
  'diagrams.k8s.compute', 
  'diagrams.k8s.network', 
  'diagrams.k8s.clusterconfig',
  'diagrams.k8s.group',
  'diagrams.k8s.others',
  'diagrams.k8s.podconfig',
  'diagrams.k8s.rbac',
  'diagrams.k8s.storage'
]

modules = [importlib.import_module(m) for m in module_names]

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

class K8sNode:
  def __init__(self, data, context):
    self.data = data
    self.name = data['metadata']['name']
    self.var_name = f"{data['kind'].lower()}_{self.name.replace('-', '_')}"
    self.labels = data['metadata'].get('labels')

  def link(self, context):
    pass

class Deployment(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    containers = data['spec']['template']['spec']['containers']
    self.ports = [port for container in containers for port in container['ports']]
    self.labels = data['spec']['template']['metadata'].get('labels')
    context.file.write(f'''
    with Cluster(f'Deployment: {self.name}'):
      with Cluster(f'ReplicaSet: {self.name}'):
        {self.var_name} = {str([f"Pod('{self.name}-{i}')" for i in range(data['spec']['replicas'])]).replace('"', '')}
''')


class K8sPod(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    context.file.write(f"{context.spacer}{self.var_name} = Pod('{self.name}')\n")


class DaemonSet(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.labels = data['spec']['template']['metadata'].get('labels')
    context.file.write(f'''
    with Cluster(f'DaemonSet: {self.name}'):
      {self.var_name} = Pod('{self.name}')
    ''')


class StatefulSet(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.labels = data['spec']['template']['metadata'].get('labels')
    context.file.write(f'''
    with Cluster(f'StatefulSet: {self.name}'):
      {self.var_name} = {str([f"Pod('{self.name}-{i}')" for i in range(data['spec']['replicas'])]).replace('"', '')}
''')


class Service(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    context.file.write(f"{context.spacer}{self.var_name} = SVC('{self.name}')")
    self.ports = data['spec']['ports']

  def link(self, context):
    selector = self.data['spec']['selector']
    for node in context.nodes:
      if not node.labels or node.data['kind'] not in ('Pod', 'Deployment', 'DaemonSet', 'StatefulSet'):
        continue
      for k in selector.keys():
        if node.labels.get(k) != selector[k]:
          break
      else:
        context.file.write(f"{context.spacer}{self.var_name} >> {node.var_name}\n")


class Ingress(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    context.file.write(f"{context.spacer}{self.var_name} = Ing('{self.name}')\n")

  def link(self, context):
    rules = self.data['spec']['rules']
    paths = [path for rule in rules for path in rule['http']['paths']]
    for path in paths:
      svc = path['backend'].get('serviceName') or path['backend']['service']['name']
      port = path['backend'].get('servicePort') or path['backend']['service']['port']['number']
      for node in context.nodes:
        if node.data['kind'] == 'Service' and node.name == svc:
          context.file.write(f"{context.spacer}{self.var_name} >> Edge(label='{path['path']} -> {port}') >> {node.var_name}\n")



KIND_MAPPING = {
  'Deployment': Deployment,
  'Service': Service,
  'Ingress': Ingress,
  'Pod': K8sPod,
  'CronJob': Cronjob,
  'DaemonSet': DaemonSet,
  'StatefulSet': StatefulSet
}