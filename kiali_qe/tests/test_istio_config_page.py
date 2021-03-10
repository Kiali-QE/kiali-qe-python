import pytest
from kiali_qe.tests import IstioConfigPageTest
from kiali_qe.components.enums import (
    IstioConfigPageSort,
    IstioConfigPageFilter,
    IstioConfigObjectType,
    IstioConfigValidationType

)

BOOKINFO_2 = 'bookinfo2'
ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_ro_top_safe
@pytest.mark.p_ro_group4
def test_namespaces(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group4
def test_filter_options(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group4
def test_sort_options(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_filter_feature_random(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_feature_random()


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_all_configs(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_2_names(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": IstioConfigPageFilter.ISTIO_NAME.text, "value": "ratings"},
        {"name": IstioConfigPageFilter.ISTIO_NAME.text, "value": "reviews"}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_istiotype(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    for _type in IstioConfigObjectType:
        tests.apply_filters(filters=[
            {"name": IstioConfigPageFilter.ISTIO_TYPE.text, "value": _type.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_config_validation_valid(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": IstioConfigPageFilter.CONFIG.text, "value": IstioConfigValidationType.VALID.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_config_validation_warning(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": IstioConfigPageFilter.CONFIG.text,
         "value": IstioConfigValidationType.WARNING.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_config_validation_not_valid(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": IstioConfigPageFilter.CONFIG.text,
         "value": IstioConfigValidationType.NOT_VALID.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_configs_filter_config_validation_not_validated(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": IstioConfigPageFilter.CONFIG.text,
         "value": IstioConfigValidationType.NOT_VALIDATED.text}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group4
def test_all_configs_namespace(kiali_client, openshift_client, browser):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[ISTIO_SYSTEM],
                           sort_options=[IstioConfigPageSort.CONFIGURATION, True])


@pytest.mark.p_ro_namespace
@pytest.mark.p_ro_group4
def test_config_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_random_details(namespaces=[namespace])
