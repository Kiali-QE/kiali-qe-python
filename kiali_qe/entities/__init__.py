from kiali_qe.components.enums import HealthType


class EntityBase(object):

    def is_in(self, items):
        for item in items:
            if self.is_equal(item):
                return True
        return False

    def is_equal(self, item):
        raise NotImplemented('Should be implemented on sub class')


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

    def is_healthy(self):
        if self.request_count + self.request_error_count == 0:
            return HealthType.NA
        elif self.request_count > self.request_error_count:
            return HealthType.HEALTHY
        else:
            return HealthType.FAILURE

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
