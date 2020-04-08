from kiali_qe.entities import EntityBase, DeploymentStatus, AppRequests
from kiali_qe.components.enums import HealthType
from kiali_qe.utils import is_equal


class ApplicationHealth(EntityBase):

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
        if self.requests.is_healthy() == HealthType.NA \
                and self.deployment_statuses_health() == HealthType.NA:
            return HealthType.NA
        elif self.requests.is_healthy() == HealthType.FAILURE \
                or self.deployment_statuses_health() == HealthType.FAILURE:
            return HealthType.FAILURE
        elif self.requests.is_healthy() == HealthType.DEGRADED:
            return HealthType.DEGRADED
        else:
            return HealthType.HEALTHY

    def deployment_statuses_health(self):
        for deployment_status in self.deployment_statuses:
            if deployment_status.is_healthy() == HealthType.FAILURE:
                return HealthType.FAILURE
            elif deployment_status.is_healthy() == HealthType.NA:
                # if app is not deployed, it is not healthy
                return HealthType.FAILURE
        return HealthType.HEALTHY

    def is_equal(self, other):
        if not isinstance(other, ApplicationHealth):
            return False
        if not is_equal(self.deployment_statuses, other.deployment_statuses):
            return False
        if not self.requests.is_equal(other.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update deployment statuses
        _deployment_status_list = []
        if 'workloadStatuses' in health:
            for _d_in_rest in health['workloadStatuses']:
                deployment_status = DeploymentStatus(
                    name=_d_in_rest['name'],
                    replicas=_d_in_rest['desiredReplicas'],
                    available=_d_in_rest['availableReplicas'])
                _deployment_status_list.append(deployment_status)
            # update requests
        _r_rest = health['requests']
        _requests = AppRequests(
            inboundErrorRatio=cls._get_error_ratio(_r_rest['inboundErrorRatio']),
            outboundErrorRatio=cls._get_error_ratio(_r_rest['outboundErrorRatio']))
        return ApplicationHealth(
            deployment_statuses=_deployment_status_list, requests=_requests)

    @classmethod
    def _get_error_ratio(cls, error_ratio):
        if error_ratio != -1:
            return float(error_ratio)
        return float(error_ratio / 100)


class Application(EntityBase):

    def __init__(self, name, namespace, istio_sidecar=None, health=None,
                 application_status=None, labels={}):
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.application_status = application_status
        self.labels = labels

    def __str__(self):
        return 'name:{}, namespace:{}, sidecar:{}, health:{}, labels:{}'.format(
            self.name, self.namespace, self.istio_sidecar, self.health, self.labels)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace),
            repr(self.istio_sidecar), repr(self.health), repr(self.labels))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.namespace) ^ hash(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Application):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        # if self.istio_sidecar != other.istio_sidecar:
        #    return False
        # advanced check
        if advanced_check:
            if self.health != other.health:
                return False
            if self.labels != other.labels:
                return False
            # TODO in case of unstable env pods can recreate
            # if self.application_status and other.application_status and \
            #         not self.application_status.is_equal(other.application_status):
            #     return False
        return True


class ApplicationDetails(EntityBase):

    def __init__(self, name,
                 istio_sidecar=False, health=None, application_status=None, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.application_status = application_status
        self.workloads = kwargs['workloads']\
            if 'workloads' in kwargs else None
        self.services = kwargs['services']\
            if 'services' in kwargs else None
        self.traffic_tab = kwargs['traffic_tab']\
            if 'traffic_tab' in kwargs else None
        self.inbound_metrics = kwargs['inbound_metrics']\
            if 'inbound_metrics' in kwargs else None
        self.outbound_metrics = kwargs['outbound_metrics']\
            if 'outbound_metrics' in kwargs else None

    def __str__(self):
        return 'name:{}, sidecar:{}, health:{}'.format(
            self.name, self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name),
            repr(self.istio_sidecar), repr(self.health))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, ApplicationDetails):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if advanced_check:
            # if self.istio_sidecar != other.istio_sidecar:
            #    return False
            if self.health != other.health:
                return False
            if self.application_status and \
                    not self.application_status.is_equal(other.application_status):
                return False
        return True


class AppWorkload(EntityBase):

    def __init__(self, name, istio_sidecar=False):
        self.name = name
        self.istio_sidecar = istio_sidecar

    def __str__(self):
        return 'name:{}, istio_sidecar:{}'.format(
            self.name, self.istio_sidecar)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, repr(self.name),
            repr(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other)

    def __hash__(self):
        return (hash(self.name) ^ hash(self.istio_sidecar))

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, AppWorkload):
            return False
        if self.name != other.name:
            return False
        # if self.istio_sidecar != other.istio_sidecar:
        #    return False
        return True
