from enum import Enum


class StringEnum(Enum):
    def __init__(self, text):
        self.text = text


class MainMenuEnum(StringEnum):
    OVERVIEW = ('Overview')
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
    JAEGER = ("JaegerURL")
    GRAFANA = ("GrafanaURL")


class PaginationPerPage(Enum):
    FIVE = 5
    TEN = 10
    FIFTEEN = 15


class GraphPageDuration(StringEnum):
    LAST_MINUTE = ('Last min')
    LAST_5_MINUTES = ('Last 5 min')
    LAST_10_MINUTES = ('Last 10 min')
    LAST_30_MINUTES = ('Last 30 min')
    LAST_HOUR = ('Last hour')
    LAST_3_HOURS = ('Last 3 hours')
    LAST_6_HOURS = ('Last 6 hours')
    LAST_12_HOURS = ('Last 12 hours')
    LAST_DAY = ('Last day')
    LAST_7_DAYS = ('Last 7 days')
    LAST_30_DAYS = ('Last 30 days')


class GraphRefreshInterval(StringEnum):
    PAUSE = ('Pause')
    IN_5_SECONDS = ('Every 5 sec')
    IN_10_SECONDS = ('Every 10 sec')
    IN_15_SECONDS = ('Every 15 sec')
    IN_30_SECONDS = ('Every 30 sec')
    IN_1_MINUTE = ('Every 1 min')
    IN_5_MINUTES = ('Every 5 min')


class GraphPageLayout(StringEnum):
    COLA = ('cola')
    COSE = ('cose-bilkent')
    DAGRE = ('dagre')


class GraphType(StringEnum):
    APP = ('App')
    SERVICE = ('Service')
    VERSIONED_APP = ('Versioned app')
    WORKLOAD = ('Workload')


class GraphPageDisplayFilter(StringEnum):
    NODE_LABELS = ('Node Names')
    SERVICE_NODES = ('Service Nodes')
    TRAFFIC_ANIMATION = ('Traffic Animation')
    UNUSED_NODES = ('Unused Nodes')


class GraphPageBadgesFilter(StringEnum):
    CIRCUIT_BREAKERS = ('Circuit Breakers')
    VIRTUAL_SERVICES = ('Virtual Services')
    MISSING_SIDECARS = ('Missing Sidecars')
    SECURITY = ('Security')


class EdgeLabelsFilter(StringEnum):
    HIDE = ('Hide')
    REQUEST_PER_SECOND = ('Requests per second')
    REQUEST_PERCENT = ('Requests percent of total')
    RESPONSE_TIME = ('Response time 95th percentile')


class ApplicationsPageFilter(StringEnum):
    APP_NAME = ('App Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    NAMESPACE = ('Namespace')
    HEALTH = ('Health')


class ApplicationsPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    APP_NAME = ('App Name')
    ISTIO_SIDECAR = ('IstioSidecar')
    ERROR_RATE = ('Error Rate')


class OverviewPageFilter(StringEnum):
    NAME = ('Name')
    HEALTH = ('Health')


class OverviewPageSort(StringEnum):
    NAME = ('Name')
    STATUS = ('Status')


class WorkloadsPageFilter(StringEnum):
    WORKLOAD_NAME = ('Workload Name')
    WORKLOAD_TYPE = ('Workload Type')
    ISTIO_SIDECAR = ('Istio Sidecar')
    HEALTH = ('Health')
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
    CRON_JOB = ('CronJob')
    DAEMON_SET = ('DaemonSet')
    DEPLOYMENT = ('Deployment')
    DEPLOYMENT_CONFIG = ('DeploymentConfig')
    JOB = ('Job')
    POD = ('Pod')
    REPLICA_SET = ('ReplicaSet')
    REPLICATION_CONTROLLER = ('ReplicationController')
    STATEFUL_SET = ('StatefulSet')


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
    NAMESPACE = ('Namespace')
    SERVICE_NAME = ('Service Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    HEALTH = ('Health')


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
    ADAPTER = ('Adapter')
    TEMPLATE = ('Template')
    VIRTUAL_SERVICE = ('VirtualService')
    GATEWAY = ('Gateway')
    SERVICE_ENTRY = ('ServiceEntry')
    QUOTA_SPEC = ('QuotaSpec')
    QUOTA_SPEC_BINDING = ('QuotaSpecBinding')


class IstioConfigValidationType(StringEnum):
    VALID = ('Valid')
    NOT_VALID = ('Not Valid')
    NOT_VALIDATED = ('Not Validated')


class HealthType(StringEnum):
    NA = ('N/A')
    HEALTHY = ('Healthy')
    FAILURE = ('Failure')
    DEGRADED = ('Degraded')


class IstioConfigValidation(StringEnum):
    NA = ('N/A')
    VALID = ('Valid')
    WARNING = ('Warning')
    NOT_VALID = ('Not Valid')


class MetricsFilter(StringEnum):
    LOCAL_VERSION = ('Local version')
    REMOTE_APP = ('Remote app')
    REMOTE_VERSION = ('Remote version')
    RESPONSE_CODE = ('Response code')


class MetricsHistograms(StringEnum):
    AVERAGE = ('Average')
    QUANTILE_05 = ('Quantile 0.5')
    QUANTILE_095 = ('Quantile 0.95')
    QUANTILE_099 = ('Quantile 0.99')
    QUANTILE_0999 = ('Quantile 0.999')


class MetricsSource(StringEnum):
    SOURCE = ('Source')
    DESTINATION = ('Destination')


class MetricsDuration(StringEnum):
    LAST_MINUTE = ('Last min')
    LAST_5_MINUTES = ('Last 5 min')
    LAST_10_MINUTES = ('Last 10 min')
    LAST_30_MINUTES = ('Last 30 min')
    LAST_HOUR = ('Last hour')
    LAST_3_HOURS = ('Last 3 hours')
    LAST_6_HOURS = ('Last 6 hours')
    LAST_12_HOURS = ('Last 12 hours')
    LAST_DAY = ('Last day')
    LAST_7_DAYS = ('Last 7 days')
    LAST_30_DAYS = ('Last 30 days')


class MetricsRefreshInterval(StringEnum):
    PAUSE = ('Pause')
    IN_5_SECONDS = ('5 sec')
    IN_10_SECONDS = ('10 sec')
    IN_15_SECONDS = ('15 sec')
    IN_30_SECONDS = ('30 sec')
    IN_1_MINUTE = ('1 min')
    IN_5_MINUTES = ('5 min')
