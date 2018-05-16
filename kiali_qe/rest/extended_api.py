from kiali.api import KialiClient

from kiali_qe.entities.rule import Action, Rule
from kiali_qe.entities.service import Health, Service


class KialiExtendedClient(KialiClient):

    def namespace_list(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = super(KialiExtendedClient, self).namespace_list()
        if entities_j:
            for entity_j in entities_j:
                entities.append(entity_j['name'])
        return entities

    def service_list(self, *namespaces):
        """Returns list of services.
        Args:
            namespaces: can be zero or any number of namespaces
        """
        items = []
        namespace_list = []
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            _data = super(KialiExtendedClient, self).services_list(namespace=_namespace)
            _services = _data['services']
            # update all the services to our custom entity
            for _service_rest in _services:
                # update health status
                _health = Health.get_from_rest(_service_rest['health'])
                _service = Service(
                    namespace=_namespace,
                    name=_service_rest['name'],
                    istio_sidecar=_service_rest['istio_sidecar'],
                    health=_health)
                items.append(_service)
        return items

    def rule_list(self, *namespaces):
        """Returns list of rules.
        Args:
            namespaces: can be zero or any number of namespaces
        """
        items = []
        namespace_list = []
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            _data = super(KialiExtendedClient, self).rules_list(namespace=_namespace)
            _rules = _data['rules']
            # update all the rules to our custom entity
            for _rule_rest in _rules:
                # update actions
                _actions = []
                for _action_r in _rule_rest['actions']:
                    _actions.append(Action.get_from_rest(_action_r))
                _match = None
                if 'match' in _rule_rest:
                    _match = _rule_rest['match']
                _rule = Rule(
                    namespace=_namespace,
                    name=_rule_rest['name'],
                    actions=_actions,
                    match=_match)
                items.append(_rule)
        return items
