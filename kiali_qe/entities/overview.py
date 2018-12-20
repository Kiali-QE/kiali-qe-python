from kiali_qe.entities import EntityBase


class Overview(EntityBase):

    def __init__(self, overview_type, namespace, items, healthy=0, unhealthy=0, degraded=0, na=0):
        self.overview_type = overview_type
        self.namespace = namespace
        self.items = items
        self.unhealthy = unhealthy
        self.healthy = healthy
        self.degraded = degraded
        self.na = na

    def __str__(self):
        return 'overview_type:{}, namespace:{}, items:{}, \
            healthy:{}, unhealthy:{}, degraded:{}, N/A:{}'.format(
            self.overview_type, self.namespace, self.items,
            self.healthy, self.unhealthy, self.degraded, self.na)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.overview_type), repr(self.namespace), repr(self.items),
            repr(self.healthy), repr(self.unhealthy), repr(self.degraded), repr(self.na))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Overview):
            return False
        if self.overview_type != other.overview_type:
            return False
        if self.namespace != other.namespace:
            return False
        if self.items != other.items:
            return False
        # advanced check
        if advanced_check:
            if self.healthy != other.healthy:
                return False
            if self.unhealthy != other.unhealthy:
                return False
            if self.degraded != other.degraded:
                return False
            if self.na != other.na:
                return False
        return True
