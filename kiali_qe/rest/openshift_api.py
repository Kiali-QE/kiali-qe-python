from kubernetes import config
from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import NotFoundError

from kiali_qe.entities.service import Service
from kiali_qe.entities.workload import Workload


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
    def _replicationcontroller(self):
        return self._resource(kind='ReplicationController')

    @property
    def _statefulset(self):
        return self._resource(kind='StatefulSet')

    def _istio_config(self, kind, api_version):
        return self._resource(kind=kind, api_version=api_version)

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
            # TODO: istio side car and heath needs to be added
            _service = Service(
                namespace=_item.metadata.namespace,
                name=_item.metadata.name,
                istio_sidecar=None,
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
        result.extend(self._workload_list('_cronjob', 'CronJob',
                                          namespaces=namespaces, workload_names=workload_names))
        result.extend(self._workload_list('_daemonset', 'DaemonSet',
                                          namespaces=namespaces, workload_names=workload_names))
        result.extend(self._workload_list('_deployment', 'Deployment',
                                          namespaces=namespaces, workload_names=workload_names))
        result.extend(self._workload_list('_deploymentconfig', 'DeploymentConfig',
                                          namespaces=namespaces, workload_names=workload_names))
        # TODO apply Job filters
        result.extend(self._workload_list('_job', 'Job', namespaces=namespaces,
                                          workload_names=workload_names))
        # TODO apply Pod filters
        result.extend(self._workload_list('_pod', 'Pod', namespaces=namespaces,
                                          workload_names=workload_names))
        result.extend(self._workload_list('_replicaset', 'ReplicaSet',
                                          namespaces=namespaces, workload_names=workload_names))
        result.extend(self._workload_list('_replicationcontroller', 'ReplicationController',
                                          namespaces=namespaces, workload_names=workload_names))
        result.extend(self._workload_list('_statefulset', 'StatefulSet',
                                          namespaces=namespaces, workload_names=workload_names))
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
            # TODO: istio side car and labels needs to be added
            _workload = Workload(
                name=_item.metadata.name,
                namespace=_item.metadata.namespace,
                workload_type=workload_type,
                istio_sidecar=None,
                app_label=None,
                version_label=None)
            items.append(_workload)
        # filter by workload name
        if len(workload_names) > 0:
            filtered_list = []
            for _name in workload_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            return set(filtered_list)
        return items

    def delete_istio_config(self, name, namespace, kind, api_version):
        try:
            self._istio_config(kind=kind, api_version=api_version).delete(name=name,
                                                                          namespace=namespace)
        except NotFoundError:
            pass

    def create_istio_config(self, body, namespace, kind, api_version):
        resp = self._istio_config(kind=kind, api_version=api_version).create(body=body,
                                                                             namespace=namespace)
        return resp
