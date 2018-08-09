from kiali_qe.entities import EntityBase


class Envoy(EntityBase):

    def __init__(self, i_healthy, i_total, o_healthy, o_total):
        self.i_healthy = i_healthy
        self.i_total = i_total
        self.o_healthy = o_healthy
        self.o_total = o_total

    def __str__(self):
        return 'inbound (healthy:{}, total:{}), outbound (healthy:{}, total:{})'.format(
            self.i_healthy, self.i_total, self.o_healthy, self.o_total)

    def __repr__(self):
        return "{}({}, {})({}, {})".format(type(self).__name__,
                                           repr(self.i_healthy),
                                           repr(self.i_total),
                                           repr(self.o_healthy),
                                           repr(self.o_total))

    def is_equal(self, other):
        return isinstance(other, Envoy)\
         and self.i_healthy == other.i_healthy and self.i_total == other.i_total\
         and self.o_healthy == other.o_healthy and self.o_total == other.o_total


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

    def is_equal(self, other):
        return isinstance(other, DeploymentStatus)\
         and self.name == other.name\
         and self.replicas == other.replicas\
         and self.available == other.available


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

    def is_equal(self, other):
        return isinstance(other, Requests)\
         and self.request_count == other.request_count\
         and self.request_error_count == other.request_error_count


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

    def is_equal(self, other):
        if not isinstance(other, Health):
            return False
        if not self.envoy.is_equal(other.envoy):
            return False
        if not self.deployment_statuses.is_equal(other.deployment_statuses):
            return False
        if not self.requests.is_equal(other.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update envoy
        _e_in_rest = health['envoy']
        _envoy = Envoy(i_healthy=_e_in_rest['inbound']['healthy'],
                       i_total=_e_in_rest['inbound']['total'],
                       o_healthy=_e_in_rest['outbound']['healthy'],
                       o_total=_e_in_rest['outbound']['total'])
        # update deployment statuses
        _deployment_status_list = []
        if 'deploymentStatuses' in health:
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

    def __hash__(self):
        return (hash(self.name) ^ hash(self.namespace) ^ hash(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Service):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.istio_sidecar != other.istio_sidecar:
            return False
        if not self.health.is_equal(other.health):
            return False
        return True


class ServiceDetails(object):
    """
    Service class provides information details on Service details page.

    Args:
        name: name of the service
        istio_sidecar: Is istio side car available
        health: health status
    """

    def __init__(self, name, istio_sidecar=False, health=None, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.virtual_services_number = kwargs['virtual_services_number']\
            if 'virtual_services_number' in kwargs else None
        self.destination_rules_number = kwargs['destination_rules_number']\
            if 'destination_rules_number' in kwargs else None
        self.virtual_services = kwargs['virtual_services']\
            if 'virtual_services' in kwargs else None
        self.destination_rules = kwargs['destination_rules']\
            if 'destination_rules' in kwargs else None

    def __str__(self):
        return 'name:{}, istio_sidecar:{}, health:{}'.format(
            self.name, self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.istio_sidecar), repr(self.health))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, ServiceDetails):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.istio_sidecar != other.istio_sidecar:
            return False
        if not self.health.is_equal(other.health):
            return False
        return True


class VirtualService(object):
    """
    Service class provides information details on VirtualService of Service Details.

    Args:
        name: name of the virtual service
        created_at: creation datetime
        resource_version: resource version
    """

    def __init__(self, name, created_at, resource_version):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.created_at = created_at
        self.resource_version = resource_version

    def __str__(self):
        return 'name:{}, created_at:{}, resource_version:{}'.format(
            self.name, self.created_at, self.resource_version)

    def __repr__(self):
        return "{}({}, {}".format(
            type(self).__name__,
            repr(self.name), repr(self.created_at), repr(self.resource_version))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.created_at) ^ hash(self.resource_version))

    def __eq__(self, other):
        return self.is_equal(advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, VirtualService):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.created_at != other.created_at:
            return False
        if self.resource_version != other.resource_version:
            return False
        return True


class DestinationRule(object):
    """
    Service class provides information details on DestinationRule of Service Details.

    Args:
        name: name of the virtual service
        host: the host of destination rule
        created_at: creation datetime
        resource_version: resource version
    """

    def __init__(self, name, host, created_at, resource_version):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.host = host
        self.created_at = created_at
        self.resource_version = resource_version

    def __str__(self):
        return 'name:{}, host:{}, created_at:{}, resource_version:{}'.format(
            self.name, self.host, self.created_at, self.resource_version)

    def __repr__(self):
        return "{}({}, {}".format(
            type(self).__name__,
            repr(self.name), repr(self.host), repr(self.created_at), repr(self.resource_version))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.host) ^ hash(self.created_at)
                ^ hash(self.resource_version))

    def __eq__(self, other):
        return self.is_equal(advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, DestinationRule):
            return False
        if self.name != other.name:
            return False
        if self.host != other.host:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.created_at != other.created_at:
            return False
        if self.resource_version != other.resource_version:
            return False
        return True
