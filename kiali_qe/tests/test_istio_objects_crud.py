from kiali_qe.tests import IstioConfigPageTest
from kiali_qe.utils import get_yaml, get_dict
from kiali_qe.utils.path import istio_objects_path
from kiali_qe.components.enums import (
    IstioConfigObjectType,
    IstioConfigPageFilter,
    IstioConfigValidationType
)


BOOKINFO = 'bookinfo'
DEST_RULE = 'destination-rule-cb.yaml'
DEST_RULE_BROKEN = 'destination-rule-cb-broken.yaml'
DEST_POLICY = 'destination-policy.yaml'
DEST_POLICY_BROKEN = 'destination-policy-broken.yaml'
VIRTUAL_SERVICE = 'virtual-service.yaml'
VIRTUAL_SERVICE_BROKEN = 'virtual-service-broken.yaml'
ROUTE_RULE = 'route-rule.yaml'
ROUTE_RULE_BROKEN = 'route-rule-broken.yaml'
QUOTA_SPEC = 'quota-spec.yaml'
QUOTA_SPEC_BINDING = 'quota-spec-binding.yaml'
GATEWAY = 'gateway.yaml'
SERVICE_ENTRY = 'service-entry.yaml'


def test_destination_rule(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(istio_objects_path.strpath, DEST_RULE)
    destination_rule_dict = get_dict(istio_objects_path.strpath, DEST_RULE)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_rule_dict.metadata.name}
                        ],
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3')


def test_destination_rule_broken(kiali_client, openshift_client, browser):
    destination_rule_broken = get_yaml(istio_objects_path.strpath, DEST_RULE_BROKEN)
    destination_rule_broken_dict = get_dict(istio_objects_path.strpath, DEST_RULE_BROKEN)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_broken_dict,
                       destination_rule_broken,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.NOT_VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_rule_broken_dict.metadata.name}
                        ],
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3')


def test_destination_policy(kiali_client, openshift_client, browser):
    destination_policy = get_yaml(istio_objects_path.strpath, DEST_POLICY)
    destination_policy_dict = get_dict(istio_objects_path.strpath, DEST_POLICY)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_policy_dict,
                       destination_policy,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_POLICY.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_policy_dict.metadata.name}
                        ],
                       kind='DestinationPolicy',
                       api_version='config.istio.io/v1alpha2')


def test_destination_policy_broken(kiali_client, openshift_client, browser):
    destination_policy_broken = get_yaml(istio_objects_path.strpath, DEST_POLICY_BROKEN)
    destination_policy_broken_dict = get_dict(istio_objects_path.strpath, DEST_POLICY_BROKEN)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_policy_broken_dict,
                       destination_policy_broken,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_POLICY.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.NOT_VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_policy_broken_dict.metadata.name}
                        ],
                       kind='DestinationPolicy',
                       api_version='config.istio.io/v1alpha2')


def test_virtual_service(kiali_client, openshift_client, browser):
    virtual_service = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE)
    virtual_service_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE)

    _istio_config_test(kiali_client, openshift_client, browser,
                       virtual_service_dict,
                       virtual_service,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.VIRTUAL_SERVICE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': virtual_service_dict.metadata.name}
                        ],
                       kind='VirtualService',
                       api_version='networking.istio.io/v1alpha3')


def test_virtual_service_broken(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)

    _istio_config_test(kiali_client, openshift_client, browser,
                       virtual_service_broken_dict,
                       virtual_service_broken,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.VIRTUAL_SERVICE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.NOT_VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': virtual_service_broken_dict.metadata.name}
                        ],
                       kind='VirtualService',
                       api_version='networking.istio.io/v1alpha3')


def test_route_rule(kiali_client, openshift_client, browser):
    route_rule = get_yaml(istio_objects_path.strpath, ROUTE_RULE)
    route_rule_dict = get_dict(istio_objects_path.strpath, ROUTE_RULE)

    _istio_config_test(kiali_client, openshift_client, browser,
                       route_rule_dict,
                       route_rule,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.ROUTE_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': route_rule_dict.metadata.name}
                        ],
                       kind='RouteRule',
                       api_version='config.istio.io/v1alpha2')


def test_route_rule_broken(kiali_client, openshift_client, browser):
    route_rule_broken = get_yaml(istio_objects_path.strpath, ROUTE_RULE_BROKEN)
    route_rule_broken_dict = get_dict(istio_objects_path.strpath, ROUTE_RULE_BROKEN)

    _istio_config_test(kiali_client, openshift_client, browser,
                       route_rule_broken_dict,
                       route_rule_broken,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.ROUTE_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.NOT_VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': route_rule_broken_dict.metadata.name}
                        ],
                       kind='RouteRule',
                       api_version='config.istio.io/v1alpha2')


def test_quota_spec(kiali_client, openshift_client, browser):
    quota_spec = get_yaml(istio_objects_path.strpath, QUOTA_SPEC)
    quota_spec_dict = get_dict(istio_objects_path.strpath, QUOTA_SPEC)

    _istio_config_test(kiali_client, openshift_client, browser,
                       quota_spec_dict,
                       quota_spec,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.QUOTA_SPEC.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': 'quota-spec-auto'}
                        ],
                       kind='QuotaSpec',
                       api_version='config.istio.io/v1alpha2')


def test_quota_spec_binding(kiali_client, openshift_client, browser):
    quota_spec_binding = get_yaml(istio_objects_path.strpath, QUOTA_SPEC_BINDING)
    quota_spec_binding_dict = get_dict(istio_objects_path.strpath, QUOTA_SPEC_BINDING)

    _istio_config_test(kiali_client, openshift_client, browser,
                       quota_spec_binding_dict,
                       quota_spec_binding,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.QUOTA_SPEC_BINDING.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': 'quota-spec-binding-auto'}
                        ],
                       kind='QuotaSpecBinding',
                       api_version='config.istio.io/v1alpha2')


def test_gateway(kiali_client, openshift_client, browser):
    gateway = get_yaml(istio_objects_path.strpath, GATEWAY)
    gateway_dict = get_dict(istio_objects_path.strpath, GATEWAY)

    _istio_config_test(kiali_client, openshift_client, browser,
                       gateway_dict,
                       gateway,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.GATEWAY.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': gateway_dict.metadata.name}
                        ],
                       kind='Gateway',
                       api_version='networking.istio.io/v1alpha3')


def test_service_entry(kiali_client, openshift_client, browser):
    yaml = get_yaml(istio_objects_path.strpath, SERVICE_ENTRY)
    dict = get_dict(istio_objects_path.strpath, SERVICE_ENTRY)

    _istio_config_test(kiali_client, openshift_client, browser,
                       dict,
                       yaml,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.SERVICE_ENTRY.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': dict.metadata.name}
                        ],
                       kind='ServiceEntry',
                       api_version='networking.istio.io/v1alpha3')


def _istio_config_test(kiali_client, openshift_client, browser, config_dict,
                       config_yaml, filters, kind, api_version):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)

    openshift_client.create_istio_config(body=config_yaml,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)
    tests.assert_all_items(filters)

    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)
    tests.assert_all_items(filters)
