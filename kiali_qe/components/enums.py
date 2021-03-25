from enum import Enum


class StringEnum(Enum):
    def __init__(self, text):
        self.text = text


class StringTupleEnum(Enum):
    def __init__(self, key, text):
        self.key = key
        self.text = text


class MainMenuEnum(StringEnum):
    OVERVIEW = ('Overview')
    GRAPH = ('Graph')
    APPLICATIONS = ('Applications')
    WORKLOADS = ('Workloads')
    SERVICES = ('Services')
    ISTIO_CONFIG = ('Istio Config')
    DISTRIBUTED_TRACING = ('Distributed Tracing')
    THREESCALE_CONFIG = ('3scale Config')


class HelpMenuEnum(StringEnum):
    DOCUMENTATION = ('Documentation')
    VIEW_DEBUG_INFO = ('View Debug Info')
    ABOUT = ('About')


class UserMenuEnum(StringEnum):
    LOGOUT = ('Logout')


class ApplicationVersionEnum(StringEnum):
    KIALI_UI = ("Kiali UI")
    KIALI_CORE = ("Kiali Server")
    KIALI_CONTAINER = ("Kiali Container")
    ISTIO = ("OpenShift Service Mesh")
    PROMETHEUS = ("Prometheus")
    KUBERNETES = ("Kubernetes")
    GRAFANA = ("Grafana URL")
    JAEGER = ("Jaeger URL")


class ApplicationVersionUpstreamEnum(StringEnum):
    KIALI_UI = ("Kiali UI")
    KIALI_CORE = ("Kiali Server")
    KIALI_CONTAINER = ("Kiali Container")
    ISTIO = ("Istio")
    PROMETHEUS = ("Prometheus")
    KUBERNETES = ("Kubernetes")
    GRAFANA = ("Grafana URL")
    JAEGER = ("Jaeger URL")


class TimeIntervalUIText(StringEnum):
    LAST_MINUTE = ('1m Traffic')
    LAST_5_MINUTES = ('5m Traffic')
    LAST_10_MINUTES = ('10m Traffic')
    LAST_30_MINUTES = ('30m Traffic')
    LAST_HOUR = ('1h Traffic')
    LAST_3_HOURS = ('3h Traffic')
    LAST_6_HOURS = ('6h Traffic')


class MetricsTimeInterval(StringEnum):
    LAST_MINUTE = ('1m Traffic')
    LAST_5_MINUTES = ('5m Traffic')
    LAST_10_MINUTES = ('10m Traffic')
    LAST_30_MINUTES = ('30m Traffic')
    LAST_HOUR = ('1h Traffic')
    LAST_3_HOURS = ('3h Traffic')
    LAST_6_HOURS = ('6h Traffic')
    CUSTOM = ('Custom')


class TimeIntervalRestParam(StringEnum):
    LAST_MINUTE = ('1m')
    LAST_5_MINUTES = ('5m')
    LAST_10_MINUTES = ('10m')
    LAST_30_MINUTES = ('30m')
    LAST_HOUR = ('1h')
    LAST_3_HOURS = ('3h')
    LAST_6_HOURS = ('6h')


class TailLines(StringEnum):
    LINES_10 = ('10 lines')
    LINES_50 = ('50 lines')
    LINES_100 = ('100 lines')
    LINES_300 = ('300 lines')
    LINES_500 = ('500 lines')
    LINES_1000 = ('1000 lines')
    LINES_5000 = ('5000 lines')
    LINES_ALL = ('All lines')


class GraphRefreshInterval(StringEnum):
    PAUSE = ('Pause')
    IN_10_SECONDS = ('Every 10s')
    IN_15_SECONDS = ('Every 15s')
    IN_30_SECONDS = ('Every 30s')
    IN_1_MINUTE = ('Every 1m')
    IN_5_MINUTES = ('Every 5m')
    IN_15_MINUTES = ('Every 15m')


class GraphPageLayout(StringEnum):
    COLA = ('cola')
    COSE = ('cose-bilkent')
    DAGRE = ('dagre')


class GraphType(StringEnum):
    APP = ('App graph')
    SERVICE = ('Service graph')
    VERSIONED_APP = ('Versioned app graph')
    WORKLOAD = ('Workload graph')


class GraphPageDisplayFilter(StringEnum):
    COMPRESS_HIDDEN = ('Compress Hidden')
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
    HEALTH = ('Health')


class ApplicationsPageSort(StringEnum):
    APP_NAME = ('Name')
    NAMESPACE = ('Namespace')
    HEALTH = ('Health')
    DETAILS = ('Details')


class OverviewPageFilter(StringEnum):
    NAME = ('Name')
    HEALTH = ('Health')
    MTLS_STATUS = ('mTLS status')


class OverviewPageSort(StringEnum):
    NAME = ('Name')
    HEALTH = ('Health')
    MTLS = ('mTLS')
    ISTIO_CONFIG = ('Istio Config')


class OverviewPageType(StringEnum):
    APPS = ('Apps')
    WORKLOADS = ('Workloads')
    SERVICES = ('Services')


class OverviewLinks(StringEnum):
    GRAPH = ('graph')
    APPLICATIONS = ('applications')
    WORKLOADS = ('workloads')
    SERVICES = ('services')
    ISTIO_CONFIG = ('istio')


class OverviewGraphTypeLink(StringEnum):
    APP = ('app')
    WORKLOAD = ('workload')
    SERVICE = ('service')


class WorkloadsPageFilter(StringEnum):
    WORKLOAD_NAME = ('Workload Name')
    WORKLOAD_TYPE = ('Workload Type')
    ISTIO_SIDECAR = ('Istio Sidecar')
    HEALTH = ('Health')
    APP_LABEL = ('App Label')
    VERSION_LABEL = ('Version Label')


class WorkloadsPageSort(StringEnum):
    WORKLOAD_NAME = ('Name')
    NAMESPACE = ('Namespace')
    WORKLOAD_TYPE = ('Type')
    HEALTH = ('Health')
    DETAILS = ('Details')
    LABEL_VALIDATION = ('Label Validation')


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
    SERVICE_NAME = ('Service Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    HEALTH = ('Health')


class ServicesPageSort(StringEnum):
    SERVICE_NAME = ('Name')
    NAMESPACE = ('Namespace')
    HEALTH = ('Health')
    DETAILS = ('Details')
    CONFIGURATION = ('Configuration')


class ServicesPageRateInterval(StringEnum):
    LAST_1_MINUTE = ('Last 1 minute')
    LAST_5_MINUTES = ('Last 5 minutes')
    LAST_10_MINUTES = ('Last 10 minutes')
    LAST_30_MINUTES = ('Last 30 minutes')


class IstioConfigPageFilter(StringEnum):
    ISTIO_TYPE = ('Istio Type')
    ISTIO_NAME = ('Istio Name')
    CONFIG = ('Config')


class IstioConfigPageSort(StringEnum):
    ISTIO_NAME = ('Name')
    NAMESPACE = ('Namespace')
    ISTIO_TYPE = ('Type')
    CONFIGURATION = ('Configuration')


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
    POLICY = ('Policy')
    MESH_POLICY = ('MeshPolicy')
    CLUSTER_RBAC_CONFIG = ('ClusterRbacConfig')
    SERVICE_MESH_POLICY = ('ServiceMeshPolicy')
    SERVICE_MESH_RBAC_CONFIG = ('ServiceMeshRbacConfig')
    RBAC_CONFIG = ('RbacConfig')
    SIDECAR = ('Sidecar')
    AUTHORIZATION_POLICY = ('AuthorizationPolicy')
    SERVICE_ROLE = ('ServiceRole')
    SERVICE_ROLE_BINDING = ('ServiceRoleBinding')


class IstioConfigValidationType(StringEnum):
    VALID = ('Valid')
    NOT_VALID = ('Not Valid')
    WARNING = ('Warning')
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


class InboundMetricsFilter(StringEnum):
    LOCAL_VERSION = ('Local version')
    REMOTE_APP = ('Remote app')
    REMOTE_VERSION = ('Remote version')
    RESPONSE_CODE = ('Response code')
    RESPONSE_FLAGS = ('Response flags')


class OutboundMetricsFilter(StringEnum):
    LOCAL_VERSION = ('Local version')
    REMOTE_SERVICE = ('Remote service')
    REMOTE_APP = ('Remote app')
    REMOTE_VERSION = ('Remote version')
    RESPONSE_CODE = ('Response code')
    RESPONSE_FLAGS = ('Response flags')


class MetricsHistograms(StringEnum):
    AVERAGE = ('Average')
    QUANTILE_05 = ('Quantile 0.5')
    QUANTILE_095 = ('Quantile 0.95')
    QUANTILE_099 = ('Quantile 0.99')
    QUANTILE_0999 = ('Quantile 0.999')


class MetricsSource(StringEnum):
    SOURCE = ('Source')
    DESTINATION = ('Destination')


class MeshWideTLSType(StringEnum):
    DISABLED = ('')
    PARTLY_ENABLED = ('Mesh-wide TLS is partially enabled')
    ENABLED = ('Mesh-wide TLS is fully enabled')


class RoutingWizardType(StringEnum):
    CREATE_WEIGHTED_ROUTING = ('Create Weighted Routing')
    UPDATE_WEIGHTED_ROUTING = ('Update Weighted Routing')
    CREATE_MATCHING_ROUTING = ('Create Matching Routing')
    UPDATE_MATCHING_ROUTING = ('Update Matching Routing')
    SUSPEND_TRAFFIC = ('Suspend Traffic')
    UPDATE_SUSPENDED_TRAFFIC = ('Update Suspended Traffic')
    ADD_3_SCALE_RULE = ('Add 3scale API Management Rule')
    UPDATE_3_SCALE_RULE = ('Update 3scale API Management Rule')
    DELETE_3_SCALE_RULE = ('Delete 3Scale API Management Rule')


class RoutingWizardTLS(StringEnum):
    DISABLE = ('DISABLE')
    ISTIO_MUTUAL = ('ISTIO_MUTUAL')
    SIMPLE = ('SIMPLE')
    MUTUAL = ('MUTUAL')


class TLSMutualValues(StringTupleEnum):
    CA_CERT = ('caCertificates', 'ca_cert')
    CLIENT_CERT = ('clientCertificate', 'client_cert')
    PRIVATE_KEY = ('privateKey', 'private_key')


class RoutingWizardLoadBalancer(StringEnum):
    ROUND_ROBIN = ('ROUND_ROBIN')
    LEAST_CONN = ('LEAST_CONN')
    RANDOM = ('RANDOM')
    PASSTHROUGH = ('PASSTHROUGH')


class ThreeScaleConfigPageSort(StringEnum):
    HANDLER_NAME = ('Handler Name')
    SERVICE_ID = ('Service Id')
    SYSTEM_URL = ('System Url')


class TrafficType(StringEnum):
    APP = ('App')
    SERVICE = ('Service')
    WORKLOAD = ('Workload')
    UNKNOWN = ('Unknown')


class ItemIconType(StringEnum):
    API_DOCUMENTATION = ('API Documentation')
