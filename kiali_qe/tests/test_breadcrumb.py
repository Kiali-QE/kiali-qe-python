import pytest

from kiali_qe.tests import (
    WorkloadsPageTest,
    ApplicationsPageTest,
    ServicesPageTest,
    IstioConfigPageTest
)

BOOKINFO_2 = 'bookinfo2'
ISTIO_SYSTEM = 'istio-system'


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group10
def test_workload_breadcrumb_menu(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_menu(name='details-v1', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group10
def test_workload_breadcrumb_namespace(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_namespace(name='details-v1', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_workload_breadcrumb_object(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_object(name='details-v1', namespace=namespace)


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_application_breadcrumb_menu(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_menu(name='details', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_application_breadcrumb_namespace(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_namespace(name='details', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_application_breadcrumb_object(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_object(name='details', namespace=namespace)


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_service_breadcrumb_menu(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_menu(name='details', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_service_breadcrumb_namespace(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_namespace(name='details', namespace=namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_service_breadcrumb_object(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_breadcrumb_object(name='details', namespace=namespace)


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_config_breadcrumb_menu(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_breadcrumb_menu(name='default', namespace=ISTIO_SYSTEM)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_config_breadcrumb_namespace(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_breadcrumb_namespace(name='default', namespace=ISTIO_SYSTEM)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def test_config_breadcrumb_object(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_breadcrumb_object(name='default', namespace=ISTIO_SYSTEM)
