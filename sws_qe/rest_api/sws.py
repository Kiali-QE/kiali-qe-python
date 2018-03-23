from collections import namedtuple
from rest_client import RestAPIClient

Namespace = namedtuple('Namespace', ['name'])
Service = namedtuple('Service', ['namespace', 'name'])
Action = namedtuple('Action', ['handler', 'instances'])
Rule = namedtuple('Rule', ['namespace', 'name', 'match', 'actions'])
Resource = namedtuple('Resource', ['namespace', 'data'])


class SWSAPI(object):
    def __init__(self, url, entry="api"):
        """ The class for SWS services
        Args:
            url: the url of SWS
            entry: entry point of a service url
        """
        self.url = url
        self._api = RestAPIClient(url=url,  entry=entry)

    def status(self):
        """ Returns status of a service """
        return self._get(path='status')

    def _get(self, path, params=None):
        """ runs GET request and returns response as JSON """
        return self._api.get_json(path, params=params)

    def list_namespaces(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = self._get('namespaces')
        if entities_j:
            for entity_j in entities_j:
                entities.append(Namespace(entity_j['name']))
        return entities

    def list_services(self, namespace=None):
        """Returns list of services.

        Args:
            namespace: Namespace of the resource
        """
        resources = self.list_resources(resource_name='services', namespace=namespace)
        services_list = []
        if resources:
            for resource in resources:
                services_list.append(Service(resource.namespace, resource.data['name']))
        return services_list

    def list_rules(self, namespace=None):
        """Returns list of rules.

        Args:
            namespace: Namespace of the resource
        """
        resources = self.list_resources(resource_name='rules', namespace=namespace)
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

    def list_resources(self, resource_name, namespace=None):
        """Returns list of resources.

          Args:
            namespace: Namespace of the resource
            resource_name: Name of the resource
        """
        if not namespace:
            resources = []
            for namespace in self.list_namespaces():
                resources.extend(self._list_resources(namespace=namespace.name,
                                                      resource_name=resource_name))
            return resources
        else:
            return self._list_resources(namespace=namespace, resource_name=resource_name)

    def _list_resources(self, resource_name, namespace):
        """Returns list of resources.

         Args:
            namespace: Namespace of the resource
            resource_name: Name of the resource
        """
        if not namespace:
            raise KeyError("'namespace' is a mandatory field!")
        if not resource_name:
            raise KeyError("'resource_name' is a mandatory field!")
        resources_list = []
        entities_j = self._get('namespaces/{}/{}'.format(namespace, resource_name))
        if entities_j:
            for entity_j in entities_j[resource_name]:
                resources_list.append(Resource(entities_j['namespace']['name'], entity_j))
        return resources_list
