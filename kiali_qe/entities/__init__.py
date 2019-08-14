from kiali_qe.components.enums import HealthType


class EntityBase(object):

    def is_in(self, items):
        for item in items:
            if self.is_equal(item):
                return True
        return False

    def is_equal(self, item):
        raise NotImplementedError('Should be implemented on sub class')


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
         and self.errorRatio == other.errorRatio


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
        if self.inboundErrorRatio < 0 and self.outboundErrorRatio < 0:
            return HealthType.NA
        if self.inboundErrorRatio < 0.001 and self.outboundErrorRatio < 0.001:
            return HealthType.HEALTHY
        elif self.inboundErrorRatio >= 0.20 or self.outboundErrorRatio >= 0.20:
            return HealthType.FAILURE
        else:
            return HealthType.DEGRADED

    def is_equal(self, other):
        return isinstance(other, Requests)\
         and self.inboundErrorRatio == other.inboundErrorRatio\
         and self.outboundErrorRatio == other.outboundErrorRatio


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
