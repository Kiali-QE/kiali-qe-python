import pytest
from kiali_qe.tests import IstioConfigPageTest

BOOKINFO_2 = 'bookinfo2'


@pytest.mark.p_ro_namespace
@pytest.mark.p_group6
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which is not affected by other CRUD tests which are using
    # bookinfo
    tests.apply_namespaces(['istio-system'])
    tests.assert_pagination_feature()


@pytest.mark.p_ro_top_safe
@pytest.mark.p_group10
def test_namespaces(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_group10
def test_filter_options(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


# p_group_last is used for tests which must be run at the end when all other test are done
@pytest.mark.p_ro_top
@pytest.mark.p_group_last
def test_filter_feature_random(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_feature_random()


@pytest.mark.p_ro_top
@pytest.mark.p_group_last
def test_all_configs(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_config_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_random_details(namespaces=[namespace])
