import pytest

from kiali_qe.tests import ApplicationsPageTest

BOOKINFO_2 = 'bookinfo2'


@pytest.mark.p_ro_namespace
@pytest.mark.p_group9
def test_pagination_feature(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only istio-system namespace which contains sufficient number of items for this test
    tests.apply_namespaces(['istio-system'])
    tests.assert_pagination_feature()


@pytest.mark.p_ro_top_safe
@pytest.mark.p_group4
def test_namespaces(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_group4
def test_filter_options(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_group4
def test_all_applications(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_group4
def test_application_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_random_details(namespaces=[namespace])
