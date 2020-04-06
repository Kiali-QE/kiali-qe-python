from kiali_qe.entities import EntityBase
from kiali_qe.components.enums import MeshWideTLSType


class Overview(EntityBase):

    def __init__(self, overview_type, namespace, items,
                 config_status=None,
                 graph_link=None, apps_link=None, workloads_link=None,
                 services_link=None, configs_link=None,
                 healthy=0, unhealthy=0, degraded=0, na=0,
                 tls_type=MeshWideTLSType.DISABLED,
                 labels={}):
        self.overview_type = overview_type
        self.namespace = namespace
        self.items = items
        self.config_status = config_status
        self.graph_link = graph_link
        self.apps_link = apps_link
        self.workloads_link = workloads_link
        self.services_link = services_link
        self.configs_link = configs_link
        self.unhealthy = unhealthy
        self.healthy = healthy
        self.degraded = degraded
        self.na = na
        self.tls_type = tls_type
        self.labels = labels

    def __str__(self):
        return 'overview_type:{}, namespace:{}, items:{}, \
            healthy:{}, unhealthy:{}, degraded:{}, N/A:{}, TLS:{}'.format(
            self.overview_type, self.namespace, self.items,
            self.healthy, self.unhealthy, self.degraded, self.na,
            self.tls_type)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {}, {})".format(
            type(self).__name__, repr(self.overview_type), repr(self.namespace), repr(self.items),
            repr(self.healthy), repr(self.unhealthy), repr(self.degraded), repr(self.na),
            repr(self.tls_type))

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
            if self.labels != other.labels:
                return False
        return True
