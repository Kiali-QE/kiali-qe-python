from kiali_qe.entities import EntityBase, DeploymentStatus, Requests, Envoy
from kiali_qe.components.enums import HealthType


class ApplicationHealth(EntityBase):

    def __init__(self, envoys, deployment_statuses, requests):
        self.envoys = envoys
        self.deployment_statuses = deployment_statuses
        self.requests = requests

    def __str__(self):
        return 'envoys:{}, deployment_statuses:{}, requests:{}'.format(
            self.envoys, self.deployment_statuses, self.requests)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__,
            repr(self.envoys), repr(self.deployment_statuses), repr(self.requests))

    def is_healthy(self):
        if self.envoys_health() == HealthType.NA \
                and self.requests.is_healthy() == HealthType.NA \
                and self.deployment_statuses_health() == HealthType.NA:
            return HealthType.NA
        elif self.envoys_health() == HealthType.FAILURE \
                or self.requests.is_healthy() == HealthType.FAILURE \
                or self.deployment_statuses_health() == HealthType.FAILURE:
            return HealthType.FAILURE
        else:
            return HealthType.HEALTHY

    def envoys_health(self):
        for envoy in self.envoys:
            if envoy.is_healthy() == HealthType.FAILURE:
                return HealthType.FAILURE
            elif envoy.is_healthy() == HealthType.NA:
                return HealthType.NA
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
        if not self.envoys.is_equal(other.envoys):
            return False
        if not self.deployment_statuses.is_equal(other.deployment_statuses):
            return False
        if not self.requests.is_equal(other.requests):
            return False
        return True

    @classmethod
    def get_from_rest(cls, health):
        # update envoys
        _envoy_list = []
        for _e_in_rest in health['envoy']:
            _envoy = Envoy(i_healthy=_e_in_rest['inbound']['healthy'],
                           i_total=_e_in_rest['inbound']['total'],
                           o_healthy=_e_in_rest['outbound']['healthy'],
                           o_total=_e_in_rest['outbound']['total'])
            _envoy_list.append(_envoy)
        # update deployment statuses
        _deployment_status_list = []
        if 'workloadStatuses' in health:
            for _d_in_rest in health['workloadStatuses']:
                deployment_status = DeploymentStatus(
                    name=_d_in_rest['name'],
                    replicas=_d_in_rest['replicas'],
                    available=_d_in_rest['available'])
                _deployment_status_list.append(deployment_status)
            # update requests
        _r_rest = health['requests']
        _requests = Requests(
            errorRatio=_r_rest['errorRatio'])
        return ApplicationHealth(
            envoys=_envoy_list, deployment_statuses=_deployment_status_list, requests=_requests)


class Application(EntityBase):

    def __init__(self, name, namespace, istio_sidecar=None, health=None):
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar
        self.health = health

    def __str__(self):
        return 'name:{}, namespace:{}, sidecar:{}, health:{}'.format(
            self.name, self.namespace, self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace),
            repr(self.istio_sidecar), repr(self.health))

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
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
            if self.health != other.health:
                return False
        return True


class ApplicationDetails(EntityBase):

    def __init__(self, name,
                 istio_sidecar=False, health=None, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.health = health
        self.workloads = kwargs['workloads']\
            if 'workloads' in kwargs else None
        self.services = kwargs['services']\
            if 'services' in kwargs else None

    def __str__(self):
        return 'name:{}, sidecar:{}, health:{}'.format(
            self.name, self.istio_sidecar, self.health)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name),
            repr(self.istio_sidecar), repr(self.health))

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
            if self.istio_sidecar != other.istio_sidecar:
                return False
            if self.health != other.health:
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

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, AppWorkload):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
        return True
