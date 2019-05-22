from kiali_qe.entities import EntityBase, DeploymentStatus, Requests
from kiali_qe.components.enums import HealthType
from kiali_qe.utils import is_equal as compare_lists


class ServiceHealth(EntityBase):

    def __init__(self, deployment_statuses, requests):
        self.deployment_statuses = deployment_statuses
        self.requests = requests

    def __str__(self):
        return 'deployment_statuses:{}, requests:{}'.format(
            self.deployment_statuses, self.requests)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__,
            repr(self.deployment_statuses), repr(self.requests))

    def is_healthy(self):
        if self.requests.is_healthy() == HealthType.NA:
            return HealthType.NA
        elif self.requests.is_healthy() == HealthType.FAILURE:
            return HealthType.FAILURE
        elif self.requests.is_healthy() == HealthType.DEGRADED:
            return HealthType.DEGRADED
        else:
            return HealthType.HEALTHY

    def is_equal(self, other):
        if not isinstance(other, ServiceHealth):
            return False
        if not self.deployment_statuses.is_equal(other.deployment_statuses):
            return False
        if not self.requests.is_equal(other.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update deployment statuses
        _deployment_status_list = []
        if 'deploymentStatuses' in health:
            for _d_in_rest in health['deploymentStatuses']:
                deployment_status = DeploymentStatus(
                    name=_d_in_rest['name'],
                    replicas=_d_in_rest['desiredReplicas'],
                    available=_d_in_rest['availableReplicas'])
                _deployment_status_list.append(deployment_status)
            # update requests
        _r_rest = health['requests']
        _requests = Requests(
            errorRatio=_r_rest['errorRatio'])
        return ServiceHealth(
            deployment_statuses=_deployment_status_list, requests=_requests)


class Service(EntityBase):
    """
    Service class provides information details on Services list page.

    Args:
        name: name of the service
        namespace: namespace where service is located
        istio_sidecar: Is istio side car available
        app_label: App label
        version_label: version label
        health: health status
    """

    def __init__(self, name, namespace, istio_sidecar=None,
                 app_label=None, version_label=None, health=None):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        if namespace is None:
            raise KeyError("'namespace' should not be 'None'")
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar
        self.app_label = app_label
        self.version_label = version_label
        self.health = health

    def __str__(self):
        return 'name:{}, namespace:{}, istio_sidecar:{}, app_label:{}, '\
            'version_label:{}, health:{}'.format(
                self.name, self.namespace, self.istio_sidecar,
                self.app_label, self.version_label, self.health)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.namespace),
            repr(self.istio_sidecar), repr(self.app_label),
            repr(self.version_label), repr(self.health))

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
                 resource_version, ip, ports, labels={},
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
        self.labels = labels
        self.workloads_number = kwargs['workloads_number']\
            if 'workloads_number' in kwargs else None
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
        self.traffic = kwargs['traffic']\
            if 'traffic' in kwargs else None
        self.inbound_metrics = kwargs['inbound_metrics']\
            if 'inbound_metrics' in kwargs else None

    def __str__(self):
        return 'name:{}, created_at: {}, service_type: {}, resource_version: {}, \
        ip: {}, ports: {}, istio_sidecar:{}, health:{}, labels:{}'.format(
            self.name, self.created_at,
            self.service_type, self.resource_version,
            self.ip, self.ports,
            self.istio_sidecar, self.health, self.labels)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.istio_sidecar), repr(self.health),
            repr(self.labels))

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
        if self.labels != other.labels:
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
        status: the validation status of VS
        name: name of the virtual service
        created_at: creation datetime
        resource_version: resource version
    """

    def __init__(self, status, name, created_at, resource_version, hosts=[], weights=[]):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.created_at = created_at
        self.resource_version = resource_version
        self.status = status
        self.hosts = hosts
        self.weights = weights

    def __str__(self):
        return 'name:{}, status:{}, created_at:{}, '\
            'resource_version:{}, hosts:{}, weights:{}'.format(
                self.name, self.status, self.created_at, self.resource_version,
                self.hosts, self.weights)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name),
            repr(self.status),
            repr(self.created_at), repr(self.resource_version),
            repr(self.hosts), repr(self.weights))

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
        if self.created_at != other.created_at:
            return False
        if self.resource_version != other.resource_version:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        if not compare_lists(self.hosts, other.hosts):
            return False
        if not compare_lists(self.weights, other.weights):
            return False
        return True


class VirtualServiceWeight(EntityBase):
    """
    Service class provides information details on VirtualServiceWeight of VS Overview.

    """

    def __init__(self, host, subset=None, port=None, status=None, weight=None):
        if host is None:
            raise KeyError("'host' should not be 'None'")
        self.host = host
        self.subset = subset
        self.port = port
        self.status = status
        self.weight = weight

    def __str__(self):
        return 'host:{}, status:{}, subset:{}, port:{}, weight:{}'.format(
            self.host, self.status, self.subset, self.port, self.weight)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.host),
            repr(self.status),
            repr(self.subset), repr(self.port),
            repr(self.weight))

    def __hash__(self):
        return (hash(self.host) ^ hash(self.subset))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, VirtualServiceWeight):
            return False
        if self.host != other.host:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        if self.subset != other.subset:
            return False
        if self.port != other.port:
            return False
        if self.weight != other.weight:
            return False
        return True


class DestinationRule(EntityBase):
    """
    Service class provides information details on DestinationRule of Service Details.

    Args:
        status: the validation status of DR
        name: name of the destination rule
        host: the host of destination rule
        traffic_policy: traffic policy as a text
        subsets: subsets as a plain text
        created_at: creation datetime
        resource_version: resource version
    """

    def __init__(self, status, name, host, traffic_policy, subsets, created_at, resource_version):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.host = host
        self.traffic_policy = traffic_policy
        self.subsets = subsets
        self.created_at = created_at
        self.resource_version = resource_version
        self.status = status

    def __str__(self):
        return 'name:{}, status:{}, host:{}, traffic_policy:{}, subsets:{}, '\
            'created_at:{}, resource_version:{}'.format(
                self.name, self.status, self.host,
                self.traffic_policy, self.subsets,
                self.created_at, self.resource_version)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.status),
            repr(self.host),
            repr(self.traffic_policy), repr(self.subsets),
            repr(self.created_at), repr(self.resource_version))

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
        if self.created_at != other.created_at:
            return False
        if self.resource_version != other.resource_version:
            return False
        if self.traffic_policy != other.traffic_policy:
            return False
        if self.subsets != other.subsets:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
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
