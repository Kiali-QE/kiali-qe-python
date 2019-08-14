import pytest

from kiali_qe.tests import DistributedTracingPageTest

BOOKINFO = 'bookinfo'


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_search_traces(kiali_client, openshift_client, browser):
    tests = DistributedTracingPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_search_traces(service_name='details', namespaces=[BOOKINFO])
