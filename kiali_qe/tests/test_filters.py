import pytest

from kiali_qe.tests import (
    ServicesPageTest,
    ApplicationsPageTest,
    WorkloadsPageTest,
    IstioConfigPageTest
)
from kiali_qe.components.enums import (
    ServicesPageFilter,
    ApplicationsPageFilter,
    WorkloadsPageFilter,
    IstioConfigPageFilter,
    IstioSidecar,
    HealthType,
    WorkloadType,
    AppLabel,
    VersionLabel,
    IstioConfigObjectType,
    IstioConfigValidationType
)

FILTER_NAMESPACE = ['istio-system']
FILTER_PRESENT = IstioSidecar.PRESENT.text
FILTER_HEALTHY = HealthType.HEALTHY.text
FILTER_NAME = "test"
CONFIG_KEPT_FILTER = []


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_app_filters_kept(kiali_client, openshift_client, browser):
    app_filters = [
        {'name': ApplicationsPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': ApplicationsPageFilter.HEALTH.text, 'value': FILTER_HEALTHY},
        {'name': ApplicationsPageFilter.APP_NAME.text, 'value': FILTER_NAME}]

    kept_filters = [
        {'name': ApplicationsPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': ApplicationsPageFilter.HEALTH.text, 'value': FILTER_HEALTHY}]

    app_tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    app_tests.apply_namespaces(FILTER_NAMESPACE)
    app_tests.apply_filters(filters=app_filters)
    wl_tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    wl_tests.assert_applied_filters(kept_filters)
    wl_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    services_tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    services_tests.assert_applied_filters(kept_filters)
    services_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    config_tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    config_tests.assert_applied_filters(filters=CONFIG_KEPT_FILTER)
    config_tests.assert_applied_namespaces(FILTER_NAMESPACE)


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_workloads_filters_kept(kiali_client, openshift_client, browser):
    wr_filters = [
        {'name': WorkloadsPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': WorkloadsPageFilter.HEALTH.text, 'value': FILTER_HEALTHY},
        {'name': WorkloadsPageFilter.WORKLOAD_NAME.text, 'value': FILTER_NAME},
        {'name': WorkloadsPageFilter.WORKLOAD_TYPE.text, 'value': WorkloadType.DEPLOYMENT.text},
        {'name': WorkloadsPageFilter.APP_LABEL.text, 'value': AppLabel.PRESENT.text},
        {'name': WorkloadsPageFilter.VERSION_LABEL.text, 'value': VersionLabel.PRESENT.text}]

    kept_filters = [
        {'name': WorkloadsPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': WorkloadsPageFilter.HEALTH.text, 'value': FILTER_HEALTHY}]

    wl_tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    wl_tests.apply_namespaces(FILTER_NAMESPACE)
    wl_tests.apply_filters(wr_filters)
    app_tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    app_tests.assert_applied_filters(filters=kept_filters)
    app_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    services_tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    services_tests.assert_applied_filters(kept_filters)
    services_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    config_tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    config_tests.assert_applied_filters(filters=CONFIG_KEPT_FILTER)
    config_tests.assert_applied_namespaces(FILTER_NAMESPACE)


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_services_filters_kept(kiali_client, openshift_client, browser):
    services_filters = [
        {'name': ServicesPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': ServicesPageFilter.HEALTH.text, 'value': FILTER_HEALTHY},
        {'name': ServicesPageFilter.SERVICE_NAME.text, 'value': FILTER_NAME}]

    kept_filters = [
        {'name': ServicesPageFilter.ISTIO_SIDECAR.text, 'value': FILTER_PRESENT},
        {'name': ServicesPageFilter.HEALTH.text, 'value': FILTER_HEALTHY}]

    services_tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    services_tests.apply_namespaces(FILTER_NAMESPACE)
    services_tests.apply_filters(services_filters)
    app_tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    app_tests.assert_applied_filters(kept_filters)
    app_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    wl_tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    wl_tests.assert_applied_filters(kept_filters)
    wl_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    config_tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    config_tests.assert_applied_filters(filters=CONFIG_KEPT_FILTER)
    config_tests.assert_applied_namespaces(FILTER_NAMESPACE)


@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_config_filters_kept(kiali_client, openshift_client, browser):
    config_filters = [
        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
         'value': IstioConfigObjectType.DESTINATION_RULE.text},
        {'name': IstioConfigPageFilter.CONFIG.text, 'value': IstioConfigValidationType.VALID.text},
        {'name': IstioConfigPageFilter.ISTIO_NAME.text, 'value': FILTER_NAME}]

    config_tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    config_tests.apply_namespaces(FILTER_NAMESPACE)
    config_tests.apply_filters(filters=config_filters)
    services_tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    services_tests.assert_applied_filters(CONFIG_KEPT_FILTER)
    services_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    app_tests = ApplicationsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    app_tests.assert_applied_filters(CONFIG_KEPT_FILTER)
    app_tests.assert_applied_namespaces(FILTER_NAMESPACE)
    wl_tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    wl_tests.assert_applied_filters(CONFIG_KEPT_FILTER)
    wl_tests.assert_applied_namespaces(FILTER_NAMESPACE)
