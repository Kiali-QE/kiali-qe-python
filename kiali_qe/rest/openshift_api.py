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
    def _deployment(self):
        return self._resource(kind='Deployment')

    def _istio_config(self, kind, api_version):
        return self._resource(kind=kind, api_version=api_version)

    def namespace_list(self):
        """ Returns list of namespaces """
        _response = self._namespace.get()
        namespaces = []
        for _item in _response.items:
            namespaces.append(_item.metadata.name)
        return namespaces

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
        return self._deployment_list(namespaces=namespaces, deployment_names=workload_names)

    def _deployment_list(self, namespaces=[], deployment_names=[]):
        """ Returns list of deployments
        Args:
            namespace: Namespace of the deployment, optional
            deployment_names: Names of the deployments, optional
        """
        items = []
        _raw_items = []
        if len(namespaces) > 0:
            # update items
            for _namespace in namespaces:
                _response = self._deployment.get(namespace=_namespace)
                _raw_items.extend(_response.items)
        else:
            _response = self._deployment.get()
            _raw_items.extend(_response.items)
        for _item in _raw_items:
            # update all the deployments to our custom entity
            # TODO: istio side car and labels needs to be added
            _deployment = Workload(
                name=_item.metadata.name,
                namespace=_item.metadata.namespace,
                workload_type='Deployment',
                istio_sidecar=None,
                app_label=None,
                version_label=None)
            items.append(_deployment)
        # filter by deployment name
        if len(deployment_names) > 0:
            filtered_list = []
            for _name in deployment_names:
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
