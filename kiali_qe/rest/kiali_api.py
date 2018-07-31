import json
from kiali.api import KialiClient

from kiali_qe.components.enums import IstioConfigObjectType as OBJECT_TYPE
from kiali_qe.components.enums import IstioConfigPageFilter as FILTER_TYPE
from kiali_qe.entities.istio_config import IstioConfig, IstioConfigDetails, Rule
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

    def service_list(self, namespaces=[], service_names=[]):
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
            _data = super(KialiExtendedClient, self).service_list(namespace=_namespace)
            _services = _data['services']
            # update all the services to our custom entity
            for _service_rest in _services:
                if 'health' in _service_rest:
                    # update health status
                    _health = Health.get_from_rest(_service_rest['health'])
                else:
                    _health = None
                _service = Service(
                    namespace=_namespace,
                    name=_service_rest['name'],
                    istio_sidecar=_service_rest['istioSidecar'],
                    health=_health)
                items.append(_service)
        # filter by service name
        if len(service_names) > 0:
            filtered_list = []
            for _name in service_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def istio_config_list(self, filters=[]):
        """Returns list of istio config.
        Args:
            namespaces: can be zero or any number of namespaces
        """
        items = []
        namespace_list = []
        # filters
        namespaces = []
        istio_names = []
        istio_types = []
        for _filter in filters:
            if FILTER_TYPE.NAMESPACE.text in _filter['name']:
                namespaces.append(_filter['value'])
            elif FILTER_TYPE.ISTIO_NAME.text in _filter['name']:
                istio_names.append(_filter['value'])
            elif FILTER_TYPE.ISTIO_TYPE.text in _filter['name']:
                istio_types.append(_filter['value'])
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            _data = super(KialiExtendedClient, self).istio_config_list(namespace=_namespace)

            # update DestinationRule
            if len(_data['destinationRules']) > 0:
                for _policy in _data['destinationRules']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.DESTINATION_RULE.text))

            # update Rule
            if len(_data['rules']) > 0:
                for _policy in _data['rules']:
                    items.append(Rule(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.RULE.text))

            # update VirtualService
            if len(_data['virtualServices']) > 0:
                for _policy in _data['virtualServices']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.VIRTUAL_SERVICE.text))

            # update QuotaSpec
            if len(_data['quotaSpecs']) > 0:
                for _policy in _data['quotaSpecs']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.QUOTA_SPEC.text))

            # update QuotaSpecBindings
            if len(_data['quotaSpecBindings']) > 0:
                for _policy in _data['quotaSpecBindings']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.QUOTA_SPEC_BINDING.text))

            # update Gateway
            if len(_data['gateways']) > 0:
                for _policy in _data['gateways']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.GATEWAY.text))

            # update serviceEntries
            if len(_data['serviceEntries']) > 0:
                for _policy in _data['serviceEntries']:
                    items.append(IstioConfig(
                        name=_policy['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.SERVICE_ENTRY.text))

            # not required at this stage. These options not availabe in UI
            # # update all the rules to our custom entity
            # for _rule_rest in _rules:
            #     # update actions
            #     _actions = []
            #     for _action_r in _rule_rest['actions']:
            #         _actions.append(Action.get_from_rest(_action_r))
            #     _match = None
            #     if 'match' in _rule_rest:
            #         _match = _rule_rest['match']
            #     _rule = Rule(
            #         namespace=_namespace,
            #         name=_rule_rest['name'],
            #         actions=_actions,
            #         match=_match)
            #     items.append(_rule)

        # apply filters
        if len(istio_names) > 0 or len(istio_types) > 0:
            name_filtered_list = []
            type_filtered_list = []
            for _name in istio_names:
                name_filtered_list.extend([_i for _i in items if _name in _i.name])
            for _type in istio_types:
                type_filtered_list.extend([_i for _i in items if _type in _i.object_type])
            # If both filters were set, then results must be intersected,
            # as UI applies AND in filters
            if len(istio_names) > 0 and len(istio_types) > 0:
                return set(name_filtered_list).intersection(set(type_filtered_list))
            elif len(istio_names) > 0:
                return set(name_filtered_list)
            elif len(istio_types) > 0:
                return set(type_filtered_list)
        return items

    def istio_config_details(self, namespace, object_type, object_name):
        """Returns details of istio config.
        Args:
            namespaces: namespace where istio config is located
            object_type: type of istio config
            object_name: name of istio config
        """

        _data = super(KialiExtendedClient, self).istio_config_details(
            namespace=namespace,
            object_type=object_type,
            object_name=object_name)
        config = None
        config_data = None
        if _data:
            # get DestinationRule
            if _data['destinationRule']:
                config_data = _data['destinationRule']

            # get Rule
            if _data['rule']:
                config_data = _data['rule']

            # get VirtualService
            if _data['virtualService']:
                config_data = _data['virtualService']

            # get QuotaSpec
            if _data['quotaSpec']:
                config_data = _data['quotaSpec']

            # get QuotaSpecBindings
            if _data['quotaSpecBinding']:
                config_data = _data['quotaSpecBinding']

            # get Gateway
            if _data['gateway']:
                config_data = _data['gateway']

            # get serviceEntry
            if _data['serviceEntry']:
                config_data = _data['serviceEntry']

            if config_data:
                config = IstioConfigDetails(name=config_data['name'],
                                            type=_data['objectType'],
                                            text=json.dumps(config_data))
        return config
