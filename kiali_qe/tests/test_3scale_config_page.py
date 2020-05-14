import pytest
from kiali_qe.tests import ThreeScaleConfigPageTest


NAME1 = 'handler1'
NAME2 = 'handler2'
SERVICE_ID1 = 'serviceid1'
SERVICE_ID2 = 'serviceid2'
SYSTEM_URL1 = 'systemurl1'
SYSTEM_URL2 = 'systemurl2'
ACCESS_TOKEN1 = 'token1'
ACCESS_TOKEN2 = 'token2'


@pytest.mark.p_atomic
@pytest.mark.p_ro_group4
def test_sort_options(kiali_client, openshift_client, browser):
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_all_handlers(kiali_client, openshift_client, browser):
    _handler_create(kiali_client, NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)
    _handler_create(kiali_client, NAME2, SERVICE_ID2, SYSTEM_URL2, ACCESS_TOKEN2)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items()


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_details(kiali_client, openshift_client, browser):
    _handler_create(kiali_client, NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_details(NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_create(kiali_client, openshift_client, browser):
    _handler_delete(kiali_client, NAME1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_handler_creation(NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_update(kiali_client, openshift_client, browser):
    _handler_create(kiali_client, NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)
    _handler_delete(kiali_client, NAME2)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_handler_update(NAME1, SERVICE_ID2, SYSTEM_URL2, ACCESS_TOKEN2)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_handler_delete(kiali_client, openshift_client, browser):
    _handler_create(kiali_client, NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)
    tests = ThreeScaleConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_three_scale_handler_delete(NAME1)
    assert len(_handler_list(kiali_client, NAME1)) == 0


def _handler_create(kiali_client, name, service_id, system_url, access_token):
    kiali_client.delete_three_scale_handler(name=name)

    kiali_client.create_three_scale_handler(name, service_id, system_url, access_token)


def _handler_delete(kiali_client, name):
    kiali_client.delete_three_scale_handler(name=name)


def _handler_list(kiali_client, name):
    return kiali_client.three_scale_handler_list(handler_names=[name])
