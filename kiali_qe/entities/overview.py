from kiali_qe.entities import EntityBase


class Overview(EntityBase):

    def __init__(self, namespace, applications, healthy=0, unhealthy=0, degraded=0):
        self.namespace = namespace
        self.applications = applications
        self.unhealthy = unhealthy
        self.healthy = healthy
        self.degraded = degraded

    def __str__(self):
        return 'namespace:{}, applications:{}, healthy:{}, unhealthy:{}, degraded:{}'.format(
            self.namespace, self.applications, self.healthy, self.unhealthy, self.degraded)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.namespace), repr(self.applications),
            repr(self.healthy), repr(self.unhealthy), repr(self.degraded))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Overview):
            return False
        if self.namespace != other.namespace:
            return False
        if self.applications != other.applications:
            return False
        # advanced check
        if advanced_check:
            if self.healthy != other.healthy:
                return False
            if self.unhealthy != other.unhealthy:
                return False
            if self.degraded != other.degraded:
                return False
        return True
