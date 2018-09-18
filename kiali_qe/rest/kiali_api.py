import json

from kiali.api import KialiClient
from kiali_qe.components.enums import IstioConfigObjectType as OBJECT_TYPE
from kiali_qe.components.enums import IstioConfigPageFilter as FILTER_TYPE
from kiali_qe.entities.istio_config import IstioConfig, IstioConfigDetails, Rule
from kiali_qe.entities.service import (
    Health,
    Service,
    ServiceDetails,
    VirtualService,
    DestinationRule
)
from kiali_qe.entities.workload import (
    Workload,
    WorkloadDetails,
    WorkloadPod
)
from kiali_qe.entities.applications import (
    Application,
    ApplicationDetails,
    AppWorkload
)
from kiali_qe.utils.date import parse_from_rest, from_rest_to_ui


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

    def application_list(self, namespaces=[], application_names=[]):
        """Returns list of applications.
        Args:
            namespaces: can be zero or any number of namespaces
            application_names: can be zero or any number of applications
        """
        items = []
        namespace_list = []
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            _data = super(KialiExtendedClient, self).app_list(namespace=_namespace)
            _applications = _data['applications']
            if _applications:
                for _application_rest in _applications:
                    _application = Application(
                        namespace=_namespace,
                        name=_application_rest['name'],
                        istio_sidecar=_application_rest['istioSidecar'])
                    items.append(_application)
        # filter by application name
        if len(application_names) > 0:
            filtered_list = []
            for _name in application_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def workload_list(self, namespaces=[], workload_names=[]):
        """Returns list of workloads.
        Args:
            namespaces: can be zero or any number of namespaces
            workload_names: can be zero or any number of workloads
        """
        items = []
        namespace_list = []
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            _data = super(KialiExtendedClient, self).workload_list(namespace=_namespace)
            _workloads = _data['workloads']
            if _workloads:
                for _workload_rest in _workloads:
                    _workload = Workload(
                        namespace=_namespace,
                        name=_workload_rest['name'],
                        workload_type=_workload_rest['type'],
                        istio_sidecar=_workload_rest['istioSidecar'],
                        app_label=_workload_rest['appLabel'],
                        version_label=_workload_rest['versionLabel'])
                    items.append(_workload)
        # filter by workload name
        if len(workload_names) > 0:
            filtered_list = []
            for _name in workload_names:
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
                                            _type=_data['objectType'],
                                            text=json.dumps(config_data))
        return config

    def service_details(self, namespace, service_name):
        """Returns details of Service.
        Args:
            namespaces: namespace where Service is located
            service_name: name of Service
        """

        _service_data = super(KialiExtendedClient, self).service_details(
            namespace=namespace,
            service=service_name)
        _service = None
        if _service_data:
            if 'health' in _service_data:
                    # update health status
                _health = Health.get_from_rest(_service_data['health'])
            else:
                _health = None
            _service_rest = self.service_list(namespaces=[namespace],
                                              service_names=[service_name]).pop()
            virtual_services = []
            if _service_data['virtualServices']:
                for _vs_data in _service_data['virtualServices']:
                    virtual_services.append(VirtualService(
                        name=_vs_data['name'],
                        created_at=parse_from_rest(_vs_data['createdAt']),
                        resource_version=_vs_data['resourceVersion']))
            destination_rules = []
            if _service_data['destinationRules']:
                for _dr_data in _service_data['destinationRules']:
                    destination_rules.append(DestinationRule(
                        name=_dr_data['name'],
                        host=_dr_data['host'],
                        created_at=parse_from_rest(_dr_data['createdAt']),
                        resource_version=_dr_data['resourceVersion']))
            _ports = ''
            for _port in _service_data['service']['ports']:
                _ports += '{}{} ({}) '.format(_port['protocol'],
                                              ' ' + _port['name'] if _port['name'] != '' else '',
                                              _port['port'])
            _service = ServiceDetails(
                    name=_service_data['service']['name'],
                    istio_sidecar=_service_rest.istio_sidecar,
                    created_at=parse_from_rest(
                        _service_data['service']['createdAt']),
                    resource_version=_service_data['service']['resourceVersion'],
                    service_type=_service_data['service']['type'],
                    ip=_service_data['service']['ip'],
                    ports=_ports.strip(),
                    health=_health,
                    virtual_services=virtual_services,
                    destination_rules=destination_rules)
        return _service

    def workload_details(self, namespace, workload_name):
        """Returns details of Workload.
        Args:
            namespaces: namespace where Workload is located
            workload_name: name of Workload
        """

        _workload_data = super(KialiExtendedClient, self).workload_details(
            namespace=namespace,
            workload=workload_name)
        _workload = None
        if _workload_data:
            _workload_rest = self.workload_list(namespaces=[namespace],
                                                workload_names=[workload_name]).pop()
            _services = []
            if _workload_data['services']:
                for _ws_data in _workload_data['services']:
                    _ports = ''
                    for _port in _ws_data['ports']:
                        _ports += '{}{} ({}) '.format(_port['protocol'],
                                                      ' ' + _port['name']
                                                      if _port['name'] != '' else '',
                                                      _port['port'])
                    _services.append(ServiceDetails(
                        name=_ws_data['name'],
                        created_at=parse_from_rest(_ws_data['createdAt']),
                        service_type=_ws_data['type'],
                        ip=_ws_data['ip'],
                        ports=_ports.strip(),
                        resource_version=_ws_data['resourceVersion']))
            _workload_pods = []
            if _workload_data['pods']:
                for _pod_data in _workload_data['pods']:
                    _istio_init_containers = ''
                    _istio_containers = ''
                    if _pod_data['istioContainers']:
                        _istio_containers = _pod_data['istioContainers'][0]['image']
                    if _pod_data['istioInitContainers']:
                        _istio_init_containers = _pod_data['istioInitContainers'][0]['image']
                    _created_by = '{} ({})'.format(_pod_data['createdBy'][0]['name'],
                                                   _pod_data['createdBy'][0]['kind'])
                    _pod = WorkloadPod(
                        name=str(_pod_data['name']),
                        created_at=from_rest_to_ui(_pod_data['createdAt']),
                        created_by=_created_by,
                        istio_init_containers=str(_istio_init_containers),
                        istio_containers=str(_istio_containers))
                    _workload_pods.append(_pod)

            _pods = []
            if len(_workload_pods) > 1:
                _pod = WorkloadPod(
                    name='{}... ({} replicas)'.format(_pod.name[:-5], len(_workload_pods)),
                    created_at='{} and {}'.format(
                        _pod.created_at, _workload_pods[len(_workload_pods)-1].created_at),
                    created_by=_workload_pods[0].created_by,
                    istio_init_containers=_workload_pods[0].istio_init_containers,
                    istio_containers=_workload_pods[0].istio_containers)
                _pods.append(_pod)
            elif len(_workload_pods) == 1:
                _pod = WorkloadPod(
                    name='{} (1 replica)'.format(_workload_pods[0].name),
                    created_at=_workload_pods[0].created_at,
                    created_by=_workload_pods[0].created_by,
                    istio_init_containers=_workload_pods[0].istio_init_containers,
                    istio_containers=_workload_pods[0].istio_containers)
                _pods.append(_pod)
            # TODO get labels
            _workload = WorkloadDetails(
                name=_workload_data['name'],
                istio_sidecar=_workload_rest.istio_sidecar,
                workload_type=_workload_data['type'],
                created_at=parse_from_rest(_workload_data['createdAt']),
                resource_version=_workload_data['resourceVersion'],
                pods_number=len(_workload_pods),
                services_number=len(_services),
                pods=_pods,
                services=_services)
        return _workload

    def application_details(self, namespace, application_name):
        """Returns details of Application.
        Args:
            namespaces: namespace where Workload is located
            application_name: name of Application
        """

        _application_data = super(KialiExtendedClient, self).app_details(
            namespace=namespace,
            app=application_name)
        _application = None
        if _application_data:
            _application_rest = self.application_list(namespaces=[namespace],
                                                      application_names=[application_name]).pop()
            _workloads = []
            if _application_data['workloads']:
                for _wl_data in _application_data['workloads']:
                    _services = ''
                    for _service in _wl_data['serviceNames']:
                        _services += '{}{}'.format(_service,
                                                   ' ' if len(_wl_data['serviceNames']) > 1 else '')
                    _workloads.append(AppWorkload(
                        name=_wl_data['workloadName'],
                        istio_sidecar=_wl_data['istioSidecar'],
                        services=_services))
            _application = ApplicationDetails(
                name=_application_data['name'],
                istio_sidecar=_application_rest.istio_sidecar,
                workloads=_workloads)
        return _application
