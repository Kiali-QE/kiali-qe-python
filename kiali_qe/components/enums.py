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


class HelpMenuEnum(StringEnum):
    DOCUMENTATION = ('Documentation')
    VIEW_DEBUG_INFO = ('View Debug Info')
    VIEW_CERTIFICATES_INFO = ('View Certificates Info')
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
    LAST_MINUTE = ('Last 1m')
    LAST_5_MINUTES = ('Last 5m')
    LAST_10_MINUTES = ('Last 10m')
    LAST_30_MINUTES = ('Last 30m')
    LAST_HOUR = ('Last 1h')
    LAST_3_HOURS = ('Last 3h')
    LAST_6_HOURS = ('Last 6h')


class MetricsTimeInterval(StringEnum):
    LAST_MINUTE = ('Last 1m')
    LAST_5_MINUTES = ('Last 5m')
    LAST_10_MINUTES = ('Last 10m')
    LAST_30_MINUTES = ('Last 30m')
    LAST_HOUR = ('Last 1h')
    LAST_3_HOURS = ('Last 3h')
    LAST_6_HOURS = ('Last 6h')
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
    REQUEST_RATE = ('Request Rate')
    RESPONSE_TIME = ('Response Time')
    THROUGHPUT = ('Throughput')
    REQUEST_DISTRIBUTION = ('Request Distribution')
    CLUSTER_BOXES = ('Cluster Boxes')
    NAMESPACE_BOXES = ('Namespace Boxes')
    COMPRESSED_HIDE = ('Compressed Hide')
    IDLE_EDGES = ('Idle Edges')
    IDLE_NODES = ('Idle Nodes')
    OPERATION_NODES = ('Operation Nodes')
    SERVICE_NODES = ('Service Nodes')
    TRAFFIC_ANIMATION = ('Traffic Animation')


class GraphPageBadgesFilter(StringEnum):
    MISSING_SIDECARS = ('Missing Sidecars')
    SECURITY = ('Security')
    VIRTUAL_SERVICES = ('Virtual Services')


class ApplicationsPageFilter(StringEnum):
    APP_NAME = ('App Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    ISTIO_TYPE = ('Istio Type')
    HEALTH = ('Health')
    LABEL = ('Label')


class ApplicationsPageSort(StringEnum):
    APP_NAME = ('Name')
    NAMESPACE = ('Namespace')
    HEALTH = ('Health')
    DETAILS = ('Details')


class OverviewPageFilter(StringEnum):
    NAME = ('Namespace')
    HEALTH = ('Health')
    MTLS_STATUS = ('mTLS status')
    LABEL = ('Namespace Label')


class OverviewPageSort(StringEnum):
    NAME = ('Name')
    HEALTH = ('Health')
    MTLS = ('mTLS')
    ISTIO_CONFIG = ('Istio Config')


class OverviewPageType(StringEnum):
    APPS = ('Apps')
    WORKLOADS = ('Workloads')
    SERVICES = ('Services')


class OverviewViewType(StringEnum):
    EXPAND = ('Expand view')
    COMPACT = ('Compact view')
    LIST = ('List view')


class OverviewLinks(StringEnum):
    GRAPH = ('Graph')
    APPLICATIONS = ('Applications')
    WORKLOADS = ('Workloads')
    SERVICES = ('Services')
    ISTIO_CONFIG = ('Istio Config')


class OverviewInjectionLinks(StringEnum):
    DISABLE_AUTO_INJECTION = ('Disable Auto Injection')
    ENABLE_AUTO_INJECTION = ('Enable Auto Injection')
    REMOVE_AUTO_INJECTION = ('Remove Auto Injection')


class OverviewTrafficLinks(StringEnum):
    CREATE_TRAFFIC_POLICIES = ('Create Traffic Policies')
    UPDATE_TRAFFIC_POLICIES = ('Update Traffic Policies')
    DELETE_TRAFFIC_POLICIES = ('Delete Traffic Policies')


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
    LABEL = ('Label')


class WorkloadsPageSort(StringEnum):
    WORKLOAD_NAME = ('Name')
    NAMESPACE = ('Namespace')
    WORKLOAD_TYPE = ('Type')
    HEALTH = ('Health')
    DETAILS = ('Details')


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


class WorkloadHealth(StringEnum):
    HEALTHY = ('Healthy')
    DEGRADED = ('Degraded')
    FAILURE = ('Failure')
    NO_HEALTH_INFO = ('No health information')


class ServicesPageFilter(StringEnum):
    SERVICE_NAME = ('Service Name')
    ISTIO_SIDECAR = ('Istio Sidecar')
    ISTIO_TYPE = ('Istio Type')
    HEALTH = ('Health')
    LABEL = ('Label')


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
    AUTHORIZATION_POLICY = ('AuthorizationPolicy')
    DESTINATION_RULE = ('DestinationRule')
    ENVOY_FILTER = ('EnvoyFilter')
    GATEWAY = ('Gateway')
    PEER_AUTHENTICATION = ('PeerAuthentication')
    REQUEST_AUTHENTICATION = ('RequestAuthentication')
    SERVICE_ENTRY = ('ServiceEntry')
    SIDECAR = ('Sidecar')
    VIRTUAL_SERVICE = ('VirtualService')
    WORKLOAD_ENTRY = ('WorkloadEntry')
    WORKLOAD_GROUP = ('WorkloadGroup')


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
    IDLE = ('Idle')


class IstioConfigValidation(StringEnum):
    NA = ('N/A')
    VALID = ('Valid')
    WARNING = ('Warning')
    NOT_VALID = ('Not Valid')


class InboundMetricsFilter(StringEnum):
    LOCAL_VERSION = ('Local version')
    REMOTE_VERSION = ('Remote version')
    RESPONSE_CODE = ('Response code')
    GRPC_STATUS = ('GRPC status')
    RESPONSE_FLAGS = ('Response flags')


class OutboundMetricsFilter(StringEnum):
    LOCAL_VERSION = ('Local version')
    REMOTE_VERSION = ('Remote version')
    RESPONSE_CODE = ('Response code')
    GRPC_STATUS = ('GRPC status')
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
    REQUEST_ROUTING = ('Request Routing')
    FAULT_INJECTION = ('Fault Injection')
    TRAFFIC_SHIFTING = ('Traffic Shifting')
    TCP_TRAFFIC_SHIFTING = ('TCP Traffic Shifting')
    REQUEST_TIMEOUTS = ('Request Timeouts')


class RoutingWizardTLS(StringEnum):
    UNSET = ('UNSET')
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


class TrafficType(StringEnum):
    APP = ('App')
    SERVICE = ('Service')
    WORKLOAD = ('Workload')
    UNKNOWN = ('Unknown')


class ItemIconType(StringEnum):
    API_DOCUMENTATION = ('API Documentation')


class AuthPolicyType(StringEnum):
    DENY_ALL = ('DENY_ALL')
    ALLOW_ALL = ('ALLOW_ALL')
    RULES = ('RULES')


class AuthPolicyActionType(StringEnum):
    DENY = ('DENY')
    ALLOW = ('ALLOW')


class MutualTLSMode(StringEnum):
    UNSET = ('UNSET')
    DISABLE = ('DISABLE')
    PERMISSIVE = ('PERMISSIVE')
    STRICT = ('STRICT')


class PeerAuthMode(StringEnum):
    UNSET = ('UNSET')
    DISABLE = ('DISABLE')
    PERMISSIVE = ('PERMISSIVE')
    STRICT = ('STRICT')


class LabelOperation(StringEnum):
    OR = ('or')
    AND = ('and')


class BoundTrafficType(StringEnum):
    INBOUND = ('Inbound')
    OUTBOUND = ('Outbound')


class OverviewHealth(StringEnum):
    FAILURE = ('Failure')
    DEGRADED = ('Degraded')
    HEALTHY = ('Healthy')


class AppIstioSidecar(StringEnum):
    PRESENT = ('Present')
    NOT_PRESENT = ('Not Present')


class AppHealth(StringEnum):
    HEALTHY = ('Healthy')
    DEGRADED = ('Degraded')
    FAILURE = ('Failure')
    NO_HEALTH_INFO = ('No health information')


class OverviewMTSLStatus (StringEnum):
    ENABLED = ('Enabled')
    PARENABLED = ('Partially Enabled')
    DISABLED = ('Disabled')
