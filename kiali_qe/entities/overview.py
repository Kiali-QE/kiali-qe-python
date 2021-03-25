from kiali_qe.entities import EntityBase
from kiali_qe.components.enums import MeshWideTLSType


class Overview(EntityBase):

    def __init__(self, overview_type, namespace, items,
                 config_status=None,
                 healthy=0, unhealthy=0, degraded=0, na=0, idle=0,
                 tls_type=MeshWideTLSType.DISABLED,
                 labels={}):
        self.overview_type = overview_type
        self.namespace = namespace
        self.items = items
        self.config_status = config_status
        self.unhealthy = unhealthy
        self.healthy = healthy
        self.degraded = degraded
        self.na = na
        self.idle = idle
        self.tls_type = tls_type
        self.labels = labels

    def __str__(self):
        return 'overview_type:{}, namespace:{}, items:{}, \
            healthy:{}, unhealthy:{}, degraded:{}, N/A:{}, Idle:{}, TLS:{}'.format(
            self.overview_type, self.namespace, self.items,
            self.healthy, self.unhealthy, self.degraded, self.na, self.idle,
            self.tls_type)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.overview_type), repr(self.namespace), repr(self.items),
            repr(self.healthy), repr(self.unhealthy), repr(self.degraded), repr(self.na),
            repr(self.idle),
            repr(self.tls_type))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def __hash__(self):
        return (hash(self.namespace) ^ hash(self.overview_type))

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
            # @TODO performance issue between UI and REST
            '''if self.healthy != other.healthy:
                return False
            if self.unhealthy != other.unhealthy:
                return False
            if self.degraded != other.degraded:
                return False
            if self.na != other.na:
                return False
            if self.idle != other.idle:
                return False'''
            if self.labels != other.labels:
                return False
        return True
