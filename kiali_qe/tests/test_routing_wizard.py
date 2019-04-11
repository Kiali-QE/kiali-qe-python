import pytest

from kiali_qe.tests import ServicesPageTest
from kiali_qe.components.enums import RoutingWizardType

BOOKINFO_2 = 'bookinfo2'


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_weighted_routing_single(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.test_routing_create(name='details', namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING)


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_matching_routing_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.test_routing_create(name='reviews', namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_MATCHING_ROUTING)


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_suspend_traffic_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    tests.test_routing_create(name='ratings', namespace=namespace,
                              routing_type=RoutingWizardType.SUSPEND_TRAFFIC)
