import pytest
from kiali_qe.tests import ThreeScaleConfigPageTest
from kiali_qe.utils import get_yaml, get_dict
from kiali_qe.utils.path import threescale_path

HANDLER1 = "handler1.yaml"
HANDLER2 = "handler2.yaml"
INSTANCE1 = "instance1.yaml"
INSTANCE2 = "instance2.yaml"
RULE1 = "rule1.yaml"
RULE2 = "rule2.yaml"
HANDLER_NAME1 = 'handler-auto1'
HANDLER_NAME2 = 'handler-auto2'
RULE_NAME1 = 'handler-auto-rule1'
RULE_NAME2 = 'handler-auto-rule2'
INSTANCE_NAME1 = 'handler-auto-rule1'
INSTANCE_NAME2 = 'handler-auto-rule2'
SERVICE_ID1 = 'serviceid1'
SERVICE_ID2 = 'serviceid2'
SYSTEM_URL1 = 'https://systemurl1.net:443'
SYSTEM_URL2 = 'https://systemurl2.net:443'
ACCESS_TOKEN1 = 'token1'
ACCESS_TOKEN2 = 'token2'
ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_all_handlers(kiali_client, openshift_client, browser):
    handler_create(openshift_client, HANDLER1)
    handler_create(openshift_client, HANDLER2)
    handler_create(openshift_client, RULE1, kind='rule')
    handler_create(openshift_client, RULE2, kind='rule')
    handler_create(openshift_client, INSTANCE1, kind='instance')
    handler_create(openshift_client, INSTANCE2, kind='instance')
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespace=ISTIO_SYSTEM)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_details(kiali_client, openshift_client, browser):
    handler_create(openshift_client, HANDLER1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_handler_details(HANDLER_NAME1, SYSTEM_URL1, ACCESS_TOKEN1)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_create(kiali_client, openshift_client, browser):
    handler_delete(openshift_client, HANDLER_NAME1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_handler_creation(HANDLER_NAME1, SYSTEM_URL1, ACCESS_TOKEN1)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_delete(kiali_client, openshift_client, browser):
    handler_create(openshift_client, HANDLER1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_handler_delete(HANDLER_NAME1)
    assert len(_handler_list(kiali_client, HANDLER_NAME1)) == 0


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_rule_instance_create(kiali_client, openshift_client, browser):
    handler_create(openshift_client, HANDLER1)
    handler_delete(openshift_client, RULE_NAME1, kind='rule')
    handler_delete(openshift_client, INSTANCE_NAME1, kind='instance')
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_instance_rule_creation(RULE_NAME1, HANDLER_NAME1)


def handler_create(openshift_client, handler, kind='handler',
                   api_version='config.istio.io/v1alpha2', namespace=ISTIO_SYSTEM):
    config_yaml = get_yaml(threescale_path.strpath, handler)
    config_dict = get_dict(threescale_path.strpath, handler)
    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)

    openshift_client.create_istio_config(body=config_yaml,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def handler_delete(openshift_client, name, kind='handler',
                   api_version='config.istio.io/v1alpha2', namespace=ISTIO_SYSTEM):
    openshift_client.delete_istio_config(name=name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def _handler_list(kiali_client, name, namespace=ISTIO_SYSTEM):
    return kiali_client.three_scale_handler_list(namespace=namespace, handler_names=[name])
