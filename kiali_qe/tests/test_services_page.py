import pytest

from kiali_qe.tests import ServicesPageTest
from kiali_qe.components.enums import ServicesPageSort, ServicesPageFilter, LabelOperation

BOOKINFO_2 = 'bookinfo2'
BOOKINFO_3 = 'bookinfo3'
ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_ro_top_safe
@pytest.mark.p_ro_group7
def test_namespaces(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_namespaces()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group7
def test_filter_options(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


@pytest.mark.p_atomic
@pytest.mark.p_ro_group7
def test_sort_options(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_sort_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_filter_feature_random(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_feature_random()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_all_services(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_services_filter_2_names(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.apply_filters(filters=[
        {"name": ServicesPageFilter.SERVICE_NAME.text, "value": "ratings"},
        {"name": ServicesPageFilter.SERVICE_NAME.text, "value": "reviews"}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_filter_service_by_label(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[
        {"name": ServicesPageFilter.LABEL.text, "value": "app:reviews"}])


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_filter_service_by_or_label(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[BOOKINFO_2],
                           filters=[
        {"name": ServicesPageFilter.LABEL.text, "value": "app:reviews"},
        {"name": ServicesPageFilter.LABEL.text, "value": "service"}],
        label_operation=LabelOperation.OR.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_filter_service_by_and_label(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[BOOKINFO_2],
                           filters=[
        {"name": ServicesPageFilter.LABEL.text, "value": "app"},
        {"name": ServicesPageFilter.LABEL.text, "value": "service"}],
        label_operation=LabelOperation.AND.text)


@pytest.mark.p_ro_top
@pytest.mark.p_ro_group7
def test_all_services_namespace(kiali_client, openshift_client, browser):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(namespaces=[ISTIO_SYSTEM], sort_options=[ServicesPageSort.HEALTH, True])


@pytest.mark.p_ro_namespace
@pytest.mark.p_ro_group7
def test_service_details_kiali(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_details(name='kiali', namespace=ISTIO_SYSTEM)


@pytest.mark.p_ro_namespace
@pytest.mark.p_ro_group7
def test_service_graph_overview(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    namespace = pick_namespace(BOOKINFO_3)
    tests.assert_graph_overview(name='details', namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_ro_group10
def test_service_details_random(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.assert_random_details(namespaces=[namespace])
