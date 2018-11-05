import pytest

from kiali_qe.tests import ApplicationsPageTest
from kiali_qe.components.enums import ApplicationsPageFilter


@pytest.mark.p_group9
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which contains sufficient number of items for this test
    tests.apply_filters(filters=[
        {'name': ApplicationsPageFilter.NAMESPACE.text, 'value': 'istio-system'}])
    tests.assert_pagination_feature()


@pytest.mark.p_group4
def test_namespaces(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_group4
def test_filter_options(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_group4
def test_all_applications(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_group4
def test_application_details_random(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_random_details(filters=[])
