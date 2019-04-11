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
    name = 'details'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_WEIGHTED_ROUTING)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_matching_routing_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'reviews'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_MATCHING_ROUTING)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_MATCHING_ROUTING)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_group5
def test_suspend_traffic_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'ratings'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.SUSPEND_TRAFFIC)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_SUSPENDED_TRAFFIC)
    tests.test_routing_delete(name=name, namespace=namespace)
