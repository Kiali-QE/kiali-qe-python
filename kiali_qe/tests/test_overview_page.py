import pytest

from selenium.common.exceptions import StaleElementReferenceException
from kiali_qe.tests import OverviewPageTest
from kiali_qe.components.enums import (
    OverviewPageType,
    OverviewViewType,
    OverviewPageFilter
)
from kiali_qe.utils.command_exec import oc_idle

BOOKINFO_2 = 'bookinfo2'


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_filter_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_sort_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_type_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_type_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_app_compact_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_services_compact_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_workloads_compact_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.COMPACT)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_app_expand_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_services_expand_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_workloads_expand_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.EXPAND)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_app_list_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.APPS,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_services_list_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.SERVICES,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_smoke
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_all_workloads_list_overviews(kiali_client, openshift_client, browser):
    _idle_bookinfo()
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[], overview_type=OverviewPageType.WORKLOADS,
                           list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_filter_overviews_by_label(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": OverviewPageFilter.LABEL.text, "value": "istio-injection:enabled"},
        {"name": OverviewPageFilter.LABEL.text, "value": "kiali.io/member-of:istio-system"}],
        list_type=OverviewViewType.LIST)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group6
def test_overview_auto_injection(kiali_client, openshift_client, browser, pick_namespace):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_2)
    try:
        tests.test_disable_enable_delete_auto_injection(namespace)
    except (StaleElementReferenceException):
        pass


def _idle_bookinfo():
    oc_idle('details', 'bookinfo')
