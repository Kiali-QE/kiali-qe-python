import pytest
from kiali_qe.tests import IstioConfigPageTest
from kiali_qe.utils import get_yaml, get_dict
from kiali_qe.utils.path import dr_hosts_path

'''
Tests are divided into groups using different services and namespaces. This way the group of tests
can be run in parallel.
'''

BOOKINFO_1 = 'bookinfo'
DEST_RULE_1 = 'dest-rules1.yaml'
DEST_RULE_2 = 'dest-rules2.yaml'
DEST_RULE_3 = 'dest-rules3.yaml'
DEST_RULE_4 = 'dest-rules4.yaml'
DEST_RULE_5 = 'dest-rules5.yaml'
DEST_RULE_6 = 'dest-rules6.yaml'
DEST_RULE_7 = 'dest-rules7.yaml'
DEST_RULE_8 = 'dest-rules8.yaml'
DEST_RULE_9 = 'dest-rules9.yaml'


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_1(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_1)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_1)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=True)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_2(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_2)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_2)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=True)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_3(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_3)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_3)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=True)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_4(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_4)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_4)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_5(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_5)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_5)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_6(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_6)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_6)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_7(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_7)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_7)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_8(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_8)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_8)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_9(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(dr_hosts_path.strpath, DEST_RULE_9)
    destination_rule_dict = get_dict(dr_hosts_path.strpath, DEST_RULE_9)

    _dr_host_link_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       namespace=BOOKINFO_1,
                       is_link_expected=False)


def _istio_config_create(openshift_client, config_dict, config_yaml, kind, api_version,
                         namespace=BOOKINFO_1):
    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)

    openshift_client.create_istio_config(body=config_yaml,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def _istio_config_delete(openshift_client, name, kind, api_version, namespace=BOOKINFO_1):
    openshift_client.delete_istio_config(name=name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def _dr_host_link_test(kiali_client, openshift_client, browser, config_dict,
                       config_yaml, kind, api_version,
                       namespace=BOOKINFO_1,
                       is_link_expected=True):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    try:
        _istio_config_create(
            openshift_client, config_dict, config_yaml, kind, api_version, namespace)

        tests.assert_host_link(config_name=config_dict.metadata.name, namespace=namespace,
                               host_name=config_dict.spec.host, is_link_expected=is_link_expected)
    finally:
        _istio_config_delete(openshift_client, config_dict.metadata.name,
                             kind, api_version, namespace)
