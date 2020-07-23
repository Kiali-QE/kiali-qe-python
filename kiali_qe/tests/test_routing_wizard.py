import pytest

from kiali_qe.tests import ServicesPageTest, WorkloadsPageTest
from kiali_qe.components.enums import (
    RoutingWizardType,
    RoutingWizardLoadBalancer,
    RoutingWizardTLS,
    IstioConfigObjectType,
    PeerAuthMode
)
from kiali_qe.tests import test_3scale_config_page as THREESCALE_TEST

BOOKINFO = 'bookinfo'
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
@pytest.mark.p_crud_group3
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
def test_routing_keep_advanced_settings(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'mysqldb'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.ISTIO_MUTUAL,
                              peer_auth_mode=PeerAuthMode.PERMISSIVE,
                              load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                              gateway=True, include_mesh_gateway=True)
    peerauth_details = kiali_client.istio_config_details(
        namespace=namespace,
        object_type=IstioConfigObjectType.PEER_AUTHENTICATION.text,
        object_name=name)
    assert '\"mode\": \"{}\"'.format(
        PeerAuthMode.PERMISSIVE.text) in peerauth_details.text
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_WEIGHTED_ROUTING,
                              skip_advanced=True)
    service_details = kiali_client.service_details(service_name=name, namespace=namespace)
    assert len(service_details.virtual_services) == 1
    vs_details = kiali_client.istio_config_details(
        namespace=namespace,
        object_type=IstioConfigObjectType.VIRTUAL_SERVICE.text,
        object_name=service_details.virtual_services[0].name)
    assert '\"gateways\": [\"bookinfo/bookinfo-gateway\", \"mesh\"]' in vs_details.text
    assert len(service_details.destination_rules) == 1
    dr_details = kiali_client.istio_config_details(
        namespace=namespace,
        object_type=IstioConfigObjectType.DESTINATION_RULE.text,
        object_name=service_details.destination_rules[0].name)
    assert '\"simple\": \"{}\"'.format(
        RoutingWizardLoadBalancer.ROUND_ROBIN.text) in dr_details.text
    assert '\"mode\": \"{}\"'.format(
        RoutingWizardTLS.ISTIO_MUTUAL.text) in dr_details.text
    peerauth_details = kiali_client.istio_config_details(
        namespace=namespace,
        object_type=IstioConfigObjectType.PEER_AUTHENTICATION.text,
        object_name=name)
    assert '\"mode\": \"{}\"'.format(
        PeerAuthMode.PERMISSIVE.text) in peerauth_details.text
    tests.test_routing_delete(name=name, namespace=namespace)
    assert not kiali_client.istio_config_list(
        namespaces=[namespace],
        config_names=[name])


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group6
def test_matching_routing_multi(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'ratings'
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
@pytest.mark.p_crud_group5
def test_tls_mutual(kiali_client, openshift_client, browser, pick_namespace):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'mongodb'
    tests.test_routing_create(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.CREATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.MUTUAL,
                              peer_auth_mode=PeerAuthMode.PERMISSIVE,
                              load_balancer=False,
                              load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                              gateway=False, include_mesh_gateway=False)
    tests.test_routing_update(name=name, namespace=namespace,
                              routing_type=RoutingWizardType.UPDATE_WEIGHTED_ROUTING,
                              tls=RoutingWizardTLS.UNSET,
                              peer_auth_mode=PeerAuthMode.UNSET,
                              load_balancer=True,
                              load_balancer_type=RoutingWizardLoadBalancer.PASSTHROUGH,
                              gateway=True, include_mesh_gateway=True)
    tests.test_routing_delete(name=name, namespace=namespace)
    assert not kiali_client.istio_config_list(
        namespaces=[namespace],
        config_names=[name])


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group5
def test_3scale_rule(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'details-v1'
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.HANDLER1)
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.HANDLER2)
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.RULE1, kind='rule')
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.RULE2, kind='rule')
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.INSTANCE1, kind='instance')
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.INSTANCE2, kind='instance')
    tests.test_3scale_link_create(name=name, namespace=namespace, service_id=SERVICE_ID1,
                                  rule_name=THREESCALE_TEST.RULE_NAME1)
    tests.test_3scale_link_delete(name=name, namespace=namespace)


@pytest.mark.p_ro_namespace
@pytest.mark.p_crud_group5
def test_3scale_link_auto_delete(kiali_client, openshift_client, browser, pick_namespace):
    tests = WorkloadsPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    """ Delete the Handler, Rule and Instance, the link should still exist in workload """
    # use only bookinfo2 namespace where colliding tests are in the same p_group
    namespace = pick_namespace(BOOKINFO_2)
    name = 'details-v1'
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.HANDLER1)
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.RULE1, kind='rule')
    THREESCALE_TEST.handler_create(openshift_client, THREESCALE_TEST.INSTANCE1, kind='instance')
    tests.test_3scale_link_create(name=name, namespace=namespace, service_id=SERVICE_ID1,
                                  rule_name=THREESCALE_TEST.RULE_NAME1)
    THREESCALE_TEST.handler_delete(openshift_client, THREESCALE_TEST.HANDLER_NAME1)
    THREESCALE_TEST.handler_delete(openshift_client, THREESCALE_TEST.RULE_NAME1, kind='rule')
    THREESCALE_TEST.handler_delete(openshift_client, THREESCALE_TEST.INSTANCE_NAME1,
                                   kind='instance')
    tests.test_3scale_link(name=name, namespace=namespace, exists=True)
