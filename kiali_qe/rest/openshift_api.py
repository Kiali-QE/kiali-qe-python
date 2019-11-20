import re
from kubernetes import config
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError

from kiali_qe.components.enums import IstioConfigObjectType
from kiali_qe.entities.istio_config import IstioConfig, Rule, IstioConfigDetails
from kiali_qe.entities.service import Service, ServiceDetails
from kiali_qe.entities.workload import Workload, WorkloadDetails
from kiali_qe.entities.applications import (
    Application,
    ApplicationDetails,
    AppWorkload
)
from kiali_qe.utils.date import parse_from_rest
from kiali_qe.utils.log import logger


class OpenshiftExtendedClient(object):

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
        'Rule': '_rule',
        'Adapter': '_handler',
        'Adapter: adapter': '_adapter',
        'Template: logentry': '_logentry',
        'Template: kubernetes': '_kubernetes',
        'Template: metric': '_metric',
        'Template: template': '_template',
        'QuotaSpec': '_quotaspec',
        'QuotaSpecBinding': '_quotaspecbinding',
        'Policy': '_policy',
        'ServiceMeshPolicy': '_servicemeshpolicy',
        'ServiceMeshRbacConfig': '_servicemeshrbacconfig',
        'RbacConfig': '_rbacconfig',
        'ServiceRole': '_servicerole',
        'ServiceRoleBinding': '_servicerolebinding'
    }

    APP_NAME_REGEX = re.compile('(-v\\d+-.*)?(-v\\d+$)?(-(\\w{0,7}\\d+\\w{0,7})$)?')

    WORKLOAD_NAME_REGEX = re.compile('(-(\\w{1,8}\\d+\\w{1,8}))(-(\\w{0,7}\\d+\\w{0,7})$)?')

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
        return self._istio_config(kind='ServiceEntry', api_version='v1alpha3')

    @property
    def _rule(self):
        return self._istio_config(kind='rule', api_version='v1alpha2')

    @property
    def _logentry(self):
        return self._istio_config(kind='logentry', api_version='v1alpha2')

    @property
    def _kubernetes(self):
        return self._istio_config(kind='kubernetes', api_version='v1alpha2')

    @property
    def _metric(self):
        return self._istio_config(kind='metric', api_version='v1alpha2')

    @property
    def _template(self):
        return self._istio_config(kind='template', api_version='v1alpha2')

    @property
    def _handler(self):
        return self._istio_config(kind='handler', api_version='v1alpha2')

    @property
    def _adapter(self):
        return self._istio_config(kind='adapter', api_version='v1alpha2')

    @property
    def _quotaspec(self):
        return self._istio_config(kind='QuotaSpec', api_version='v1alpha2')

    @property
    def _quotaspecbinding(self):
        return self._istio_config(kind='QuotaSpecBinding', api_version='v1alpha2')

    @property
    def _policy(self):
        return self._istio_config(kind='Policy', api_version='v1alpha1')

    @property
    def _servicemeshpolicy(self):
        return self._istio_config(kind='ServiceMeshPolicy', api_version='v1')

    @property
    def _servicemeshrbacconfig(self):
        return self._istio_config(kind='ServiceMeshRbacConfig', api_version='v1')

    @property
    def _rbacconfig(self):
        return self._istio_config(kind='RbacConfig', api_version='v1alpha1')

    @property
    def _servicerole(self):
        return self._istio_config(kind='ServiceRole', api_version='v1alpha1')

    @property
    def _servicerolebinding(self):
        return self._istio_config(kind='ServiceRoleBinding', api_version='v1alpha1')

    def namespace_list(self):
        """ Returns list of namespaces """
        _response = self._namespace.get()
        namespaces = []
        for _item in _response.items:
            namespaces.append(_item.metadata.name)
        return namespaces

    def namespace_exists(self, namespace):
        """ Returns True if given namespace exists. False otherwise. """
        try:
            self._namespace.get(name=namespace)
            return True
        except NotFoundError:
            return False

    def application_list(self, namespaces=[], application_names=[]):
        """ Returns list of applications """
        result = {}
        workloads = []
        workloads.extend(self.workload_list(namespaces=namespaces))

        for workload in workloads:
            # TODO: health needs to be added
            name = self._get_app_name(workload)
            result[name+workload.namespace] = Application(name,
                                                          workload.namespace,
                                                          istio_sidecar=workload.istio_sidecar)
        # filter by service name
        if len(application_names) > 0:
            filtered_list = []
            for _name in application_names:
                filtered_list.extend([_i for _i in result.values() if _name in _i.name])
            return set(filtered_list)
        return result.values()

    def service_list(self, namespaces=[], service_names=[]):
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
                app_label=self._get_label(_item, 'app'),
                version_label=self._get_label(_item, 'version'),
                health=None)
            items.append(_service)
        # filter by service name
        if len(service_names) > 0:
            filtered_list = []
            for _name in service_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def workload_list(self, namespaces=[], workload_names=[]):
        """ Returns list of workloads """
        result = []
        for _key, _value in self.WORKLOAD_TYPES.items():
            # TODO apply Job filters
            # TODO apply Pod filters
            result.extend(self._workload_list(_value, _key,
                                              namespaces=namespaces,
                                              workload_names=workload_names))

        return result

    def _workload_list(self, attribute_name, workload_type,
                       namespaces=[], workload_names=[]):
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
                app_label=self._get_label(_item, 'app'),
                version_label=self._get_label(_item, 'version'))
            items.append(_workload)
        # filter by workload name
        if len(workload_names) > 0:
            filtered_list = []
            for _name in workload_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

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

    def _get_label(self, item, label):
        try:
            return item.metadata.labels[label]
        except (KeyError, AttributeError, TypeError):
            return None

    def _get_app_name(self, workload):
        return workload.app_label if workload.app_label else re.sub(
            self.APP_NAME_REGEX,
            '',
            workload.name)

    def _get_workload_name(self, workload):
        return re.sub(
            self.WORKLOAD_NAME_REGEX,
            '',
            workload.name)

    def istio_config_list(self, namespaces=[], config_names=[]):
        """ Returns list of Istio Configs """
        result = []
        for _key, _value in self.CONFIG_TYPES.items():
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
            if str(resource_type) == IstioConfigObjectType.RULE.text:
                _rule = Rule(name=_item.metadata.name,
                             namespace=_item.metadata.namespace,
                             object_type=resource_type)
                # append this item to the final list
                items.append(_rule)
            elif str(resource_type) == IstioConfigObjectType.ADAPTER.text or\
                    str(resource_type) == IstioConfigObjectType.TEMPLATE.text:
                _rule = Rule(name=_item.metadata.name,
                             namespace=_item.metadata.namespace,
                             object_type='{}: {}'.format(
                                 resource_type, _item.kind))
                # append this item to the final list
                items.append(_rule)
            elif str(resource_type) == IstioConfigObjectType.SERVICE_MESH_POLICY.text or\
                    str(resource_type) == IstioConfigObjectType.SERVICE_MESH_RBAC_CONFIG.text:
                _config = IstioConfig(name=_item.metadata.name,
                                      namespace="istio-system",
                                      object_type=resource_type)
                if _config not in items:
                    # append this item to the final list
                    items.append(_config)
            else:
                _config = IstioConfig(name=_item.metadata.name,
                                      namespace=_item.metadata.namespace,
                                      object_type=resource_type)
                # append this item to the final list
                items.append(_config)
        # filter by resource name
        if len(resource_names) > 0:
            filtered_list = []
            for _name in resource_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def application_details(self, namespace, application_name):
        """ Returns the details of Application
        Args:
            namespace: Namespace of the service
            application_name: Application name
        """
        workloads = {}
        services = []
        all_workloads = self.workload_list(namespaces=[namespace])
        all_services = self.service_list(namespaces=[namespace])

        for workload in all_workloads:
            if application_name == self._get_app_name(workload):
                workload_name = self._get_workload_name(workload)
                workloads[workload_name] = AppWorkload(
                        name=workload_name,
                        istio_sidecar=workload.istio_sidecar)

        for service in all_services:
            if application_name == self._get_app_name(service):
                services.append(service.name)

        _application = ApplicationDetails(
            name=application_name,
            workloads=workloads.values(),
            services=list(set(services)),
            istio_sidecar=all([w.istio_sidecar for w in workloads.values()]),
            # TODO health
            health=None)

        return _application

    def service_details(self, namespace, service_name):
        """ Returns the details of service
        Args:
            namespace: Namespace of the service
            service_name: Service name
        """
        _response = self._service.get(namespace=namespace, name=service_name)
        _ports = ''
        for _port in _response.spec.ports:
            _ports += '{}{} ({}) '.format(_port['protocol'],
                                          ' ' + _port['name'] if _port['name'] != '' else '',
                                          _port['port'])
        _service = ServiceDetails(
            namespace=_response.metadata.namespace,
            name=_response.metadata.name,
            istio_sidecar=None,
            created_at=parse_from_rest(
                _response.metadata.creationTimestamp),
            resource_version=_response.metadata.resourceVersion,
            service_type=_response.spec.type,
            ip=_response.spec.clusterIP,
            ports=_ports.strip(),
            labels=dict(_response.metadata.labels),
            selectors=dict(_response.spec.selector if _response.spec.selector else {}),
            # TODO health
            health=None)

        return _service

    def workload_details(self, namespace, workload_name, workload_type):
        """ Returns the details of Workload
        Args:
            namespace: Namespace of the service
            workload_name: Workload name
            workload_type: Type of workload
        """
        _response = getattr(self,
                            self.WORKLOAD_TYPES[workload_type]).get(
                                namespace=namespace,
                                name=workload_name)
        _workload = WorkloadDetails(
            workload_type=_response.kind,
            name=_response.metadata.name,
            created_at=parse_from_rest(
                _response.metadata.creationTimestamp),
            resource_version=_response.metadata.resourceVersion,
            istio_sidecar=None,
            labels=dict(_response.metadata.labels),
            # TODO health
            health=None)

        return _workload

    def istio_config_details(self, namespace, object_name, object_type):
        """ Returns the details of Istio Config
        Args:
            namespace: Namespace of the config
            object_name: config name
            object_type: Type of config
        """
        _response = getattr(self,
                            self.CONFIG_TYPES[object_type]).get(
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
