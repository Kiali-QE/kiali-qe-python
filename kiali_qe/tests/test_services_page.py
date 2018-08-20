import pytest

from kiali_qe.tests import ServicesPageTest
from kiali_qe.components.enums import ServicesPageFilter

@pytest.mark.p_group9
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which is not affected by other CRUD tests which are using bookinfo
    tests.apply_filters(filters=[
            {'name': ServicesPageFilter.NAMESPACE.text, 'value': 'istio-system'}])
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

@pytest.mark.p_group4
def test_service_details_random(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_random_details(filters=[])
