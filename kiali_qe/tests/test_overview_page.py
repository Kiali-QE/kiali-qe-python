import pytest

from selenium.common.exceptions import StaleElementReferenceException
from kiali_qe.tests import OverviewPageTest
from kiali_qe.components.enums import (
    OverviewPageType,
    OverviewViewType,
    OverviewPageFilter,
    OverviewHealth,
    OverviewMTSLStatus
)
from kiali_qe.utils.command_exec import oc_idle

BOOKINFO_2 = 'bookinfo2'
BOOKINFO_3 = 'bookinfo3'


@pytest.mark.p_atomic
@pytest.mark.p_ro_group1
def test_filter_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group2
def test_sort_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_type_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_type_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_app_compact_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_services_compact_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_workloads_compact_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_app_expand_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_services_expand_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_workloads_expand_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_app_list_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_services_list_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_all_workloads_list_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_filter_overviews_by_label(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.LABEL.text, "value": "istio-injection:enabled"},
        {"name": OverviewPageFilter.LABEL.text, "value": "kiali.io/member-of:istio-system"}],
        list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_filter_overviews_by_single_namespace(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.NAME.text, "value": "bookinfo2"}],
        list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_filter_overviews_by_two_namespaces(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.NAME.text, "value": "bookinfo2"},
        {"name": OverviewPageFilter.NAME.text, "value": "bookinfo3"}],
        list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_crud_group4
def test_overview_auto_injection(kiali_client, openshift_client, browser, pick_namespace):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    try:
        tests.test_disable_enable_delete_auto_injection(namespace)
    except (StaleElementReferenceException):
        pass


@pytest.mark.p_ro_top
@pytest.mark.p_crud_group4
def test_overview_traffic_policies(kiali_client, openshift_client, browser, pick_namespace):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_3)
    tests.test_create_update_delete_traffic_policies(namespace)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_filter_overviews_by_health_failure(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.HEALTH.text, "value": OverviewHealth.FAILURE.text}],)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def __test_filter_overviews_by_health_degraded(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.HEALTH.text, "value": OverviewHealth.DEGRADED.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def __test_filter_overviews_by_health_healthy(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.HEALTH.text, "value": OverviewHealth.HEALTHY.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group3
def __test_filter_overviews_by_mtlsstatus_enabled(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.MTLS_STATUS.text, "value": OverviewMTSLStatus.ENABLED.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group2
def __test_filter_overviews_by_mtlsstatus_partiallyenabled(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.MTLS_STATUS.text, "value": OverviewMTSLStatus.PARENABLED.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group1
def __test_filter_overviews_by_mtlsstatus_disabled(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.MTLS_STATUS.text, "value": OverviewMTSLStatus.DISABLED.text}])


def _idle_bookinfo():
    oc_idle('mysqldb', 'bookinfo')
