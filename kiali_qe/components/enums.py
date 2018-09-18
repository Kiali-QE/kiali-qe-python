from enum import Enum


class StringEnum(Enum):
    def __init__(self, text):
        self.text = text


class MainMenuEnum(StringEnum):
    GRAPH = ('Graph')
    APPLICATIONS = ('Applications')
    WORKLOADS = ('Workloads')
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
    LAST_3_HOURS = ('Last 3 hours')
    LAST_6_HOURS = ('Last 6 hours')
    LAST_12_HOURS = ('Last 12 hours')
    LAST_DAY = ('Last day')
    LAST_7_DAYS = ('Last 7 days')
    LAST_30_DAYS = ('Last 30 days')


class GraphRefreshInterval(StringEnum):
    PAUSE = ('Pause')
    IN_5_SECONDS = ('5 seconds')
    IN_10_SECONDS = ('10 seconds')
    IN_15_SECONDS = ('15 seconds')
    IN_30_SECONDS = ('30 seconds')
    IN_1_MINUTE = ('1 minute')
    IN_5_MINUTES = ('5 minutes')


class GraphPageLayout(StringEnum):
    COLA = ('Cola')
    COSE = ('Cose')
    DAGRE = ('Dagre')


class GraphPageDisplayFilter(StringEnum):
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


class ApplicationsPageFilter(StringEnum):
    APP_NAME = ('App Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    NAMESPACE = ('Namespace')


class ApplicationsPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    APP_NAME = ('App Name')
    ISTIO_SIDECAR = ('IstioSidecar')
    ERROR_RATE = ('Error Rate')


class WorkloadsPageFilter(StringEnum):
    WORKLOAD_NAME = ('Workload Name')
    WORKLOAD_TYPE = ('Workload Type')
    ISTIO_SIDECAR = ('Istio Sidecar')
    APP_LABEL = ('App Label')
    VERSION_LABEL = ('Version Label')
    NAMESPACE = ('Namespace')


class WorkloadsPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    WORKLOAD_NAME = ('Workload Name')
    WORKLOAD_TYPE = ('Workload Type')
    ISTIO_SIDECAR = ('IstioSidecar')
    APP_LABEL = ('App Label')
    VERSION_LABEL = ('Version Label')


class WorkloadType(StringEnum):
    DEPLOYMENT = ('Deployment')


class IstioSidecar(StringEnum):
    PRESENT = ('Present')
    NOT_PRESENT = ('Not Present')


class AppLabel(StringEnum):
    PRESENT = ('Present')
    NOT_PRESENT = ('Not Present')


class VersionLabel(StringEnum):
    PRESENT = ('Present')
    NOT_PRESENT = ('Not Present')


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
