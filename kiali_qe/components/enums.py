from enum import Enum


class StringEnum(Enum):
    def __init__(self, text):
        self.text = text


class MainMenuEnum(StringEnum):
    GRAPH = ('Graph')
    SERVICES = ('Services')
    ISTIO_CONFIG = ('Istio Config')
    DISTRIBUTED_TRACING = ('Distributed Tracing')


class HelpMenuEnum(StringEnum):
    ABOUT = ('About')


class UserMenuEnum(StringEnum):
    LOGOUT = ('Logout')


class ApplicationVersionEnum(StringEnum):
    KIALI_UI = ("kiali-ui")
    KIALI_CORE = ("kiali")
    ISTIO = ("Istio")
    PROMETHEUS = ("Prometheus")
    KUBERNETES = ("Kubernetes")


class PaginationPerPage(Enum):
    FIVE = 5
    TEN = 10
    FIFTEEN = 15


class GraphPageDuration(StringEnum):
    LAST_MINUTE = ('Last minute')
    LAST_5_MINUTES = ('Last 5 minutes')
    LAST_10_MINUTES = ('Last 10 minutes')
    LAST_30_MINUTES = ('Last 30 minutes')
    LAST_HOUR = ('Last hour')
    LAST_6_HOURS = ('Last 6 hours')
    LAST_12_HOURS = ('Last 12 hours')
    LAST_DAY = ('Last day')
    LAST_7_DAYS = ('Last 7 days')
    LAST_30_DAYS = ('Last 30 days')


class GraphPageLayout(StringEnum):
    COLA = ('Cola')
    COSE = ('Cose')
    DAGRE = ('Dagre')


class GraphPageDisplayFilter(StringEnum):
    LEGEND = ('Legend')
    NODE_LABELS = ('Node Names')
    TRAFFIC_ANIMATION = ('Traffic Animation')


class GraphPageBadgesFilter(StringEnum):
    CIRCUIT_BREAKERS = ('Circuit Breakers')
    VIRTUAL_SERVICES = ('Virtual Services')
    MISSING_SIDECARS = ('Missing Sidecars')


class EdgeLabelsFilter(StringEnum):
    HIDE = ('Hide')
    REQUEST_PER_SECOND = ('Requests per second')
    REQUEST_PERCENT = ('Requests percent of total')
    RESPONSE_TIME = ('Response time 95th percentile')
    SECURITY = ('Security')


class ServicesPageFilter(StringEnum):
    SERVICE_NAME = ('Service Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    NAMESPACE = ('Namespace')


class ServicesPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    SERVICE_NAME = ('Service Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    ERROR_RATE = ('Error Rate')


class ServicesPageRateInterval(StringEnum):
    LAST_1_MINUTE = ('Last 1 minute')
    LAST_5_MINUTES = ('Last 5 minutes')
    LAST_10_MINUTES = ('Last 10 minutes')
    LAST_30_MINUTES = ('Last 30 minutes')


class IstioConfigPageFilter(StringEnum):
    ISTIO_TYPE = ('Istio Type')
    ISTIO_NAME = ('Istio Name')
    CONFIG = ('Config')
    NAMESPACE = ('Namespace')


class IstioConfigPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    ISTIO_NAME = ('Istio Name')


class IstioConfigObjectType(StringEnum):
    DESTINATION_RULE = ('DestinationRule')
    RULE = ('Rule')
    VIRTUAL_SERVICE = ('VirtualService')
    GATEWAY = ('Gateway')
    SERVICE_ENTRY = ('ServiceEntry')
    QUOTA_SPEC = ('QuotaSpec')
    QUOTA_SPEC_BINDING = ('QuotaSpecBinding')


class IstioConfigValidationType(StringEnum):
    VALID = ('Valid')
    NOT_VALID = ('Not Valid')
    NOT_VALIDATED = ('Not Validated')
