from kiali_qe.tests import IstioConfigPageTest, ServicesPageTest
from kiali_qe.utils import get_yaml, get_dict
from kiali_qe.utils.path import istio_objects_path
from kiali_qe.components.enums import (
    IstioConfigObjectType,
    IstioConfigPageFilter,
    IstioConfigValidationType
)


BOOKINFO = 'bookinfo'
REVIEWS = 'reviews'
DEST_RULE = 'destination-rule-cb.yaml'
DEST_RULE_VS = 'destination-rule.yaml'
DEST_RULE_BROKEN = 'destination-rule-cb-broken.yaml'
VIRTUAL_SERVICE = 'virtual-service.yaml'
VIRTUAL_SERVICE_BROKEN = 'virtual-service-broken.yaml'
VIRTUAL_SERVICE_BROKEN_WEIGHT = 'virtual-service-broken-weight.yaml'
VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT = 'virtual-service-broken-weight-text.yaml'
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


def test_virtual_service(kiali_client, openshift_client, browser):
    virtual_service = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE)
    virtual_service_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE)
    _create_dest_rule_vs(openshift_client)

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
    _delete_dest_rule_vs(openshift_client)


def test_virtual_service_broken(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)
    _create_dest_rule_vs(openshift_client)

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
    _delete_dest_rule_vs(openshift_client)


def test_virtual_service_broken_weight(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath,
                                      VIRTUAL_SERVICE_BROKEN_WEIGHT)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath,
                                           VIRTUAL_SERVICE_BROKEN_WEIGHT)
    _create_dest_rule_vs(openshift_client)

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
    _delete_dest_rule_vs(openshift_client)


def test_virtual_service_broken_weight_text(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath,
                                      VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath,
                                           VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT)
    _create_dest_rule_vs(openshift_client)

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
    _delete_dest_rule_vs(openshift_client)


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


def _istio_config_create(openshift_client, config_dict, config_yaml, kind, api_version):
    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)

    openshift_client.create_istio_config(body=config_yaml,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)


def _istio_config_delete(openshift_client, config_dict, kind, api_version):
    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=BOOKINFO,
                                         kind=kind,
                                         api_version=api_version)


def _create_dest_rule_vs(openshift_client):
    destination_rule = get_yaml(istio_objects_path.strpath, DEST_RULE_VS)
    destination_rule_dict = get_dict(istio_objects_path.strpath, DEST_RULE_VS)
    _istio_config_create(openshift_client, destination_rule_dict, destination_rule,
                         kind='DestinationRule',
                         api_version='networking.istio.io/v1alpha3')


def _delete_dest_rule_vs(openshift_client):
    destination_rule_dict = get_dict(istio_objects_path.strpath, DEST_RULE_VS)
    _istio_config_delete(openshift_client, destination_rule_dict,
                         kind='DestinationRule',
                         api_version='networking.istio.io/v1alpha3')


def _istio_config_test(kiali_client, openshift_client, browser, config_dict,
                       config_yaml, filters, kind, api_version):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    _istio_config_create(openshift_client, config_dict, config_yaml, kind, api_version)

    tests.assert_all_items(filters)

    _istio_config_details_test(kiali_client,
                               openshift_client,
                               browser,
                               config_dict,
                               config_yaml,
                               kind,
                               api_version)

    _service_details_test(kiali_client,
                          openshift_client,
                          browser,
                          config_dict,
                          config_yaml,
                          kind,
                          api_version)

    _istio_config_delete(openshift_client, config_dict, kind, api_version)

    tests.assert_all_items(filters)


def _istio_config_details_test(kiali_client, openshift_client, browser, config_dict,
                               config_yaml, kind, api_version):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    tests.assert_details(name=config_dict.metadata.name, namespace=BOOKINFO)


def _service_details_test(kiali_client, openshift_client, browser, config_dict,
                          config_yaml, kind, api_version):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    tests.assert_details(name=REVIEWS, namespace=BOOKINFO)
