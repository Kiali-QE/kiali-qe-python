import pytest
from kiali_qe.tests import IstioConfigPageTest
from kiali_qe.components.enums import IstioConfigPageFilter


@pytest.mark.p_group6
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which is not affected by other CRUD tests which are using
    # bookinfo
    tests.apply_filters(filters=[
            {'name': IstioConfigPageFilter.NAMESPACE.text, 'value': 'istio-system'}])
    tests.assert_pagination_feature()


@pytest.mark.p_group7
def test_namespaces(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_group7
def test_filter_options(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


# p_group_last is used for tests which must be run at the end when all other test are done
@pytest.mark.p_group_last
def test_filter_feature_random(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_feature_random()
