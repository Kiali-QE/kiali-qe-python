from enum import Enum


class StringEnum(Enum):
    def __init__(self, text):
        self.text = text


class MainMenuEnum(StringEnum):
    GRAPH = ('Graph')
    SERVICES = ('Services')
    ISTIO_MIXER = ('Istio Mixer')
    DISTRIBUTED_TRACING = ('Distributed Tracing')


class HelpMenuEnum(StringEnum):
    ABOUT = ('About')


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
    BREADTH_FIRST = ('Breadthfirst')
    COLA = ('Cola')
    COSE = ('Cose')
    DAGRE = ('Dagre')
    KLAY = ('Klay')


class GraphPageFilter(StringEnum):
    CIRCUIT_BREAKERS = ('Circuit Breakers')
    ROUTE_RULES = ('Route Rules')
    EDGE_LABELS = ('Edge Labels')
    NODE_LABELS = ('Node Labels')


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


class IstioMixerPageFilter(StringEnum):
    RULE_NAME = ('Rule Name')
    NAMESPACE = ('Namespace')


class IstioMixerPageSort(StringEnum):
    NAMESPACE = ('Namespace')
    RULE_NAME = ('Rule Name')
