from kiali_qe.entities import EntityBase, Requests
from kiali_qe.components.enums import HealthType
from kiali_qe.utils import is_equal as compare_lists, is_equal


class ServiceHealth(EntityBase):

    def __init__(self, requests):
        self.requests = requests

    def __str__(self):
        return 'requests:{}'.format(self.requests)

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__,
            repr(self.requests))

    def is_healthy(self):
        if not self.requests:
            return HealthType.NA
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
        if not self.requests.is_equal(other.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update requests
        _r_rest = health['requests']
        _requests = Requests(
            errorRatio=cls._get_error_ratio(_r_rest['inbound']))
        return ServiceHealth(requests=_requests)


class Service(EntityBase):
    """
    Service class provides information details on Services list page.

    Args:
        name: name of the service
        namespace: namespace where service is located
        istio_sidecar: Is istio side car available
        labels: labels
        health: health status
    """

    def __init__(self, name, namespace, istio_sidecar=None,
                 labels={}, health=None,
                 service_status=None,
                 config_status=None,
                 icon=None):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        if namespace is None:
            raise KeyError("'namespace' should not be 'None'")
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar
        self.labels = labels
        self.health = health
        self.service_status = service_status
        self.config_status = config_status
        self.icon = icon

    def __str__(self):
        return 'name:{}, namespace:{}, istio_sidecar:{}, labels:{}, '\
            'health:{}'.format(
                self.name, self.namespace, self.istio_sidecar,
                self.labels, self.health)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.namespace),
            repr(self.istio_sidecar), repr(self.labels), repr(self.health))

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
        # if self.istio_sidecar != other.istio_sidecar:
        #    return False
        if self.health != other.health:
            return False
        if self.labels != other.labels:
            return False
        if self.service_status and other.service_status and \
                not self.service_status.is_equal(other.service_status):
            return False
        if self.icon != other.icon:
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

    def __init__(self, name, created_at, created_at_ui, service_type,
                 resource_version, ip, ports,
                 labels={}, selectors={},
                 istio_sidecar=False, health=None, service_status=None,
                 endpoints=[],
                 validations=[], icon=None, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.created_at = created_at
        self.created_at_ui = created_at_ui
        self.service_type = service_type
        self.resource_version = resource_version
        self.ip = ip
        self.ports = ports
        self.labels = labels
        self.selectors = selectors
        self.service_status = service_status
        self.endpoints = endpoints
        self.validations = validations
        self.icon = icon
        self.workloads_number = kwargs['workloads_number']\
            if 'workloads_number' in kwargs else None
        self.istio_configs_number = kwargs['istio_configs_number']\
            if 'istio_configs_number' in kwargs else None
        self.istio_configs = kwargs['istio_configs']\
            if 'istio_configs' in kwargs else None
        self.virtual_services = kwargs['virtual_services']\
            if 'virtual_services' in kwargs else None
        self.destination_rules = kwargs['destination_rules']\
            if 'destination_rules' in kwargs else None
        self.workloads = kwargs['workloads']\
            if 'workloads' in kwargs else None
        self.traffic_tab = kwargs['traffic_tab']\
            if 'traffic_tab' in kwargs else None
        self.inbound_metrics = kwargs['inbound_metrics']\
            if 'inbound_metrics' in kwargs else None
        self.traces_tab = kwargs['traces_tab']\
            if 'traces_tab' in kwargs else None

    def __str__(self):
        return 'name:{}, created_at: {}, service_type: {}, resource_version: {}, \
        ip: {}, endpoints: {}, ports: {}, \
        istio_sidecar:{}, health:{}, labels:{}, selectors:{}, service_status: {}'.format(
            self.name, self.created_at,
            self.service_type, self.resource_version,
            self.ip, self.endpoints, self.ports,
            self.istio_sidecar, self.health, self.labels, self.selectors,
            self.service_status)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.istio_sidecar), repr(self.health),
            repr(self.labels), repr(self.selectors))

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
        if self.created_at_ui != other.created_at_ui:
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
        if not is_equal(self.endpoints, other.endpoints):
            return False
        # https://github.com/kiali/kiali/issues/1382
        # if self.selectors != other.selectors:
        #    return False
        # advanced check
        if not advanced_check:
            return True
        # if self.istio_sidecar != other.istio_sidecar:
        #    return False
        if self.health != other.health:
            return False
        if self.service_status and other.service_status and \
                not self.service_status.is_equal(other.service_status):
            return False
        if self.icon != other.icon:
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

    def __init__(self, status, name, created_at, created_at_ui,
                 resource_version,
                 protocol_route=None, hosts=[], weights=[], gateways=[]):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.created_at = created_at
        self.created_at_ui = created_at_ui
        self.resource_version = resource_version
        self.status = status
        self.protocol_route = protocol_route
        self.hosts = hosts
        self.weights = weights
        self.gateways = gateways

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
        if self.created_at_ui != other.created_at_ui:
            return False
        if self.resource_version != other.resource_version:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        if self.protocol_route != other.protocol_route:
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


class VirtualServiceGateway(EntityBase):
    """
    Service class provides information details on Gateway of VS Overview.

    """

    def __init__(self, text, link=None):
        if text is None:
            raise KeyError("'text' should not be 'None'")
        self.text = text
        self.link = link

    def __str__(self):
        return 'text:{}, link:{}'.format(
            self.text, self.link)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__,
            repr(self.text),
            repr(self.link))

    def __hash__(self):
        return (hash(self.text))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, VirtualServiceGateway):
            return False
        if self.text != other.text:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.link != other.link:
            return False
        return True


class VirtualServiceOverview(EntityBase):
    """
    Service class provides information details on VirtualService Overview.

    Args:
        hosts: references to hosts
        gateways: references to gateways
        validation_references: references to other VS objects having conflicts with
    """

    def __init__(self, name, status=None, hosts=[], gateways=[], validation_references=[]):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.status = status
        self.hosts = hosts
        self.gateways = gateways
        self.validation_references = validation_references

    def __str__(self):
        return 'name:{}, status:{}, '\
            'resource_version:{}, hosts:{}, weights:{}'.format(
                self.name, self.status,
                self.hosts, self.gateways, self.validation_references)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name),
            repr(self.status),
            repr(self.hosts), repr(self.gateways), repr(self.validation_references))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.hosts) ^ hash(self.gateways))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, VirtualServiceOverview):
            return False
        if self.name != other.name:
            return False
        if not compare_lists(self.hosts, other.hosts):
            return False
        if not compare_lists(self.gateways, other.gateways):
            return False
        if not compare_lists(self.validation_references, other.validation_references):
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        return True


class DestinationRuleOverview(EntityBase):
    """
    Service class provides information details on DestinationRule Overview.

    Args:
        status: the validation status of DR
        name: name of the destination rule
        host: the host of destination rule
        subsets: subsets as a plain text
    """

    def __init__(self, status, name, host, subsets):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.host = host
        self.subsets = subsets
        self.status = status

    def __str__(self):
        return 'name:{}, status:{}, host:{}, subsets:{}, '\
            'created_at:{}, resource_version:{}'.format(
                self.name, self.status, self.host,
                self.subsets)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.status),
            repr(self.host),
            repr(self.subsets))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.host))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, DestinationRuleOverview):
            return False
        if self.name != other.name:
            return False
        if self.host != other.host:
            return False
        if self.subsets != other.subsets:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        return True


class DestinationRuleSubset(EntityBase):
    """
    Service class provides information details on Subsets of DR Overview.

    """

    def __init__(self, name, status=None, labels={}, traffic_policy=None):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.traffic_policy = traffic_policy
        self.status = status
        self.labels = labels

    def __str__(self):
        return 'status:{}, name:{}, labels:{}, traffic_policy:{}'.format(
            self.status, self.name, self.labels, self.traffic_policy)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.status),
            repr(self.name), repr(self.labels),
            repr(self.traffic_policy))

    def __hash__(self):
        return (hash(self.name))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, DestinationRuleSubset):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if not advanced_check:
            return True
        if self.status != other.status:
            return False
        if self.labels != other.labels:
            return False
        if self.traffic_policy != other.traffic_policy:
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

    def __init__(self, status, name, host, traffic_policy, subsets,
                 created_at, created_at_ui, resource_version):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.host = host
        self.traffic_policy = traffic_policy
        self.subsets = subsets
        self.created_at = created_at
        self.created_at_ui = created_at_ui
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
        if self.created_at_ui != other.created_at_ui:
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


class IstioConfigRow(EntityBase):
    """
    Service class provides information details on Istio Config of Service/Workload Details.

    Args:
        status: the validation status of config
        name: name of the config
        type: the config type
        created_at: creation datetime
        resource_version: resource version
    """

    def __init__(self, status, name, type,
                 created_at, created_at_ui, resource_version):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.type = type
        self.created_at = created_at
        self.created_at_ui = created_at_ui
        self.resource_version = resource_version
        self.status = status

    def __str__(self):
        return 'name:{}, status:{}, type:{}, '\
            'created_at:{}, resource_version:{}'.format(
                self.name, self.status, self.type,
                self.created_at, self.resource_version)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.status),
            repr(self.host),
            repr(self.traffic_policy), repr(self.subsets),
            repr(self.created_at), repr(self.resource_version))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.type) ^ hash(self.created_at)
                ^ hash(self.resource_version))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, DestinationRule):
            return False
        if self.name != other.name:
            return False
        if self.type != other.type:
            return False
        if self.created_at != other.created_at:
            return False
        if self.created_at_ui != other.created_at_ui:
            return False
        if self.resource_version != other.resource_version:
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
