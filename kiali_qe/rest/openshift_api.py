import re
from kubernetes import config
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError

from kiali_qe.components.enums import (
    WorkloadType,
    IstioConfigObjectType
)
from kiali_qe.entities import DeploymentStatus
from kiali_qe.entities.istio_config import IstioConfig, IstioConfigDetails
from kiali_qe.entities.service import Service, ServiceDetails
from kiali_qe.entities.workload import (
    Workload,
    WorkloadDetails,
    WorkloadPod,
    WorkloadHealth
)
from kiali_qe.entities.applications import (
    Application,
    ApplicationDetails,
    AppWorkload,
    ApplicationHealth
)
from kiali_qe.utils import dict_contains, to_linear_string
from kiali_qe.utils.date import from_rest_to_ui
from kiali_qe.utils.log import logger


WORKLOAD_TYPES = {
    'CronJob': '_cronjob',
    'DaemonSet': '_daemonset',
    'Deployment': '_deployment',
    'DeploymentConfig': '_deploymentconfig',
    'Job': '_job',
    'Pod': '_pod',
    'ReplicaSet': '_replicaset',
    'ReplicationController': '_replicationcontroller',
    'StatefulSet': '_statefulset',
}

CONFIG_TYPES = {
    'Gateway': '_gateway',
    'VirtualService': '_virtualservice',
    'DestinationRule': '_destinationrule',
    'ServiceEntry': '_serviceentry',
    'WorkloadEntry': '_workloadentry',
    'EnvoyFilter': '_envoyfilter',
    'PeerAuthentication': '_peerauthentication',
    'RequestAuthentication': '_requestauthentication',
    'AuthorizationPolicy': '_authorizationpolicy',
    'Sidecar': '_sidecar',
}

APP_NAME_REGEX = re.compile('(-v\\d+-.*)?(-v\\d+$)?(-(\\w{0,7}\\d+\\w{0,7})$)?')

WORKLOAD_NAME_REGEX = re.compile('(-(\\w{1,8}\\d+\\w{1,8}))?(-(\\w{0,4}\\d?\\w{0,4})$)?')

ISTIO_SYSTEM = "istio-system"


class OpenshiftExtendedClient(object):

    def __init__(self):
        self._k8s_client = config.new_client_from_config()
        self._dyn_client = DynamicClient(self._k8s_client)

    @property
    def version(self):
        return self._dyn_client.version

    def _resource(self, kind, api_version='v1'):
        return self._dyn_client.resources.get(kind=kind, api_version=api_version)

    @property
    def _namespace(self):
        return self._resource(kind='Namespace')

    @property
    def _service(self):
        return self._resource(kind='Service')

    @property
    def _cronjob(self):
        return self._resource(kind='CronJob', api_version='v1beta1')

    @property
    def _daemonset(self):
        return self._resource(kind='DaemonSet')

    @property
    def _deployment(self):
        return self._resource(kind='Deployment')

    @property
    def _deploymentconfig(self):
        return self._resource(kind='DeploymentConfig')

    @property
    def _job(self):
        return self._resource(kind='Job', api_version='v1')

    @property
    def _pod(self):
        return self._resource(kind='Pod')

    @property
    def _replicaset(self):
        return self._resource(kind='ReplicaSet')

    @property
    def _envoyfilter(self):
        return self._resource(kind='EnvoyFilter', api_version='v1alpha3')

    @property
    def _replicationcontroller(self):
        return self._resource(kind='ReplicationController')

    @property
    def _statefulset(self):
        return self._resource(kind='StatefulSet')

    def _istio_config(self, kind, api_version):
        return self._resource(kind=kind, api_version=api_version)

    @property
    def _gateway(self):
        return self._istio_config(kind='Gateway', api_version='v1alpha3')

    @property
    def _virtualservice(self):
        return self._istio_config(kind='VirtualService', api_version='v1alpha3')

    @property
    def _destinationrule(self):
        return self._istio_config(kind='DestinationRule', api_version='v1alpha3')

    @property
    def _serviceentry(self):
        return self._istio_config(kind='ServiceEntry', api_version='v1beta1')

    @property
    def _workloadentry(self):
        return self._istio_config(kind='WorkloadEntry', api_version='v1alpha3')

    @property
    def _kubernetes(self):
        return self._istio_config(kind='kubernetes', api_version='v1alpha2')

    @property
    def _metric(self):
        return self._istio_config(kind='metric', api_version='v1alpha2')

    @property
    def _peerauthentication(self):
        return self._istio_config(kind='PeerAuthentication', api_version='v1beta1')

    @property
    def _requestauthentication(self):
        return self._istio_config(kind='RequestAuthentication', api_version='v1beta1')

    @property
    def _authorizationpolicy(self):
        return self._istio_config(kind='AuthorizationPolicy', api_version='v1beta1')

    @property
    def _sidecar(self):
        return self._istio_config(kind='Sidecar', api_version='v1alpha3')

    @property
    def _configmap(self):
        return self._resource(kind='ConfigMap')

    def namespace_list(self):
        """ Returns list of namespaces """
        _response = self._namespace.get()
        namespaces = []
        for _item in _response.items:
            namespaces.append(_item.metadata.name)
        return namespaces

    def namespace_labels(self, namespace):
        try:
            return dict(self._namespace.get(name=namespace).metadata.labels)
        except NotFoundError:
            return {}

    def namespace_exists(self, namespace):
        """ Returns True if given namespace exists. False otherwise. """
        try:
            self._namespace.get(name=namespace)
            return True
        except NotFoundError:
            return False

    def application_list(self, namespaces=[]):
        """ Returns list of applications """
        result_dict = {}
        application_status_dict = {}
        workloads = []
        workloads.extend(self.workload_list(namespaces=namespaces))

        for workload in workloads:
            # TODO: health needs to be added
            _name = self._get_app_name(workload)
            if _name+workload.namespace in result_dict:
                _labels = self._concat_labels(
                    result_dict[_name+workload.namespace].labels, workload.labels)
            else:
                _labels = workload.labels

            try:
                _labels = self._concat_labels(
                    self.service_details(workload.namespace,
                                         self._get_app_name(workload)).labels,
                    _labels)
            except NotFoundError:
                pass
            if workload.workload_status:
                if _name+workload.namespace in application_status_dict:
                    application_status_dict[_name+workload.namespace].append(
                        workload.workload_status.workload_status)
                else:
                    application_status_dict[_name+workload.namespace] = \
                        [workload.workload_status.workload_status]
            result_dict[_name+workload.namespace] = Application(
                _name,
                workload.namespace,
                istio_sidecar=workload.istio_sidecar,
                labels=_labels,
                # @TODO requests are not in OC
                application_status=ApplicationHealth(
                    deployment_statuses=application_status_dict[_name+workload.namespace] \
                    if _name+workload.namespace in application_status_dict else None,
                    requests=None))
        return result_dict.values()

    def service_list(self, namespaces=[]):
        """ Returns list of services
        Args:
            namespace: Namespace of the service, optional
        """
        items = []
        _raw_items = []
        if len(namespaces) > 0:
            # update items
            for _namespace in namespaces:
                _response = self._service.get(namespace=_namespace)
                _raw_items.extend(_response.items)
        else:
            _response = self._service.get()
            _raw_items.extend(_response.items)
        for _item in _raw_items:
            # update all the services to our custom entity
            # TODO: heath needs to be added
            _service = Service(
                namespace=_item.metadata.namespace,
                name=_item.metadata.name,
                istio_sidecar=self._contains_sidecar(_item),
                labels=self._get_labels(_item),
                health=None)
            items.append(_service)
        return items

    def workload_list(self, namespaces=[]):
        """ Returns list of workloads
            Order of showing/hiding priority is: Deployments, ReplicaSets, Pods
        """
        full_list = []
        filtered_list = []
        for _key, _value in WORKLOAD_TYPES.items():
            full_list.extend(self._workload_list(_value, _key,
                                                 namespaces=namespaces))

        deployment_names = [_item.name + _item.namespace for _item in full_list if
                            _item.workload_type == WorkloadType.DEPLOYMENT.text]

        replicaset_names = [_item.name + _item.namespace for _item in full_list if
                            _item.workload_type == WorkloadType.REPLICA_SET.text]

        for _item in full_list:
            _workload_name = self._get_workload_name(_item)
            if _item.workload_type == WorkloadType.REPLICA_SET.text:
                if _workload_name + _item.namespace not in deployment_names:
                    filtered_list.append(Workload(
                                            name=_workload_name,
                                            namespace=_item.namespace,
                                            workload_type=_item.workload_type,
                                            istio_sidecar=_item.istio_sidecar,
                                            labels=_item.labels,
                                            health=_item.health,
                                            workload_status=_item.workload_status))
            elif _item.workload_type in [WorkloadType.POD.text,
                                         WorkloadType.JOB.text]:
                if _workload_name + _item.namespace not in replicaset_names and\
                        _workload_name + _item.namespace not in deployment_names:
                    filtered_list.append(Workload(
                                            name=_workload_name,
                                            namespace=_item.namespace,
                                            workload_type=_item.workload_type,
                                            istio_sidecar=_item.istio_sidecar,
                                            labels=_item.labels,
                                            health=_item.health,
                                            workload_status=_item.workload_status))
            else:
                filtered_list.append(_item)

        return filtered_list

    def _workload_list(self, attribute_name, workload_type,
                       namespaces=[]):
        """ Returns list of workload
        Args:
            attribute_name: the attribute of class for getting workload
            workload_type: the type of workload
            namespace: Namespace of the workload, optional
            workload_names: Names of the workloads, optional
        """
        items = []
        _raw_items = []
        if len(namespaces) > 0:
            # update items
            for _namespace in namespaces:
                _response = getattr(self, attribute_name).get(namespace=_namespace)
                if hasattr(_response, 'items'):
                    _raw_items.extend(_response.items)
        else:
            _response = getattr(self, attribute_name).get()
            if hasattr(_response, 'items'):
                _raw_items.extend(_response.items)
        for _item in _raw_items:
            # update all the workloads to our custom entity
            _workload = Workload(
                name=_item.metadata.name,
                namespace=_item.metadata.namespace,
                workload_type=workload_type,
                istio_sidecar=self._contains_sidecar(_item),
                labels=self._get_workload_labels(_item),
                workload_status=self._get_workload_status(_item))
            items.append(_workload)
        return items

    def _get_workload_status(self, item):
        if item.status.availableReplicas:
            _workload_status = DeploymentStatus(
                name=item.metadata.name,
                replicas=item.status.replicas,
                available=item.status.availableReplicas)
            # @TODO requests are not in OC
            return WorkloadHealth(
                workload_status=_workload_status, requests=None)
        else:
            return None

    def get_failing_applications(self, namespace):
        """ Returns list of applications from given namespace which are not ready """
        result = []
        _raw_items = []
        _response = getattr(self, '_deployment').get(namespace=namespace)
        if hasattr(_response, 'items'):
            _raw_items.extend(_response.items)

        for _raw_item in _raw_items:
            if _raw_item.status.readyReplicas < _raw_item.status.replicas:
                result.append(_raw_item.metadata.name)
        return result

    def _contains_sidecar(self, item):
        try:
            return (item.spec.template.metadata.annotations['sidecar.istio.io/inject']
                    is not None and
                    item.spec.template.metadata.annotations['sidecar.istio.io/inject']
                        .lower() == 'true') or\
                item.spec.template.metadata.annotations['sidecar.istio.io/status']\
                is not None
        except (KeyError, AttributeError, TypeError):
            return False

    def _get_workload_labels(self, item):
        try:
            labels = item.spec.template.metadata.labels if item.spec.template.metadata.labels \
                else item.metadata.labels if item.metadata.labels \
                else item.spec.selector.matchLabels if item.spec.selector.matchLabels \
                else {}
        except (KeyError, AttributeError, TypeError):
            labels = {}
        return dict(labels)

    def _get_labels(self, item):
        try:
            labels = item.metadata.labels if item.metadata.labels \
                else item.spec.selector.matchLabels if item.spec.selector.matchLabels \
                else {}
        except (KeyError, AttributeError, TypeError):
            labels = {}
        return dict(labels)

    def _get_initcontainer_image(self, item):
        try:
            return item.spec.initContainers[0].image
        except (KeyError, AttributeError, TypeError):
            return ''

    def _concat_labels(self, dict1, dict2):
        result = dict1
        for _key, _value in dict2.items():
            if _key in result:
                values = result[_key].split(',')
                values.extend(_value.split(','))
                result[_key] = ','.join(sorted(set(values)))
            else:
                result[_key] = _value
        return result

    def _get_app_name(self, workload):
        return workload.labels['app'] if 'app' in workload.labels else re.sub(
            APP_NAME_REGEX,
            '',
            workload.name)

    def _get_workload_name(self, workload):
        return re.sub(
            WORKLOAD_NAME_REGEX,
            '',
            workload.name)

    def _get_service_app(self, name, labels):
        return labels['app'] if 'app' in labels else re.sub(
            APP_NAME_REGEX,
            '',
            name)

    def istio_config_list(self, namespaces=[], config_names=[]):
        """ Returns list of Istio Configs """
        result = []
        for _key, _value in CONFIG_TYPES.items():
            result.extend(self._resource_list(_value, _key,
                                              namespaces=namespaces,
                                              resource_names=config_names))
        return result

    def _resource_list(self, attribute_name, resource_type,
                       namespaces=[], resource_names=[]):
        """ Returns list of Resource
        Args:
            attribute_name: the attribute of class for getting resource
            resource_type: the type of resource
            namespace: Namespace of the resource, optional
            resource_names: Names of the r, optional
        """
        resource_type = re.sub(': .*', '', resource_type)
        items = []
        _raw_items = []
        if len(namespaces) > 0:
            # update items
            for _namespace in namespaces:
                _response = getattr(self, attribute_name).get(namespace=_namespace)
                if hasattr(_response, 'items'):
                    _raw_items.extend(_response.items)
        else:
            _response = getattr(self, attribute_name).get()
            if hasattr(_response, 'items'):
                _raw_items.extend(_response.items)
        for _item in _raw_items:
            _config = IstioConfig(name=_item.metadata.name,
                                  namespace=_item.metadata.namespace,
                                  object_type=_item.kind)
            # append this item to the final list
            items.append(_config)
        # filter by resource name
        if len(resource_names) > 0:
            filtered_list = []
            for _name in resource_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def get_workload_pods(self, namespace, workload_name):
        _raw_items = []
        _filtered_items = []
        _response = getattr(self, WORKLOAD_TYPES['Pod']).get(namespace=namespace)
        if hasattr(_response, 'items'):
            _raw_items.extend(_response.items)
        for _item in _raw_items:
            if self._get_workload_name(_item.metadata) == workload_name:
                _filtered_items.append(WorkloadPod(
                    name=_item.metadata.name,
                    podIP=_item.status.podIP))
        return _filtered_items

    def application_details(self, namespace, application_name):
        """ Returns the details of Application
        Args:
            namespace: Namespace of the service
            application_name: Application name
        """
        workloads = {}
        services = []
        deployment_statuses = []
        all_workloads = self.workload_list(namespaces=[namespace])
        all_services = self.service_list(namespaces=[namespace])

        for workload in all_workloads:
            if application_name == self._get_app_name(workload):
                workloads[workload.name] = AppWorkload(
                        name=workload.name,
                        istio_sidecar=workload.istio_sidecar)
                if workload.workload_status:
                    deployment_statuses.append(workload.workload_status.workload_status)

        for service in all_services:
            if application_name == self._get_app_name(service):
                services.append(service.name)

        _application = ApplicationDetails(
            name=application_name,
            workloads=list(set(workloads.values())),
            services=list(set(services)),
            istio_sidecar=all([w.istio_sidecar for w in workloads.values()]),
            health=None,
            # @TODO requests are not in OC
            application_status=ApplicationHealth(
                deployment_statuses=deployment_statuses,
                requests=None))

        return _application

    def service_details(self, namespace, service_name, skip_workloads=True):
        """ Returns the details of service
        Args:
            namespace: Namespace of the service
            service_name: Service name
        """
        _response = self._service.get(namespace=namespace, name=service_name)
        _ports = ''
        for _port in _response.spec.ports:
            _ports += '{}{}/{} '.format(_port['name'] + ' ' if _port['name'] and _port['name'] != ''
                                        else '',
                                        _port['port'],
                                        _port['protocol'])
        _labels = dict(_response.metadata.labels if _response.metadata.labels else {})
        _service = ServiceDetails(
            namespace=_response.metadata.namespace,
            name=_response.metadata.name,
            istio_sidecar=None,
            created_at=from_rest_to_ui(
                _response.metadata.creationTimestamp),
            resource_version=_response.metadata.resourceVersion,
            service_type=_response.spec.type,
            ip=_response.spec.clusterIP,
            endpoints=([] if skip_workloads else self._get_service_endpoints(
                namespace,
                self._get_service_app(_response.metadata.name,
                                      _labels))),
            ports=_ports.strip(),
            labels=_labels,
            selectors=dict(_response.spec.selector if _response.spec.selector else {}),
            workloads=([] if skip_workloads else self._get_service_workloads(
                namespace,
                self._get_service_app(_response.metadata.name,
                                      _labels))),
            # TODO health
            health=None,
            istio_configs=self.get_service_configs(
                _response.metadata.namespace,
                service_name))

        return _service

    def _get_service_workloads(self, namespace, app_label):
        """ Returns the list of workload for particular service by application label
        Args:
            namespace: Namespace where service is located
            app_label: app label value
        """
        result = []
        _workloads_list = self.workload_list(namespaces=[namespace])
        for _workload_item in _workloads_list:
            if dict_contains(_workload_item.labels, ['app:{}'.format(app_label)]):
                result.append(self.workload_details(namespace,
                                                    _workload_item.name,
                                                    _workload_item.workload_type))
        return result

    def _get_service_endpoints(self, namespace, app_label):
        """ Returns the list of workload pod's IPs for particular service by application label
        Args:
            namespace: Namespace where service is located
            app_label: app label value
        """
        endpoints = []
        _workloads = self.workload_list(namespaces=[namespace])
        for _workload in _workloads:
            if dict_contains(_workload.labels, ['app:{}'.format(app_label)]):
                _pods = self.get_workload_pods(namespace, _workload.name)
                for _pod in _pods:
                    endpoints.append(_pod.podIP)
        return endpoints

    def get_service_configs(self, namespace, service_name):
        """ Returns the list of istio config pages for particular service
        Args:
            namespace: Namespace where service is located
            service_name: Name of service
        """
        istio_configs = []
        _all_vs_list = self._resource_list(
            attribute_name=CONFIG_TYPES[IstioConfigObjectType.VIRTUAL_SERVICE.text],
            resource_type=CONFIG_TYPES[IstioConfigObjectType.VIRTUAL_SERVICE.text],
            namespaces=[namespace])
        for _vs_item in _all_vs_list:
            if self._is_host_in_config(namespace, service_name, to_linear_string(
                self.istio_config_details(
                    namespace=namespace,
                    object_name=_vs_item.name,
                    object_type=IstioConfigObjectType.VIRTUAL_SERVICE.text).text)):
                istio_configs.append(_vs_item)
        _all_dr_list = self._resource_list(
            attribute_name=CONFIG_TYPES[IstioConfigObjectType.DESTINATION_RULE.text],
            resource_type=CONFIG_TYPES[IstioConfigObjectType.DESTINATION_RULE.text],
            namespaces=[namespace])
        for _dr_item in _all_dr_list:
            if self._is_host_in_config(namespace, service_name, to_linear_string(
                self.istio_config_details(
                    namespace=namespace,
                    object_name=_dr_item.name,
                    object_type=IstioConfigObjectType.DESTINATION_RULE.text).text)):
                istio_configs.append(_dr_item)
        return istio_configs

    def _is_host_in_config(self, namespace, service_name, config):
        return 'host {} '.format(service_name) in config or \
            'host {}.{}.svc.cluster.local '.format(service_name, namespace) in config

    def workload_details(self, namespace, workload_name, workload_type):
        """ Returns the details of Workload
        Args:
            namespace: Namespace of the service
            workload_name: Workload name
            workload_type: Type of workload
        """
        _response = getattr(self,
                            WORKLOAD_TYPES[workload_type]).get(
                                namespace=namespace,
                                name=workload_name)
        _workload = WorkloadDetails(
            workload_type=_response.kind,
            name=_response.metadata.name,
            created_at=from_rest_to_ui(
                _response.metadata.creationTimestamp),
            resource_version=_response.metadata.resourceVersion,
            istio_sidecar=None,
            labels=dict(_response.metadata.labels if _response.metadata.labels
                        else _response.spec.selector.matchLabels),
            pods=self.get_workload_pods(namespace, workload_name),
            health=None,
            workload_status=self._get_workload_status(_response))
        _workload.set_istio_configs(istio_configs=self.get_workload_configs(namespace, _workload))
        return _workload

    def get_workload_configs(self, namespace, workload):
        """ Returns the list of istio config pages for particular workload
        Args:
            namespace: Namespace where service is located
            workload: Workload object
        """
        istio_configs = []
        _all_peer_auth_list = self._resource_list(
            attribute_name=CONFIG_TYPES[IstioConfigObjectType.PEER_AUTHENTICATION.text],
            resource_type=CONFIG_TYPES[IstioConfigObjectType.PEER_AUTHENTICATION.text],
            namespaces=[namespace])
        for _peer_auth_item in _all_peer_auth_list:
            if 'app {}'.format(self._get_app_name(workload)) in to_linear_string(
                self.istio_config_details(
                    namespace=namespace,
                    object_name=_peer_auth_item.name,
                    object_type=IstioConfigObjectType.PEER_AUTHENTICATION.text).text):
                istio_configs.append(_peer_auth_item)
        return istio_configs

    def istio_config_details(self, namespace, object_name, object_type):
        """ Returns the details of Istio Config
        Args:
            namespace: Namespace of the config
            object_name: config name
            object_type: Type of config
        """
        _response = getattr(self,
                            CONFIG_TYPES[object_type]).get(
                                namespace=namespace,
                                name=object_name)
        config = IstioConfigDetails(
                    name=_response.metadata.name,
                    _type=_response.kind,
                    text=str(_response.metadata) + ' ' + str(_response.spec))

        return config

    def delete_istio_config(self, name, namespace, kind, api_version):
        logger.debug('Deleting istio config: {}, from namespace: {}'.format(name, namespace))
        try:
            self._istio_config(kind=kind, api_version=api_version).delete(name=name,
                                                                          namespace=namespace)
        except NotFoundError:
            pass

    def create_istio_config(self, body, namespace, kind, api_version):
        logger.debug('Creating istio config: {}, from namespace: {}'.
                     format(body['metadata']['name'], namespace))
        resp = self._istio_config(kind=kind, api_version=api_version).create(body=body,
                                                                             namespace=namespace)
        return resp

    def is_auto_mtls(self):
        return 'enableAutoMtls: true' in self._configmap.get(name='istio',
                                                             namespace=ISTIO_SYSTEM).data.mesh
