import pytest

from kiali_qe.tests import WorkloadsPageTest
from kiali_qe.components.enums import (
    WorkloadsPageSort,
    WorkloadType,
    WorkloadsPageFilter,
    LabelOperation,
    IstioSidecar,
    AppLabel,
    VersionLabel,
    WorkloadHealth
)

BOOKINFO = 'bookinfo'
BOOKINFO_2 = 'bookinfo2'
BOOKINFO_3 = 'bookinfo3'
ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_ro_top_safe
@pytest.mark.p_ro_group8
def test_namespaces(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_filter_options(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_sort_options(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_all_workloads(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_workloads_filter_2_names(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": WorkloadsPageFilter.WORKLOAD_NAME.text, "value": "ratings-v1"},
        {"name": WorkloadsPageFilter.WORKLOAD_NAME.text, "value": "reviews-v1"}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_workloads_filter_workloadtype(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    for _type in WorkloadType:
        tests.assert_all_items(filters=[
            {"name": WorkloadsPageFilter.WORKLOAD_TYPE.text, "value": _type.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_istio_sidecar_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.ISTIO_SIDECAR.text, "value": IstioSidecar.PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_istio_sidecar_not_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.ISTIO_SIDECAR.text, "value": IstioSidecar.NOT_PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_workloads_filter_health(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    for _status in WorkloadHealth:
        tests.apply_filters(filters=[
            {"name": WorkloadsPageFilter.HEALTH.text, "value": _status.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_app_label_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.APP_LABEL.text, "value": AppLabel.PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_app_label_not_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.APP_LABEL.text, "value": AppLabel.NOT_PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_version_label_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.VERSION_LABEL.text, "value": VersionLabel.PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group5
def test_workloads_filter_version_label_not_present(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.VERSION_LABEL.text, "value": VersionLabel.NOT_PRESENT.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_filter_workloads_by_or_label(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.LABEL.text, "value": "version:v2"},
        {"name": WorkloadsPageFilter.LABEL.text, "value": "app:ratings"}],
        label_operation=LabelOperation.OR.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group8
def test_filter_workloads_by_and_label(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": WorkloadsPageFilter.LABEL.text, "value": "version:v2"},
        {"name": WorkloadsPageFilter.LABEL.text, "value": "app:ratings"}],
        label_operation=LabelOperation.AND.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group9
def test_all_workloads_namespace(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[ISTIO_SYSTEM], sort_options=[WorkloadsPageSort.HEALTH, True])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group9
def test_workload_details_kiali(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_details(name='kiali',
                         namespace=ISTIO_SYSTEM,
                         workload_type=WorkloadType.DEPLOYMENT.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group9
def test_workload_graph_overview(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_graph_overview(name='details-v1', namespace=namespace)


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group10
def test_workload_details_random(kiali_client, openshift_client, browser):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_random_details(namespaces=[BOOKINFO])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group9
def test_workload_auto_injection(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_3)
    tests.test_disable_enable_delete_auto_injection(name='details-v1', namespace=namespace)
