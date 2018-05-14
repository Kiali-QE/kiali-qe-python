from kiali.api import KialiClient
from collections import namedtuple


Namespace = namedtuple('Namespace', ['name'])
Service = namedtuple('Service', ['namespace', 'name'])
Action = namedtuple('Action', ['handler', 'instances'])
Rule = namedtuple('Rule', ['namespace', 'name', 'match', 'actions'])
Resource = namedtuple('Resource', ['namespace', 'data'])


class KialiExtendedClient(KialiClient):

    def namespace_list(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = super(KialiExtendedClient, self).namespace_list()
        if entities_j:
            for entity_j in entities_j:
                entities.append(Namespace(entity_j['name']))
        return entities

    def service_list(self, namespace=None):
        """Returns list of services.
        Args:
            namespace: Namespace of the resource
        """
        resources = []
        if not namespace:
            for namespace in self.namespace_list():
                resources.extend(self._list_resources(
                    super(KialiExtendedClient, self).services_list(
                        namespace=namespace.name), resource_name='services'))
        else:
            resources.extend(self._list_resources(
                super(KialiExtendedClient, self).services_list(
                    namespace=namespace), resource_name='services'))
        services_list = []
        if resources:
            for resource in resources:
                services_list.append(Service(resource.namespace, resource.data['name']))
        return services_list

    def rule_list(self, namespace=None):
        """Returns list of rules.
        Args:
            namespace: Namespace of the resource
        """
        resources = []
        if not namespace:
            for namespace in self.namespace_list():
                resources.extend(
                    self._list_resources(super(KialiExtendedClient, self).rules_list(
                        namespace=namespace.name), resource_name='rules'))
        else:
            resources.extend(
                self._list_resources(super(KialiExtendedClient, self).rules_list(
                    namespace=namespace), resource_name='rules'))
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
