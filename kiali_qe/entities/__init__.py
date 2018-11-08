from kiali_qe.components.enums import HealthType


class EntityBase(object):

    def is_in(self, items):
        for item in items:
            if self.is_equal(item):
                return True
        return False

    def is_equal(self, item):
        raise NotImplemented('Should be implemented on sub class')


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

    def is_healthy(self):
        if self.i_total + self.o_total == 0:
            return HealthType.NA
        elif self.i_total + self.o_total == self.i_healthy + self.o_healthy:
            return HealthType.HEALTHY
        else:
            return HealthType.FAILURE

    def is_equal(self, other):
        return isinstance(other, Envoy)\
         and self.i_healthy == other.i_healthy and self.i_total == other.i_total\
         and self.o_healthy == other.o_healthy and self.o_total == other.o_total


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
         and self.request_count == other.request_count\
         and self.request_error_count == other.request_error_count


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
        if self.replicas + self.replicas == 0:
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
