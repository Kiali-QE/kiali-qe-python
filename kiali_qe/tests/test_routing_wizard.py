import pytest

from kiali_qe.tests import ServicesPageTest
from kiali_qe.components.enums import (
    RoutingWizardType,
    RoutingWizardLoadBalancer,
    RoutingWizardTLS
)

BOOKINFO_2 = 'bookinfo2'
HANDLER_NAME1 = 'handlerrule1'
HANDLER_NAME2 = 'handlerrule2'
SERVICE_ID1 = 'serviceid1'
SERVICE_ID2 = 'serviceid2'
SYSTEM_URL1 = 'systemurl1'
SYSTEM_URL2 = 'systemurl2'
ACCESS_TOKEN1 = 'token1'
ACCESS_TOKEN2 = 'token2'


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_weighted_routing_single(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'details'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.ISTIO_MUTUAL, load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                              gateway=True, include_mesh_gateway=True)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.SIMPLE, load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.LEAST_CONN,
                              gateway=False, include_mesh_gateway=False)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_matching_routing_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'reviews'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_MATCHING_ROUTING,
                              tls=RoutingWizardTLS.SIMPLE, load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.PASSTHROUGH,
                              gateway=True, include_mesh_gateway=True)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_MATCHING_ROUTING,
                              tls=None, load_balancer=False,
                              load_balancer_type=None,
                              gateway=True, include_mesh_gateway=False)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_suspend_traffic_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'ratings'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.SUSPEND_TRAFFIC,
                              tls=RoutingWizardTLS.SIMPLE, load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.RANDOM,
                              gateway=True, include_mesh_gateway=False)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_SUSPENDED_TRAFFIC,
                              tls=None, load_balancer=False,
                              load_balancer_type=None,
                              gateway=False, include_mesh_gateway=False)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_tls_mutual(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'details'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.MUTUAL, load_balancer=False,
                              load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                              gateway=False, include_mesh_gateway=False)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.MUTUAL, load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.PASSTHROUGH,
                              gateway=True, include_mesh_gateway=True)
    tests.test_routing_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_3scale_rule(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'details'
    _handler_create(kiali_client, HANDLER_NAME1, SERVICE_ID1, SYSTEM_URL1, ACCESS_TOKEN1)
    _handler_create(kiali_client, HANDLER_NAME2, SERVICE_ID2, SYSTEM_URL2, ACCESS_TOKEN2)
    tests.test_3scale_rule_create(name=name, namespace=namespace, handler_name=HANDLER_NAME1)
    tests.test_3scale_rule_update(name=name, namespace=namespace, handler_name=HANDLER_NAME2)
    tests.test_3scale_rule_delete(name=name, namespace=namespace)


def _handler_create(kiali_client, name, service_id, system_url, access_token):
    kiali_client.delete_three_scale_handler(name=name)
    kiali_client.create_three_scale_handler(name, service_id, system_url, access_token)
