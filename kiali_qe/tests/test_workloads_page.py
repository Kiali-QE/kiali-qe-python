import pytest

from kiali_qe.tests import WorkloadsPageTest
from kiali_qe.components.enums import WorkloadsPageFilter


@pytest.mark.p_group9
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which contains sufficient number of items for this test
    tests.apply_filters(filters=[
        {'name': WorkloadsPageFilter.NAMESPACE.text, 'value': 'istio-system'}])
    tests.assert_pagination_feature()


@pytest.mark.p_group7
def test_namespaces(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_group7
def test_filter_options(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_group7
def test_all_workloads(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_group7
def test_workload_details_random(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_random_details(filters=[])
