import importlib

from diagrams.k8s.compute import Cronjob

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

def map_kind(kind):
  if kind in KIND_MAPPING:
    return KIND_MAPPING[kind]
  else:
    for module in modules:
      try:
        return getattr(module, kind)
      except AttributeError:
        pass


def query_dict(data, query):
  keys = query.split('.')
  results = []
  for i, key in enumerate(keys):
    if not key:
      continue
    if key in data:
      if isinstance(data[key], list):
        for result in data[key]:
          results += query_dict(result, '.'.join(keys[i+1:]))
      else:
        data = data[key]
    else:
      break
  else:
    if results:
      return results
    if isinstance(data, list):
      results += data 
    else:
      results.append(data)

  return results

class K8sNode:
  def __init__(self, data, context):
    self.data = data
    self.name = data['metadata']['name']
    self.var_name = f"{data['kind'].lower()}_{self.name.replace('-', '_')}"
    self.labels = data['metadata'].get('labels')

  def link_helper(self, context, type, queries):
    links = set()
    for query in queries:
      link_names = query_dict(self.pod_data, query)
      for name in link_names:
        links.add(context.lookup_var_name([type], name))
    return links

  def link(self, context):
    pass

class Workload(K8sNode):
  def link(self, context):
    if context.nw_only:
      return

    links = set()
    links.update(self.link_helper(context, 'ConfigMap', [
      'spec.containers.env.valueFrom.configMapKeyRef.name',
      'spec.volumes.configMap.name'
    ]))
    links.update(self.link_helper(context, 'Secret', [
      'spec.containers.env.valueFrom.secretKeyRef.name',
      'spec.volumes.secret.secretName'
    ]))
    links.update(self.link_helper(context, 'PersistentVolumeClaim', [
      'spec.volumes.persistentVolumeClaim.claimName'
    ]))

    for link in links:
      if link:
        context.write_ln(f"{self.var_name} >> {link}")


class Deployment(Workload):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.pod_data = data['spec']['template']
    self.ports = query_dict(self.pod_data, 'spec.containers.ports')
    self.labels = self.pod_data['metadata'].get('labels')
    context.write(f'''
    with Cluster('Deployment: {self.name}'):
      with Cluster('ReplicaSet: {self.name}'):
        {self.var_name} = {str([f"Pod('{self.name}-{i}')" for i in range(data['spec']['replicas'])]).replace('"', '')}
''')


class K8sPod(Workload):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.pod_data = self.data
    context.write_ln(f"{self.var_name} = Pod('{self.name}')")


class DaemonSet(Workload):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.pod_data = data['spec']['template']
    self.labels = self.pod_data['metadata'].get('labels')
    context.write(f'''
    with Cluster(f'DaemonSet: {self.name}'):
      {self.var_name} = Pod('{self.name}')
''')


class StatefulSet(Workload):
  def __init__(self, data, context):
    super().__init__(data, context)
    self.pod_data = data['spec']['template']
    self.labels = self.pod_data['metadata'].get('labels')
    context.file.write(f'''
    with Cluster(f'StatefulSet: {self.name}'):
      {self.var_name} = {str([f"Pod('{self.name}-{i}')" for i in range(data['spec']['replicas'])]).replace('"', '')}
''')


class Service(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    context.write_ln(f"{self.var_name} = SVC('{self.name}')")
    self.ports = data['spec']['ports']

  def link(self, context):
    try:
      selector = self.data['spec']['selector']
    except KeyError:
      return
    for node in context.nodes:
      if not node.labels or node.data['kind'] not in ('Pod', 'Deployment', 'DaemonSet', 'StatefulSet'):
        continue
      for k in selector.keys():
        if node.labels.get(k) != selector[k]:
          break
      else:
        context.write_ln(f"{self.var_name} >> {node.var_name}")


class Ingress(K8sNode):
  def __init__(self, data, context):
    super().__init__(data, context)
    context.write_ln(f"{self.var_name} = Ing('{self.name}')")

  def link(self, context):
    paths = query_dict(self.data, 'spec.rules.http.paths')
    links = {}
    for path in paths:
      svc = path['backend'].get('serviceName') or path['backend']['service']['name']
      port = path['backend'].get('servicePort') or path['backend']['service']['port']['number']
      svc_var_name = context.lookup_var_name(['Service'], svc)
      if not svc_var_name:
        continue
      elif svc_var_name not in links:
        links[svc_var_name] = {'paths': set()}
      
      links[svc_var_name]['paths'].add(f"{path['path']} -> {port}") 

    
    for k, v in links.items():
      path_label = '\n'.join(v['paths'])
      context.write_ln(f"{self.var_name} >> Edge(label='''{path_label}''') >> {k}")


class ConfigMap(K8sNode):
  def __init__(self, data, context):
      super().__init__(data, context)
      context.write_ln(f"{self.var_name} = CM('{self.name}')")


class Secret(K8sNode):
  def __init__(self, data, context):
      super().__init__(data, context)
      context.write_ln(f"{self.var_name} = Secret('{self.name}')")


class PersistentVolumeClaim(K8sNode):
  def __init__(self, data, context):
      super().__init__(data, context)
      context.write_ln(f"{self.var_name} = PVC('{self.name}')")


KIND_MAPPING = {
  'Deployment': Deployment,
  'Service': Service,
  'Ingress': Ingress,
  'Pod': K8sPod,
  'CronJob': Cronjob,
  'DaemonSet': DaemonSet,
  'StatefulSet': StatefulSet,
  'ConfigMap': ConfigMap,
  'Secret': Secret,
  'PersistentVolumeClaim': PersistentVolumeClaim,
}