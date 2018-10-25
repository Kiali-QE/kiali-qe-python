from kiali_qe.entities import EntityBase, DeploymentStatus, Requests, Envoy
from kiali_qe.components.enums import HealthType


class ServiceHealth(EntityBase):

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

    def is_healthy(self):
        if self.envoy.is_healthy() == HealthType.NA \
                and self.requests.is_healthy() == HealthType.NA:
            return HealthType.NA
        elif self.envoy.is_healthy() == HealthType.FAILURE \
                or self.requests.is_healthy() == HealthType.FAILURE:
            return HealthType.FAILURE
        else:
            return HealthType.HEALTHY

    def is_equal(self, other):
        if not isinstance(other, ServiceHealth):
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
            errorRatio=_r_rest['errorRatio'])
        return ServiceHealth(
            envoy=_envoy, deployment_statuses=_deployment_status_list, requests=_requests)


class Service(EntityBase):
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
        return self.is_equal(other, advanced_check=True)

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
        if self.health != other.health:
            return False
        return True


class ServiceDetails(EntityBase):
    """
    Service class provides information details on Service details page.

    Args:
        name: name of the service
        istio_sidecar: Is istio side car available
        health: health status
    """

    def __init__(self, name, created_at, service_type,
                 resource_version, ip, ports,
                 istio_sidecar=False, health=None, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.created_at = created_at
        self.service_type = service_type
        self.resource_version = resource_version
        self.ip = ip
        self.ports = ports
        self.workloads_number = kwargs['workloads_number']\
            if 'workloads_number' in kwargs else None
        self.source_workloads_number = kwargs['source_workloads_number']\
            if 'source_workloads_number' in kwargs else None
        self.virtual_services_number = kwargs['virtual_services_number']\
            if 'virtual_services_number' in kwargs else None
        self.destination_rules_number = kwargs['destination_rules_number']\
            if 'destination_rules_number' in kwargs else None
        self.virtual_services = kwargs['virtual_services']\
            if 'virtual_services' in kwargs else None
        self.destination_rules = kwargs['destination_rules']\
            if 'destination_rules' in kwargs else None
        self.workloads = kwargs['workloads']\
            if 'workloads' in kwargs else None
        self.source_workloads = kwargs['source_workloads']\
            if 'source_workloads' in kwargs else None

    def __str__(self):
        return 'name:{}, created_at: {}, service_type: {}, resource_version: {}, \
        ip: {}, ports: {}, istio_sidecar:{}, health:{}'.format(
            self.name, self.created_at,
            self.service_type, self.resource_version,
            self.ip, self.ports,
            self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.istio_sidecar), repr(self.health))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, ServiceDetails):
            return False
        if self.name != other.name:
            return False
        if self.created_at != other.created_at:
            return False
        if self.service_type != other.service_type:
            return False
        if self.resource_version != other.resource_version:
            return False
        if self.ip != other.ip:
            return False
        if self.ports != other.ports:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.istio_sidecar != other.istio_sidecar:
            return False
        if self.health != other.health:
            return False
        return True


class VirtualService(EntityBase):
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
        return self.is_equal(other, advanced_check=True)

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


class DestinationRule(EntityBase):
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
        return self.is_equal(other, advanced_check=True)

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


class SourceWorkload(EntityBase):
    """
    Service class provides information details on SourceWorkloads of Service Details.

    Args:
        to: workload destination
        workloads: list of workload names
    """

    def __init__(self, to, workloads):
        if to is None:
            raise KeyError("'to' should not be 'None'")
        self.to = to
        self.workloads = workloads

    def __str__(self):
        return 'to:{}, workloads:{}'.format(
            self.to, self.workloads)

    def __repr__(self):
        return "{}({}, {}".format(
            type(self).__name__,
            repr(self.to), repr(self.workloads))

    def __hash__(self):
        return (hash(self.to) ^ hash(self.workloads))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, SourceWorkload):
            return False
        if self.to != other.to:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.workloads != other.workloads:
            return False
        return True
