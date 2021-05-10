import pytest

from kiali_qe.tests import ApplicationsPageTest
from kiali_qe.components.enums import (
    ApplicationsPageSort,
    ApplicationsPageFilter,
    LabelOperation,
    AppIstioSidecar,
    AppHealth
)


BOOKINFO = 'bookinfo'
BOOKINFO_2 = 'bookinfo2'
ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_ro_top_safe
@pytest.mark.p_ro_group5
def test_namespaces(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group1
def test_filter_options(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group1
def test_sort_options(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_all_applications(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_apps_filter_2_names(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": ApplicationsPageFilter.APP_NAME.text, "value": "ratings"},
        {"name": ApplicationsPageFilter.APP_NAME.text, "value": "reviews"}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_by_or_label(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.LABEL.text, "value": "version:v2"},
        {"name": ApplicationsPageFilter.LABEL.text, "value": "version:v3"}],
        label_operation=LabelOperation.OR.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_by_and_label(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.LABEL.text, "value": "version:v2"},
        {"name": ApplicationsPageFilter.LABEL.text, "value": "version:v3"}],
        label_operation=LabelOperation.AND.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group1
def test_all_applications_namespace(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[ISTIO_SYSTEM],
                           sort_options=[ApplicationsPageSort.HEALTH, True])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_application_graph_overview(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO)
    tests.assert_graph_overview(name='details', namespace=namespace)


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group1
def test_application_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO)
    tests.assert_random_details(namespaces=[namespace])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_istio_sidecar_present(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.ISTIO_SIDECAR.text, "value": AppIstioSidecar.PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_istio_sidecar_not_present(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.ISTIO_SIDECAR.text,
         "value": AppIstioSidecar.NOT_PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_health_healthy(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.HEALTH.text, "value": AppHealth.HEALTHY.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_filter_applications_health_degraded(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.HEALTH.text, "value": AppHealth.DEGRADED.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_filter_applications_health_failure(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.HEALTH.text, "value": AppHealth.FAILURE.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_filter_applications_health_no_health_information(kiali_client, openshift_client, browser):
    tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ApplicationsPageFilter.HEALTH.text, "value": AppHealth.NO_HEALTH_INFO.text}])
