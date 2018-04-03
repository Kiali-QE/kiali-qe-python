from collections import namedtuple
from oc_cli import OCCliClient

Namespace = namedtuple('Namespace', ['name'])
Service = namedtuple('Service', ['namespace', 'name', 'replicas', 'available_replicas'])
Resource = namedtuple('Resource', ['metadata', 'spec', 'status'])


class KialiCli(object):
    def __init__(self, url, username, password):
        """ The class for Kiali services in CLI
        Args:
            url: String with the URL of the Openshift (e.g. 'https://hostname:8443')
            username: OC username
            password: OC password
        """
        self._cli = OCCliClient(url=url, username=username, password=password)
        self._cli.login()

    def _get(self, command):
        """ runs OC command and returns response as JSON """
        return self._cli.get_json(command="oc get {}".format(command))

    def list_services(self):
        """Returns list of services.

        Args:
            namespace: Namespace of the resource
        """
        resources = self.list_resources(resource_type='services')
        services_list = []
        if resources:
            for resource in resources:
                deployment = self.get_resource(resource.metadata['name'],
                                               'deployments',
                                               resource.metadata['namespace'])
                services_list.append(Service(resource.metadata['namespace'],
                                             resource.metadata['name'],
                                             deployment.metadata['replicas'],
                                             deployment.metadata['available_replicas']))
        return services_list

    def list_namespaces(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = self._get('namespaces')
        if entities_j:
            for entity_j in entities_j['items']:
                entities.append(Namespace(entity_j['metadata']['name']))
        return entities

    def list_resources(self, resource_type, namespace=None):
        """Returns list of resources.

         Args:
            resource_type: Type of the resource
            namespace: Namespace of the resource, optional
        """
        if not resource_type:
            raise KeyError("'resource_type' is a mandatory field!")
        if namespace:
            namespace = " --namespace {} ".format(namespace)
        else:
            namespace = ""
        resources_list = []
        entities_j = self._get('{} {}'.format(resource_type, namespace))
        if entities_j:
            for entity_j in entities_j['items']:
                resources_list.append(Resource(entity_j['metadata'],
                                               entity_j['spec'],
                                               entity_j['status']))
        return resources_list

    def get_resource(self, resource_name, resource_type, namespace=None):
        """Returns details of resources.

         Args:
            resource_name: Name of the resource
            resource_type: Type of the resource
            namespace: Namespace of the resource, optional
        """
        if not resource_name:
            raise KeyError("'resource_name' is a mandatory field!")
        if not resource_type:
            raise KeyError("'resource_type' is a mandatory field!")
        if namespace:
            namespace = " --namespace {} ".format(namespace)
        else:
            namespace = ""
        entity_j = self._get('{} {} {}'.format(resource_type, resource_name, namespace))
        if entity_j:
            return Resource(metadata=entity_j['metadata'],
                            spec=entity_j['spec'],
                            status=entity_j['status'])
        return None
