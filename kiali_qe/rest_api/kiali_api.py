from collections import namedtuple
from kiali import KialiClient

Namespace = namedtuple('Namespace', ['name'])
Service = namedtuple('Service', ['namespace', 'name'])
Action = namedtuple('Action', ['handler', 'instances'])
Rule = namedtuple('Rule', ['namespace', 'name', 'match', 'actions'])
Resource = namedtuple('Resource', ['namespace', 'data'])


class KialiAPI(object):
    def __init__(self, host, username, password):
        """ The class for Kiali services
        Args:
            host: the hostname of Kiali
            username: the username of Kiali
            password: the password of Kiali
        """
        self._client = KialiClient(host=host, username=username, password=password)

    def list_namespaces(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = self._client.namespace_list()
        if entities_j:
            for entity_j in entities_j:
                entities.append(Namespace(entity_j['name']))
        return entities

    def list_services(self, namespace=None):
        """Returns list of services.

        Args:
            namespace: Namespace of the resource
        """
        resources = []
        if not namespace:
            for namespace in self.list_namespaces():
                resources.extend(self._list_resources(self._client.services_list(namespace=namespace.name),
                                                      resource_name='services'))
        else:
            resources.extend(self._list_resources(self._client.services_list(namespace=namespace),
                                                  resource_name='services'))
        services_list = []
        if resources:
            for resource in resources:
                services_list.append(Service(resource.namespace,
                                             resource.data['name']))
        return services_list

    def list_rules(self, namespace=None):
        """Returns list of rules.

        Args:
            namespace: Namespace of the resource
        """
        resources = []
        if not namespace:
            for namespace in self.list_namespaces():
                resources.extend(self._list_resources(self._client.istio_config_list(namespace=namespace.name),
                                                      resource_name='rules'))
        else:
            resources.extend(self._list_resources(self._client.istio_config_list(namespace=namespace),
                                                  resource_name='rules'))
        rules_list = []
        if resources:
            for resource in resources:
                match = resource.data['match']
                actions = []
                for action in resource.data['actions']:
                    handler = action['handler']
                    instances = []
                    for instance in action['instances']:
                        instances.append(instance)
                    actions.append(Action(handler, instances))
                rules_list.append(Rule(resource.namespace, resource.data['name'], match, actions))
        return rules_list

    def _list_resources(self, entities_j, resource_name):
        """Returns list of resources.

         Args:
            resource_name: Name of the resource
        """
        if not resource_name:
            raise KeyError("'resource_name' is a mandatory field!")
        resources_list = []
        if entities_j:
            for entity_j in entities_j[resource_name]:
                resources_list.append(Resource(entities_j['namespace']['name'], entity_j))
        return resources_list
