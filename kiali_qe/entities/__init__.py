import math
from kiali_qe.components.enums import HealthType


ERROR_RATIO_ABS_TOTAL = 0.09


class EntityBase(object):

    def is_in(self, items):
        for item in items:
            if self.is_equal(item):
                return True
        return False

    def is_equal(self, item):
        raise NotImplementedError('Should be implemented on sub class')

    @classmethod
    def _get_error_ratio(cls, error_ratios):
        _ratio = 0.0
        _rate = 0
        if error_ratios:
            for _ratios in error_ratios.values():
                for _k, _v in _ratios.items():
                    _rate += 1
                    if _k != '200':
                        _ratio += float(_v)
        if _rate != 0:
            return float(_ratio/_rate)
        else:
            return -1/100


class Requests(EntityBase):

    def __init__(self, errorRatio):
        self.errorRatio = errorRatio

    def __str__(self):
        return 'errorRatio:{}'.format(
            self.errorRatio)

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__, repr(self.errorRatio))

    def is_healthy(self):
        if self.errorRatio < 0:
            return HealthType.NA
        if self.errorRatio < 0.001:
            return HealthType.HEALTHY
        elif self.errorRatio >= 0.20:
            return HealthType.FAILURE
        else:
            return HealthType.DEGRADED

    def is_equal(self, other):
        return isinstance(other, Requests)\
         and math.isclose(self.errorRatio,
                          other.errorRatio,
                          abs_tol=ERROR_RATIO_ABS_TOTAL)


class AppRequests(EntityBase):

    def __init__(self, inboundErrorRatio, outboundErrorRatio):
        self.inboundErrorRatio = inboundErrorRatio
        self.outboundErrorRatio = outboundErrorRatio

    def __str__(self):
        return 'inboundErrorRatio:{} outboundErrorRatio:{}'.format(
            self.inboundErrorRatio, self.outboundErrorRatio)

    def __repr__(self):
        return "{}({},{})".format(
            type(self).__name__, repr(self.inboundErrorRatio),
            repr(self.outboundErrorRatio))

    def is_healthy(self):
        if self.inboundErrorRatio == -0.01 and self.outboundErrorRatio == -0.01:
            return HealthType.IDLE
        if self.inboundErrorRatio < 0 and self.outboundErrorRatio < 0:
            return HealthType.NA
        if self.inboundErrorRatio < 0.001 and self.outboundErrorRatio < 0.001:
            return HealthType.HEALTHY
        elif self.inboundErrorRatio >= 0.20 or self.outboundErrorRatio >= 0.20:
            return HealthType.FAILURE
        else:
            return HealthType.DEGRADED

    def is_equal(self, other):
        return isinstance(other, AppRequests)\
            and math.isclose(self.inboundErrorRatio,
                             other.inboundErrorRatio,
                             abs_tol=ERROR_RATIO_ABS_TOTAL)\
            and math.isclose(self.outboundErrorRatio,
                             other.outboundErrorRatio,
                             abs_tol=ERROR_RATIO_ABS_TOTAL)


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

    def is_healthy(self):
        if self.available + self.replicas == 0:
            return HealthType.NA
        elif self.available == self.replicas:
            return HealthType.HEALTHY
        else:
            return HealthType.FAILURE

    def is_equal(self, other):
        return isinstance(other, DeploymentStatus)\
         and self.name == other.name\
         and self.replicas == other.replicas\
         and self.available == other.available


class TrafficItem(EntityBase):

    def __init__(self, status, name, object_type, request_type, rps, success_rate,
                 bound_traffic_type=None):
        self.name = name
        self.status = status
        self.object_type = object_type
        self.request_type = request_type
        self.rps = rps
        self.success_rate = success_rate
        self.bound_traffic_type = bound_traffic_type

    def __str__(self):
        return 'name:{}, object_type: {}, status:{}, request_type:{}, bound_traffic_type{}'.format(
            self.name, self.object_type, self.status, self.request_type, self.bound_traffic_type)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.object_type),
            repr(self.status), repr(self.request_type), repr(self.bound_traffic_type))

    def is_equal(self, other):
        return isinstance(other, TrafficItem)\
         and self.name == other.name\
         and self.object_type == other.object_type\
         and self.status == other.status\
         and self.request_type == other.request_type\
         and self.bound_traffic_type == other.bound_traffic_type


class ConfigurationStatus(EntityBase):

    def __init__(self, validation, link=None):
        self.validation = validation
        self.link = link

    def __str__(self):
        return 'validation:{}, link: {}'.format(
            self.validation, self.link)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__, repr(self.validation), repr(self.link))

    def is_equal(self, other):
        return isinstance(other, ConfigurationStatus)\
         and self.validation == other.validation\
         and self.link == other.link
