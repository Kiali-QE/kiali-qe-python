import pytest

from kiali_qe.tests import ServicesPageTest
from kiali_qe.components.enums import ServicesPageFilter

BOOKINFO_2 = 'bookinfo2'


@pytest.mark.p_group9
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[])
    tests.assert_pagination_feature()


@pytest.mark.p_group4
def test_namespaces(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_group4
def test_filter_options(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_group4
def test_filter_feature_random(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_feature_random()


@pytest.mark.p_group4
def test_all_services(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_group5
def test_service_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_random_details(filters=[
        {'name': ServicesPageFilter.NAMESPACE.text, 'value': namespace}])
