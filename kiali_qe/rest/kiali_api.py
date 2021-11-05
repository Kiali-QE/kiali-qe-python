import json

from selenium.common.exceptions import NoSuchElementException
from kiali.client import KialiClient
from kiali_qe.components.enums import (
    IstioConfigObjectType as OBJECT_TYPE,
    IstioConfigValidation,
    OverviewPageType,
    TimeIntervalRestParam,
    HealthType as HEALTH_TYPE,
    ItemIconType,
    HealthType
)
from kiali_qe.entities import Requests
from kiali_qe.entities.istio_config import IstioConfig, IstioConfigDetails
from kiali_qe.entities.service import (
    ServiceHealth,
    Service,
    ServiceDetails,
    VirtualService,
    DestinationRule,
    SourceWorkload,
    VirtualServiceWeight,
    DestinationRuleSubset
)
from kiali_qe.entities.workload import (
    Workload,
    WorkloadDetails,
    WorkloadPod,
    WorkloadHealth,
    DestinationService
)
from kiali_qe.entities.applications import (
    Application,
    ApplicationDetails,
    AppWorkload,
    ApplicationHealth
)
from kiali_qe.entities.overview import Overview
from kiali_qe.utils import to_linear_string, dict_to_params
from kiali_qe.utils.date import from_rest_to_ui
from kiali_qe.utils.log import logger


ISTIO_CONFIG_TYPES = {'DestinationRule': 'destinationrules',
                      'VirtualService': 'virtualservices',
                      'ServiceEntry': 'serviceentries',
                      'WorkloadEntry': 'workloadentries',
                      'WorkloadGroup': 'workloadgroups',
                      'Gateway': 'gateways',
                      'Handler': 'handler',
                      'EnvoyFilter': 'envoyfilters',
                      'HTTPAPISpec': 'httpapispecs',
                      'HTTPAPISpecBinding': 'httpapispecbindings',
                      'QuotaSpecBinding': 'quotaspecbindings',
                      'QuotaSpec': 'quotaspecs',
                      'PeerAuthentication': 'peerauthentications',
                      'RequestAuthentication': 'requestauthentications',
                      'MeshPolicy': 'meshpolicies',
                      'RbacConfig': 'rbacconfigs',
                      'AuthorizationPolicy': 'authorizationpolicies',
                      'Sidecar': 'sidecars',
                      'ServiceRole': 'serviceroles',
                      'ServiceRoleBinding': 'servicerolebindings'}


class KialiExtendedClient(KialiClient):

    def namespace_list(self):
        """ Returns list of namespaces """
        entities = []
        entities_j = self.get_response('namespaceList')
        if entities_j:
            for entity_j in entities_j:
                entities.append(entity_j['name'])
        return entities

    def namespace_labels(self, namespace):
        """ Returns list of namespaces """
        labels = []
        entities_j = self.get_response('namespaceList')
        if entities_j:
            for entity_j in entities_j:
                if entity_j['name'] == namespace:
                    labels = self.get_labels(entity_j)
        return labels

    def namespace_exists(self, namespace):
        """ Returns True if given namespace exists. False otherwise. """
        return namespace in self.namespace_list()

    def service_list(self, namespaces=[]):
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
            _data = self.get_response('serviceList', path={'namespace': _namespace})
            _services = _data['services']
            # update all the services to our custom entity
            for _service_rest in _services:
                _service_health = self.get_service_health(
                    namespace=_namespace,
                    service_name=_service_rest['name'],
                    istioSidecar=_service_rest['istioSidecar'])
                _service = Service(
                    namespace=_namespace,
                    name=_service_rest['name'],
                    istio_sidecar=_service_rest['istioSidecar'],
                    health=_service_health.is_healthy() if _service_health else None,
                    service_status=_service_health,
                    icon=self.get_icon_type(_service_rest),
                    labels=self.get_labels(_service_rest))
                items.append(_service)
        return items

    def overview_list(self, namespaces=[], overview_type=OverviewPageType.APPS):
        """Returns list of overviews.
        Args:
            namespaces: can be zero or any number of namespaces
        """
        overviews = []
        namespace_list = []
        if len(namespaces) > 0:
            namespace_list.extend(namespaces)
        else:
            namespace_list = self.namespace_list()
        # update items
        for _namespace in namespace_list:
            if overview_type == OverviewPageType.SERVICES:
                _items = self.service_list([_namespace])
            elif overview_type == OverviewPageType.WORKLOADS:
                _items = self.workload_list([_namespace])
            else:
                _items = self.application_list([_namespace])

            _healthy = 0
            _unhealthy = 0
            _degraded = 0
            _na = 0
            _idle = 0
            for _item in _items:
                if _item.health == HEALTH_TYPE.HEALTHY:
                    _healthy += 1
                if _item.health == HEALTH_TYPE.DEGRADED:
                    _degraded += 1
                if _item.health == HEALTH_TYPE.FAILURE:
                    _unhealthy += 1
                if _item.health == HEALTH_TYPE.NA:
                    _na += 1
                if _item.health == HEALTH_TYPE.IDLE:
                    _idle += 1
            _overview = Overview(
                overview_type=overview_type.text,
                namespace=_namespace,
                items=len(_items),
                healthy=_healthy,
                unhealthy=_unhealthy,
                degraded=_degraded,
                na=_na,
                idle=_idle,
                labels=self.namespace_labels(_namespace))
            overviews.append(_overview)
        return overviews

    def application_list(self, namespaces=[]):
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
            _data = self.get_response('appList', path={'namespace': _namespace})
            _applications = _data['applications']
            if _applications:
                for _application_rest in _applications:
                    _app_health = self.get_app_health(
                            namespace=_namespace,
                            app_name=_application_rest['name'])
                    _application = Application(
                        namespace=_namespace,
                        name=_application_rest['name'],
                        istio_sidecar=_application_rest['istioSidecar'],
                        health=_app_health.is_healthy() if _app_health else None,
                        application_status=_app_health,
                        labels=self.get_labels(_application_rest))
                    items.append(_application)
        return items

    def workload_list(self, namespaces=[]):
        """Returns list of workloads.
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
            _data = self.get_response('workloadList', path={'namespace': _namespace})
            _workloads = _data['workloads']
            if _workloads:
                for _workload_rest in _workloads:
                    _workload_health = self.get_workload_health(
                        namespace=_namespace,
                        workload_name=_workload_rest['name'])
                    _workload = Workload(
                        namespace=_namespace,
                        name=_workload_rest['name'],
                        workload_type=_workload_rest['type'],
                        istio_sidecar=_workload_rest['istioSidecar'],
                        labels=self.get_labels(_workload_rest),
                        health=_workload_health.is_healthy() if _workload_health else None,
                        icon=self.get_icon_type(_workload_rest),
                        workload_status=_workload_health)
                    items.append(_workload)
        return items

    def istio_config_list(self, namespaces=[], config_names=[], params=None):
        """Returns list of istio config.
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
            _data = self.get_response(
                'istioConfigList', path={'namespace': _namespace}, params=params)

            # update DestinationRule
            if len(_data['destinationRules']) > 0:
                for _policy in _data['destinationRules']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.DESTINATION_RULE.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'destinationrules',
                                                                    _policy['metadata']['name'])))

            # update VirtualService
            if len(_data['virtualServices']) > 0:
                for _policy in _data['virtualServices']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.VIRTUAL_SERVICE.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'virtualservices',
                                                                    _policy['metadata']['name'])))

            # update Policy
            if len(_data['peerAuthentications']) > 0:
                for _policy in _data['peerAuthentications']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.PEER_AUTHENTICATION.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'peerauthentications',
                                                                    _policy['metadata']['name'])))

            # update RequestAuthentication
            if len(_data['requestAuthentications']) > 0:
                for _policy in _data['requestAuthentications']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.REQUEST_AUTHENTICATION.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'requestauthentications',
                                                                    _policy['metadata']['name'])))

            # update Gateway
            if len(_data['gateways']) > 0:
                for _policy in _data['gateways']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.GATEWAY.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'gateways',
                                                                    _policy['metadata']['name'])))

            # update EnvoyFilter
            if len(_data['envoyFilters']) > 0 and len(_data['envoyFilters']) > 0:
                for _policy in _data['envoyFilters']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.ENVOY_FILTER.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'envoyfilters',
                                                                    _policy['metadata']['name'])))

            # update serviceEntries
            if len(_data['serviceEntries']) > 0:
                for _policy in _data['serviceEntries']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.SERVICE_ENTRY.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'serviceentries',
                                                                    _policy['metadata']['name'])))

            # update WorkloadEntries
            if len(_data['workloadEntries']) > 0:
                for _policy in _data['workloadEntries']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.WORKLOAD_ENTRY.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'workloadentries',
                                                                    _policy['metadata']['name'])))

            # update workloadGroups
            if len(_data['workloadGroups']) > 0:
                for _policy in _data['workloadGroups']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.WORKLOAD_GROUP.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'workloadgroups',
                                                                    _policy['metadata']['name'])))

            # update sidecars
            if len(_data['sidecars']) > 0:
                for _policy in _data['sidecars']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.SIDECAR.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'sidecars',
                                                                    _policy['metadata']['name'])))

            # update authorizationPolicies
            if len(_data['authorizationPolicies']) > 0:
                for _policy in _data['authorizationPolicies']:
                    items.append(IstioConfig(
                        name=_policy['metadata']['name'],
                        namespace=_namespace,
                        object_type=OBJECT_TYPE.AUTHORIZATION_POLICY.text,
                        validation=self.get_istio_config_validation(_namespace,
                                                                    'authorizationpolicies',
                                                                    _policy['metadata']['name'])))

        # apply filters
        if len(config_names) > 0:
            name_filtered_list = []
            for _name in config_names:
                name_filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(name_filtered_list)
        return items

    def istio_config_details(self, namespace, object_type, object_name):
        """Returns details of istio config or None if does not exist.
        Args:
            namespaces: namespace where istio config is located
            object_type: type of istio config
            object_name: name of istio config
        """
        config_type = ISTIO_CONFIG_TYPES[object_type]
        _data = self.get_response('istioConfigDetails',
                                  path={'namespace': namespace, 'object_type': config_type,
                                        'object': object_name})
        config = None
        config_data = None
        if 'error' in _data:
            raise NoSuchElementException(_data['error'])
        else:
            # get DestinationRule
            if _data['destinationRule']:
                config_data = _data['destinationRule']

            # get VirtualService
            if _data['virtualService']:
                config_data = _data['virtualService']

            # get EnvoyFilter
            if _data['envoyFilter']:
                config_data = _data['envoyFilter']

            # get Gateway
            if _data['gateway']:
                config_data = _data['gateway']

            # get serviceEntry
            if _data['serviceEntry']:
                config_data = _data['serviceEntry']

            # get workloadEntry
            if _data['workloadEntry']:
                config_data = _data['workloadEntry']

            # get workloadGroup
            if _data['workloadGroup']:
                config_data = _data['workloadGroup']

            # get PeerAuthentication
            if _data['peerAuthentication']:
                config_data = _data['peerAuthentication']

            # get RequestAuthentication
            if _data['requestAuthentication']:
                config_data = _data['requestAuthentication']

            # get sidecar
            if _data['sidecar']:
                config_data = _data['sidecar']

            # get authorizationPolicy
            if _data['authorizationPolicy']:
                config_data = _data['authorizationPolicy']

            if config_data:
                config = IstioConfigDetails(
                    name=config_data['metadata']['name'],
                    _type=_data['objectType'],
                    text=json.dumps(config_data),
                    validation=self.get_istio_config_validation(namespace,
                                                                config_type,
                                                                object_name),
                    error_messages=self.get_istio_config_messages(namespace,
                                                                  config_type,
                                                                  object_name))
        return config

    def service_details(self, namespace, service_name):
        """Returns details of Service.
        Args:
            namespaces: namespace where Service is located
            service_name: name of Service
        """

        _service_data = self.get_response('serviceDetails',
                                          path={'namespace': namespace, 'service': service_name},
                                          params={'validate': 'true'})
        _service = None
        if _service_data:
            _services_rest = self.service_list(namespaces=[namespace])
            _service_rest = set([_s for _s in _services_rest
                                if _s.name == service_name]).pop()
            workloads = []
            if _service_data['workloads']:
                for _wl_data in _service_data['workloads']:
                    workloads.append(WorkloadDetails(
                        name=_wl_data['name'],
                        workload_type=_wl_data['type'],
                        labels=self.get_labels(_wl_data),
                        created_at=from_rest_to_ui(_wl_data['createdAt']),
                        resource_version=_wl_data['resourceVersion']))
            source_workloads = []
            # TODO better way to find Traffic
            if 'dependencies' in _service_data:
                for _wl_data in _service_data['dependencies']:
                    _wl_names = []
                    for _wl_name in _service_data['dependencies'][_wl_data]:
                        _wl_names.append(_wl_name['name'])
                    source_workloads.append(SourceWorkload(
                        to=_wl_data,
                        workloads=_wl_names))
            istio_configs = []
            virtual_services = []
            if _service_data['virtualServices'] \
                    and len(_service_data['virtualServices']) > 0:
                for _vs_data in _service_data['virtualServices']:
                    _weights = []
                    if 'http' in _vs_data['spec']:
                        _protocol = _vs_data['spec']['http'][0]
                    else:
                        _protocol = _vs_data['spec']['tcp'][0]
                    for _route in _protocol['route']:
                        _weights.append(VirtualServiceWeight(
                            host=_route['destination']['host'],
                            subset=_route['destination']['subset']
                            if 'subset' in _route['destination'] else None,
                            port=_route['destination']['port']['number']
                            if 'port' in _route['destination'] else None,
                            status=_route['destination']['status']
                            if 'status' in _route['destination'] else None,
                            weight=_route['weight'] if
                            ('weight' in _route and _route['weight'] != 0) else None)
                        )
                    if 'match' in _protocol:
                        _protocol_route = 'match ' + \
                            to_linear_string(_protocol['match'])
                    else:
                        _protocol_route = ''
                    _validation = self.get_istio_config_validation(
                            _vs_data['metadata']['namespace'],
                            'virtualservices',
                            _vs_data['metadata']['name'])
                    virtual_services.append(VirtualService(
                        status=_validation,
                        name=_vs_data['metadata']['name'],
                        created_at=from_rest_to_ui(_vs_data['metadata']['creationTimestamp']),
                        resource_version=_vs_data['metadata']['resourceVersion'],
                        protocol_route=_protocol_route,
                        hosts=_vs_data['spec']['hosts'],
                        weights=_weights))
                    # It also requires IstioConfig type of objects in several testcases
                    istio_configs.append(IstioConfig(
                        name=_vs_data['metadata']['name'],
                        namespace=_vs_data['metadata']['namespace'],
                        object_type=OBJECT_TYPE.VIRTUAL_SERVICE.text,
                        validation=_validation))

            destination_rules = []
            if _service_data['destinationRules'] \
                    and len(_service_data['destinationRules']) > 0:
                for _dr_data in _service_data['destinationRules']:
                    if 'trafficPolicy' in _dr_data['spec']:
                        _traffic_policy = to_linear_string(_dr_data['spec']['trafficPolicy'])
                    else:
                        _traffic_policy = None
                    _dr_subsets = []
                    if 'subsets' in _dr_data['spec']:
                        for _subset in _dr_data['spec']['subsets']:
                            _dr_subsets.append(DestinationRuleSubset(
                                status=None,
                                name=_subset['name'],
                                labels=_subset['labels'] if 'labels' in _subset else {},
                                traffic_policy=(to_linear_string(_subset['trafficPolicy'])
                                                if 'trafficPolicy' in _subset else None)))

                    _validation = self.get_istio_config_validation(
                            _dr_data['metadata']['namespace'],
                            'destinationrules',
                            _dr_data['metadata']['name'])
                    destination_rules.append(DestinationRule(
                        status=_validation,
                        name=_dr_data['metadata']['name'],
                        host=_dr_data['spec']['host'],
                        traffic_policy=_traffic_policy if _traffic_policy else '',
                        subsets=_dr_subsets,
                        created_at=from_rest_to_ui(_dr_data['metadata']['creationTimestamp']),
                        resource_version=_dr_data['metadata']['resourceVersion']))

                    # It also requires IstioConfig type of objects in several testcases
                    istio_configs.append(IstioConfig(
                        name=_dr_data['metadata']['name'],
                        namespace=_dr_data['metadata']['namespace'],
                        object_type=OBJECT_TYPE.DESTINATION_RULE.text,
                        validation=_validation))

            _ports = ''
            for _port in _service_data['service']['ports']:
                _ports += '{}{}/{} '.format(_port['name'] + ' ' if _port['name'] != '' else '',
                                            _port['port'],
                                            _port['protocol'])
            endpoints = []
            if _service_data['endpoints']:
                for _endpoint in _service_data['endpoints'][0]['addresses']:
                    endpoints.append(_endpoint['ip'])
            _labels = self.get_labels(_service_data['service'])
            _applications = set([_a.name for _a in self.application_list(namespaces=[namespace])
                                 if _labels['app'] == _a.name])
            _validations = []
            if _service_data['validations'] \
                    and len(_service_data['validations']['service']) > 0:
                for _data in _service_data['validations']['service'][service_name]['checks']:
                    _validations.append(_data['message'])
            _service_health = self.get_service_health(
                namespace=namespace,
                service_name=service_name,
                istioSidecar=_service_rest.istio_sidecar)
            _service = ServiceDetails(
                    name=_service_data['service']['name'],
                    istio_sidecar=_service_rest.istio_sidecar,
                    created_at=from_rest_to_ui(
                        _service_data['service']['createdAt']),
                    resource_version=_service_data['service']['resourceVersion'],
                    service_type=_service_data['service']['type'],
                    ip=_service_data['service']['ip'],
                    endpoints=endpoints,
                    validations=_validations,
                    ports=_ports.strip(),
                    labels=_labels,
                    selectors=self.get_selectors(_service_data['service']),
                    health=_service_health.is_healthy() if _service_health else None,
                    service_status=_service_health,
                    icon=self.get_icon_type(_service_data),
                    workloads=workloads,
                    applications=_applications,
                    traffic=source_workloads,
                    virtual_services=virtual_services,
                    destination_rules=destination_rules,
                    istio_configs=istio_configs,
                    istio_configs_number=len(istio_configs))
        return _service

    def workload_details(self, namespace, workload_name, workload_type):
        """Returns details of Workload.
        Args:
            namespaces: namespace where Workload is located
            workload_name: name of Workload
        """

        _workload_data = self.get_response('workloadDetails',
                                           path={'namespace': namespace, 'workload': workload_name})
        _workload = None
        if _workload_data:
            _workloads_rest = self.workload_list(namespaces=[namespace])
            _workload_rest = set([_w for _w in _workloads_rest
                                  if _w.name == workload_name]).pop()
            _services = []
            if _workload_data['services']:
                for _ws_data in _workload_data['services']:
                    _services.append(_ws_data['name'])
            _destination_services = []
            # TODO find a better way to take Traffic
            if 'destinationServices' in _workload_data:
                for _ds_data in _workload_data['destinationServices']:
                    _destination_services.append(DestinationService(
                        _from=workload_name,
                        name=_ds_data['name'],
                        namespace=_ds_data['namespace']))
            _all_pods = []
            if _workload_data['pods']:
                for _pod_data in _workload_data['pods']:
                    ''' TODO read from tooltip in UI and then activate this code
                    _istio_init_containers = ''
                    _istio_containers = ''
                    if _pod_data['istioContainers']:
                        _istio_containers = _pod_data['istioContainers'][0]['image']
                    if _pod_data['istioInitContainers']:
                        _istio_init_containers = _pod_data['istioInitContainers'][0]['image']
                    _created_by = '{} ({})'.format(_pod_data['createdBy'][0]['name'],
                                                   _pod_data['createdBy'][0]['kind'])'''
                    _pod = WorkloadPod(
                        name=str(_pod_data['name']),
                        status=self.get_pod_status(_workload_data['istioSidecar'], _pod_data))
                    _all_pods.append(_pod)

            _workload_health = self.get_workload_health(
                        namespace=namespace,
                        workload_name=_workload_data['name'])

            _labels = self.get_labels(_workload_data)
            _applications = set([_a.name for _a in self.application_list(namespaces=[namespace])
                                 if _labels['app'] == _a.name])
            _config_list = self.istio_config_list(
                namespaces=[namespace], config_names=[],
                params={'workloadSelector': dict_to_params(_labels)})

            _workload = WorkloadDetails(
                name=_workload_data['name'],
                istio_sidecar=_workload_rest.istio_sidecar,
                workload_type=_workload_data['type'],
                created_at=from_rest_to_ui(_workload_data['createdAt']),
                resource_version=_workload_data['resourceVersion'],
                health=_workload_health.is_healthy() if _workload_health else None,
                workload_status=_workload_health,
                icon=self.get_icon_type(_workload_data),
                labels=_labels,
                traffic=_destination_services,
                pods=_all_pods,
                services=_services,
                applications=_applications,
                istio_configs=_config_list)
        return _workload

    def application_details(self, namespace, application_name):
        """Returns details of Application.
        Args:
            namespaces: namespace where Workload is located
            application_name: name of Application
        """

        _application_data = self.get_response('appDetails',
                                              path={'namespace': namespace,
                                                    'app': application_name})
        _application = None
        if _application_data:
            _applications_rest = self.application_list(namespaces=[namespace])
            _application_rest = set([_a for _a in _applications_rest
                                     if _a.name == application_name]).pop()
            _workloads = []
            if _application_data['workloads']:
                for _wl_data in _application_data['workloads']:
                    _workloads.append(AppWorkload(
                        name=_wl_data['workloadName'],
                        istio_sidecar=_wl_data['istioSidecar']))
            _services = []
            if 'serviceNames' in _application_data:
                for _service in _application_data['serviceNames']:
                    _services.append(_service)
            _app_health = self.get_app_health(
                            namespace=namespace,
                            app_name=_application_data['name'])
            _application = ApplicationDetails(
                name=_application_data['name'],
                istio_sidecar=_application_rest.istio_sidecar,
                health=_app_health.is_healthy() if _app_health else None,
                application_status=_app_health,
                workloads=_workloads,
                services=_services)
        return _application

    def get_service_health(self, namespace, service_name, istioSidecar,
                           time_interval=TimeIntervalRestParam.LAST_MINUTE.text):
        """Returns Health of Service.
        Args:
            namespaces: namespace where Service is located
            service_name: name of Service
            time_interval: The rate interval used for fetching error rate
        """

        if not istioSidecar:  # without sidecar no health is available
            return ServiceHealth(requests=Requests(errorRatio=-0.01))

        _health_data = self.get_response(method_name='serviceHealth',
                                         path={'namespace': namespace, 'service': service_name},
                                         params={'rateInterval': time_interval})
        if _health_data:
            return ServiceHealth.get_from_rest(_health_data)
        else:
            return None

    def get_workload_health(self, namespace, workload_name,
                            time_interval=TimeIntervalRestParam.LAST_MINUTE.text):
        """Returns Health of Workload.
        Args:
            namespaces: namespace where Workload is located
            workload_name: name of Workload
            time_interval: The rate interval used for fetching error rate
        """

        _health_data = self.get_response(method_name='workloadHealth',
                                         path={'namespace': namespace, 'workload': workload_name},
                                         params={'rateInterval': time_interval})
        if _health_data:
            return WorkloadHealth.get_from_rest(_health_data)
        else:
            return None

    def get_app_health(self, namespace, app_name,
                       time_interval=TimeIntervalRestParam.LAST_MINUTE.text):
        """Returns Health of Application.
        Args:
            namespaces: namespace where Application is located
            workload_name: name of Application
            time_interval: The rate interval used for fetching error rate
        """

        _health_data = self.get_response(method_name='appHealth',
                                         path={'namespace': namespace, 'app': app_name},
                                         params={'rateInterval': time_interval})
        if _health_data:
            return ApplicationHealth.get_from_rest(_health_data)
        else:
            return None

    def get_istio_config_validation(self, namespace, object_type, object_name):
        """Returns Validation of Istio Config.
        Args:
            namespaces: namespace where Config is located
            object_type: type of the Config
            object: name of Config
        """

        _health_data = self.get_validation('istioConfigDetails',
                                           namespace=namespace,
                                           object_type=object_type,
                                           object=object_name)
        if _health_data:
            if len(_health_data['checks']) > 0:
                if 'error' in set(check['severity'] for check in _health_data['checks']):
                    return IstioConfigValidation.NOT_VALID
                else:
                    return IstioConfigValidation.WARNING
            else:
                return IstioConfigValidation.VALID
        else:
            return IstioConfigValidation.NA

    def get_istio_config_messages(self, namespace, object_type, object_name):
        """Returns Validation Messages of Istio Config.
        Args:
            namespaces: namespace where Config is located
            object_type: type of the Config
            object: name of Config
        """
        _error_messages = []

        _health_data = self.get_validation('istioConfigDetails',
                                           namespace=namespace,
                                           object_type=object_type,
                                           object=object_name)
        if _health_data:
            if len(_health_data['checks']) > 0:
                for _check in _health_data['checks']:
                    _error_messages.append(_check['message'])
        return _error_messages

    def create_istio_config(self, body, namespace, kind, api_version):
        """Creates Istio Config.
        Args:
            body: config body
            namespaces: namespace where Config is located
            kind: type of the Config
            api_version: Config api version (not used)
        """

        logger.debug('Creating istio config: {}, from namespace: {}'.
                     format(body['metadata']['name'], namespace))
        return self.post_response('istioConfigCreate',
                                  namespace=namespace,
                                  object_type=ISTIO_CONFIG_TYPES[kind],
                                  data=body)

    def delete_istio_config(self, name, namespace, kind, api_version):
        """Deletes Istio Config.
        Args:
            name: config name
            namespaces: namespace where Config is located
            kind: type of the Config
            api_version: Config api version (not used)
        """

        logger.debug('Deleting istio config: {}, from namespace: {}'.format(name, namespace))
        return self.delete_response('istioConfigDelete',
                                    namespace=namespace,
                                    object_type=ISTIO_CONFIG_TYPES[kind],
                                    object=name)

    def update_namespace_auto_injection(self, namespace, auto_injection=None):
        """
        Update auto injection of given namespace.
        Args:
            namespace: namespace
            auto_injection: 'enabled','disabled' or None(deleted)
        """
        date_dict = {'metadata': {'labels': {'istio-injection': auto_injection}}}
        return self.patch_response('namespaceUpdate',
                                   namespace=namespace,
                                   data=date_dict)

    def update_workload_auto_injection(self, workload_name, namespace, auto_injection=None):
        """
        Update auto injection of given workload.
        Args:
            workload_name: workload name
            auto_injection: 'enabled','disabled' or None(deleted)
        """
        date_dict = {'spec': {'template': {'metadata': {'annotations': {
            'sidecar.istio.io/inject': auto_injection}}}}}
        return self.patch_response('workloadUpdate',
                                   namespace=namespace,
                                   workload=workload_name,
                                   data=date_dict)

    def get_icon_type(self, object_rest):
        _icon = None
        if 'additionalDetailSample' in object_rest and object_rest['additionalDetailSample']:
            if object_rest['additionalDetailSample']['title'] \
                    == ItemIconType.API_DOCUMENTATION.text:
                _icon = ItemIconType.API_DOCUMENTATION
        return _icon

    def get_labels(self, object_rest):
        _labels = {}
        if 'labels' in object_rest and object_rest['labels']:
            _labels = object_rest['labels']
        return _labels

    def get_selectors(self, object_rest):
        _selectors = {}
        if 'selectors' in object_rest:
            _selectors = object_rest['selectors']
        return _selectors

    def get_response(self, method_name, path=None, params=None):
        return super(KialiExtendedClient, self).request(method_name=method_name, path=path,
                                                        params=params).json()

    def post_response(self, method_name, data, **kwargs):
        return super(KialiExtendedClient, self).request(
            method_name=method_name,
            path=kwargs,
            http_method="POST",
            data=json.dumps(data))

    def patch_response(self, method_name, data, **kwargs):
        return super(KialiExtendedClient, self).request(
            method_name=method_name,
            path=kwargs,
            http_method="PATCH",
            data=json.dumps(data))

    def delete_response(self, method_name, **kwargs):
        return super(KialiExtendedClient, self).request(
            method_name=method_name,
            path=kwargs,
            http_method="DELETE")

    def get_validation(self, method_name, **kwargs):
        response = super(KialiExtendedClient, self).request(
            method_name=method_name,
            path=kwargs,
            params={'validate': 'true'}).json()
        return response['validation'] if 'validation' in response else None

    def get_pod_status(self, istioSidecar, pod_data):
        if not pod_data['versionLabel'] or not pod_data['appLabel'] \
                or pod_data['status'] == 'Pending':
            return HealthType.DEGRADED
        else:
            return HealthType.HEALTHY
