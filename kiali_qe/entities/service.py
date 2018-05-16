from kiali_qe.entities import EntityBase


class Envoy(EntityBase):

    def __init__(self, healthy, total):
        self.healthy = healthy
        self.total = total

    def __str__(self):
        return 'healthy:{}, total:{}'.format(self.healthy, self.total)

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.healthy), repr(self.total))

    def is_equal(self, item):
        return self.healthy == item.healthy and self.total == item.total


class DeploymentStatus(EntityBase):

    def __init__(self, name, replicas, available):
        self.name = name
        self.replicas = replicas
        self.available = available

    def __str__(self):
        return 'name:{}, replicas:{}, available:{}'.format(
            self.name, self.replicas, self.available)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.replicas), repr(self.available))

    def is_equal(self, item):
        return self.name == item.name and self.replicas == item.replicas\
         and self.available == item.available


class Requests(EntityBase):

    def __init__(self, request_count, request_error_count):
        self.request_count = request_count
        self.request_error_count = request_error_count

    def __str__(self):
        return 'request_count:{}, request_error_count:{}'.format(
            self.request_count, self.request_error_count)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, repr(self.request_count), repr(self.request_error_count))

    def is_equal(self, item):
        return self.request_count == item.request_count\
         and self.request_error_count == item.request_error_count


class Health(EntityBase):

    def __init__(self, envoy, deployment_statuses, requests):
        self.envoy = envoy
        self.deployment_statuses = deployment_statuses
        self.requests = requests

    def __str__(self):
        return 'envoy:{}, deployment_statuses:{}, requests:{}'.format(
            self.envoy, self.deployment_statuses, self.requests)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__,
            repr(self.envoy), repr(self.deployment_statuses), repr(self.requests))

    def is_equal(self, item):
        if not self.envoy.is_equal(item.envoy):
            return False
        if not self.deployment_statuses.is_equal(item.deployment_statuses):
            return False
        if not self.requests.is_equal(item.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update envoy
        _e_in_rest = health['envoy']
        _envoy = Envoy(healthy=_e_in_rest['healthy'], total=_e_in_rest['total'])
        # update deployment statuses
        _deployment_status_list = []
        for _d_in_rest in health['deploymentStatuses']:
            deployment_status = DeploymentStatus(
                name=_d_in_rest['name'],
                replicas=_d_in_rest['replicas'],
                available=_d_in_rest['available'])
            _deployment_status_list.append(deployment_status)
        # update requests
        _r_rest = health['requests']
        _requests = Requests(
            request_count=_r_rest['requestCount'],
            request_error_count=_r_rest['requestErrorCount'])
        return Health(
            envoy=_envoy, deployment_statuses=_deployment_status_list, requests=_requests)


class Service(object):
    """
    Service class provides information details on Services list page.

    Args:
        name: name of the service
        namespace: namespace where service is located
        istio_sidecar: Is istio side car available
        health: health status
    """

    def __init__(self, name, namespace, istio_sidecar=False, health=None):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        if namespace is None:
            raise KeyError("'namespace' should not be 'None'")
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar
        self.health = health

    def __str__(self):
        return 'name:{}, namespace:{}, istio_sidecar:{}, health:{}'.format(
            self.name, self.namespace, self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.namespace), repr(self.istio_sidecar), repr(self.health))

    def is_equal(self, item):
        if self.name != item.name:
            return False
        if self.namespace != item.namespace:
            return False
        if self.istio_sidecar != item.istio_sidecar:
            return False
        if not self.health.is_equal(item.health):
            return False
        return True
