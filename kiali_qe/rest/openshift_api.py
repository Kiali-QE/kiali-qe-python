from openshift import client as oclient, config as oconfig
from kubernetes import client as kclient, config as kconfig
from collections import namedtuple

Namespace = namedtuple('Namespace', ['name'])
Service = namedtuple('Service', ['name', 'namespace'])


class OpenshiftAPI(object):
    def __init__(self):
        oconfig.load_kube_config()
        kconfig.load_kube_config()
        self._oapi = oclient.OapiApi()
        self._kapi = kclient.CoreV1Api()

    def list_projects(self):
        """ Returns list of projects """
        items_list = self._oapi.list_project()
        projects = []
        for item in items_list.items:
            projects.append(Namespace(item.metadata.name))
        return projects

    def list_services(self, namespace=None):
        """ Returns list of services

        Args:
            namespace: Namespace of the service, optional
        """
        if namespace:
            items_list = self._kapi.list_namespaced_service(namespace)
        else:
            items_list = self._kapi.list_service_for_all_namespaces()
        services = []
        for item in items_list.items:
            services.append(Service(item.metadata.name, item.metadata.namespace))
        return services
