import pytest
from openshift.dynamic.exceptions import InternalServerError
from kubernetes.client.rest import ApiException
from kiali_qe.tests import IstioConfigPageTest, ServicesPageTest

from kiali_qe.utils import get_yaml, get_dict
from kiali_qe.utils.path import istio_objects_path
from kiali_qe.components.enums import (
    IstioConfigObjectType,
    IstioConfigPageFilter,
    IstioConfigValidationType,
    AuthPolicyType,
    AuthPolicyActionType,
    MutualTLSMode
)
from kiali_qe.components.error_codes import (
    KIA0202,
    KIA0203,
    KIA0201,
    KIA1106,
    KIA1107,
    KIA0101,
    KIA0102,
    KIA1101,
    KIA0004,
    KIA0001,
    KIA1105
)

'''
Tests are divided into groups using different services and namespaces. This way the group of tests
can be run in parallel.
'''

BOOKINFO_1 = 'bookinfo'
BOOKINFO_2 = 'bookinfo2'
BOOKINFO_3 = 'bookinfo3'
REVIEWS = 'reviews'
DETAILS = 'details'
RATINGS = 'ratings'
DEST_RULE = 'destination-rule-cb-details.yaml'
DEST_RULE_VS_RATINGS = 'destination-rule-ratings.yaml'
DEST_RULE_VS_REVIEWS = 'destination-rule-reviews.yaml'
DEST_RULE_BROKEN = 'destination-rule-cb-broken.yaml'
DEST_RULE_WARNING = 'dest-rules-svc.yaml'
DEST_RULE_HOST_WARNING = 'destination-rule-host-wrong.yaml'
VIRTUAL_SERVICE = 'virtual-service.yaml'
VIRTUAL_SERVICE_SUBSET = 'virtual-service-subset-duplicate.yaml'
VIRTUAL_SERVICE_BROKEN = 'virtual-service-broken.yaml'
VIRTUAL_SERVICE_BROKEN_WEIGHT = 'virtual-service-broken-weight.yaml'
VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT = 'virtual-service-broken-weight-text.yaml'
VIRTUAL_SERVICE_SVC = 'virtual-service-svc.yaml'
VIRTUAL_SERVICE_SVC2 = 'virtual-service-svc2.yaml'
GATEWAY = 'gateway.yaml'
GATEWAY_LINK = 'gateway-link.yaml'
SERVICE_ENTRY = 'service-entry.yaml'
SERVICE_MESH_RBAC_CONFIG = 'service-mesh-rbac-config.yaml'
RBAC_CONFIG = 'rbac-config.yaml'
AUTH_POLICY = 'auth-policy.yaml'
SERVICE_ROLE = 'service-role.yaml'
SERVICE_ROLE_BROKEN = 'service-role-broken.yaml'
SERVICE_ROLE_BINDING = 'service-role-binding.yaml'
SERVICE_ROLE_BINDING_BROKEN = 'service-role-binding-broken.yaml'


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule(kiali_client, openshift_client, browser):
    destination_rule = get_yaml(istio_objects_path.strpath, DEST_RULE)
    destination_rule_dict = get_dict(istio_objects_path.strpath, DEST_RULE)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_dict,
                       destination_rule,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_rule_dict.metadata.name}
                        ],
                       namespace=BOOKINFO_1,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=DETAILS,
                       check_service_details=True)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_broken(kiali_client, openshift_client, browser):
    destination_rule_broken = get_yaml(istio_objects_path.strpath, DEST_RULE_BROKEN)
    destination_rule_broken_dict = get_dict(istio_objects_path.strpath, DEST_RULE_BROKEN)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_broken_dict,
                       destination_rule_broken,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.NOT_VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': destination_rule_broken_dict.metadata.name}
                        ],
                       namespace=BOOKINFO_2,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=DETAILS,
                       error_messages=[KIA0202, KIA0203],
                       check_service_details=True)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_svc_warning(kiali_client, openshift_client, browser):
    destination_rule_warning = get_yaml(istio_objects_path.strpath, DEST_RULE_WARNING)
    destination_rule_warning_dict = get_dict(istio_objects_path.strpath, DEST_RULE_WARNING)
    _create_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_warning_dict,
                       destination_rule_warning,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.WARNING.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': 'reviews-dr2-svc'}
                        ],
                       namespace=BOOKINFO_2,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=DETAILS,
                       error_messages=[KIA0201],
                       check_service_details=False)
    _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_destination_rule_host_warning(kiali_client, openshift_client, browser):
    destination_rule_warning = get_yaml(istio_objects_path.strpath, DEST_RULE_HOST_WARNING)
    destination_rule_warning_dict = get_dict(istio_objects_path.strpath, DEST_RULE_HOST_WARNING)

    _istio_config_test(kiali_client, openshift_client, browser,
                       destination_rule_warning_dict,
                       destination_rule_warning,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.DESTINATION_RULE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.WARNING.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': 'reviews-dr2-svc'}
                        ],
                       namespace=BOOKINFO_1,
                       kind='DestinationRule',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=DETAILS,
                       error_messages=[KIA0202],
                       check_service_details=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group5
def test_virtual_service(kiali_client, openshift_client, browser):
    gateway = get_yaml(istio_objects_path.strpath, GATEWAY_LINK)
    gateway_dict = get_dict(istio_objects_path.strpath, GATEWAY_LINK)
    _istio_config_create(openshift_client, gateway_dict, gateway,
                         'Gateway',
                         'networking.istio.io/v1alpha3',
                         namespace=BOOKINFO_2)
    virtual_service = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE)
    virtual_service_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE)
    _create_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)

    _istio_config_test(kiali_client, openshift_client, browser,
                       virtual_service_dict,
                       virtual_service,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.VIRTUAL_SERVICE.text},
                        {'name': IstioConfigPageFilter.CONFIG.text,
                         'value': IstioConfigValidationType.VALID.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': virtual_service_dict.metadata.name}
                        ],
                       namespace=BOOKINFO_2,
                       kind='VirtualService',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=REVIEWS,
                       check_service_details=False,
                       delete_istio_config=False)

    _vs_gateway_link_test(kiali_client, openshift_client, browser, gateway_dict,
                          kind='Gateway',
                          vs_name=virtual_service_dict.metadata.name,
                          namespace=BOOKINFO_2)
    _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)
    _delete_gateway_vs(openshift_client, GATEWAY_LINK)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_virtual_service_svc_warning(kiali_client, openshift_client, browser):
    virtual_service = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_SVC)
    virtual_service_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_SVC)
    _istio_config_create(openshift_client, virtual_service_dict, virtual_service,
                         'VirtualService',
                         'networking.istio.io/v1alpha3',
                         namespace=BOOKINFO_2)
    virtual_service2 = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_SVC2)
    virtual_service_dict2 = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_SVC2)
    _istio_config_create(openshift_client, virtual_service_dict2, virtual_service2,
                         'VirtualService',
                         'networking.istio.io/v1alpha3',
                         namespace=BOOKINFO_2)
    _create_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)

    _istio_config_details_test(kiali_client,
                               openshift_client,
                               browser,
                               virtual_service_dict,
                               virtual_service,
                               namespace=BOOKINFO_2,
                               kind='VirtualService',
                               api_version='networking.istio.io/v1alpha3',
                               error_messages=[KIA1106])
    _istio_config_details_test(kiali_client,
                               openshift_client,
                               browser,
                               virtual_service_dict2,
                               virtual_service2,
                               namespace=BOOKINFO_2,
                               kind='VirtualService',
                               api_version='networking.istio.io/v1alpha3',
                               error_messages=[KIA1106])
    _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_virtual_service_subset_warning(kiali_client, openshift_client, browser):
    gateway = get_yaml(istio_objects_path.strpath, GATEWAY)
    gateway_dict = get_dict(istio_objects_path.strpath, GATEWAY)
    _istio_config_create(openshift_client, gateway_dict, gateway,
                         'Gateway',
                         'networking.istio.io/v1alpha3',
                         namespace=BOOKINFO_1)
    virtual_service = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_SUBSET)
    virtual_service_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_SUBSET)
    _istio_config_create(openshift_client, virtual_service_dict, virtual_service,
                         'VirtualService',
                         'networking.istio.io/v1alpha3',
                         namespace=BOOKINFO_1)
    _create_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)

    _istio_config_details_test(kiali_client,
                               openshift_client,
                               browser,
                               virtual_service_dict,
                               virtual_service,
                               namespace=BOOKINFO_1,
                               kind='VirtualService',
                               api_version='networking.istio.io/v1alpha3',
                               error_messages=[KIA1105])
    _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_virtual_service_broken(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath, VIRTUAL_SERVICE_BROKEN)
    _create_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS, BOOKINFO_3)

    try:
        _istio_config_test(kiali_client, openshift_client, browser,
                           virtual_service_broken_dict,
                           virtual_service_broken,
                           [
                               {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                                'value': IstioConfigObjectType.VIRTUAL_SERVICE.text},
                               {'name': IstioConfigPageFilter.CONFIG.text,
                                'value': IstioConfigValidationType.NOT_VALID.text},
                               {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                                'value': virtual_service_broken_dict.metadata.name}
                            ],
                           namespace=BOOKINFO_3,
                           kind='VirtualService',
                           api_version='networking.istio.io/v1alpha3',
                           service_name=REVIEWS,
                           error_messages=[KIA1101, KIA1107],
                           check_service_details=True)
    finally:
        _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_REVIEWS)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group2
def test_virtual_service_broken_weight(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath,
                                      VIRTUAL_SERVICE_BROKEN_WEIGHT)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath,
                                           VIRTUAL_SERVICE_BROKEN_WEIGHT)
    try:
        _istio_config_create(
            openshift_client,
            virtual_service_broken_dict,
            virtual_service_broken,
            namespace=BOOKINFO_1,
            kind='VirtualService',
            api_version='networking.istio.io/v1alpha3')
        assert False, "'Weight sum should be 100' "\
            "error should be thrown, or Galley is not configured"
    except (ApiException, InternalServerError):
        pass


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_virtual_service_broken_weight_text(kiali_client, openshift_client, browser):
    virtual_service_broken = get_yaml(istio_objects_path.strpath,
                                      VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT)
    virtual_service_broken_dict = get_dict(istio_objects_path.strpath,
                                           VIRTUAL_SERVICE_BROKEN_WEIGHT_TEXT)
    try:
        _create_dest_rule_vs(openshift_client, DEST_RULE_VS_RATINGS)

        _istio_config_test(kiali_client, openshift_client, browser,
                           virtual_service_broken_dict,
                           virtual_service_broken,
                           [
                            {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                             'value': IstioConfigObjectType.VIRTUAL_SERVICE.text},
                            {'name': IstioConfigPageFilter.CONFIG.text,
                             'value': IstioConfigValidationType.NOT_VALID.text},
                            {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                             'value': virtual_service_broken_dict.metadata.name}
                            ],
                           namespace=BOOKINFO_1,
                           kind='VirtualService',
                           api_version='networking.istio.io/v1alpha3',
                           service_name=RATINGS,
                           error_messages=['Weight must be a number',
                                           'Weight sum should be 100'],
                           check_service_details=False)
        _delete_dest_rule_vs(openshift_client, DEST_RULE_VS_RATINGS)
    except (ApiException, InternalServerError):
        pass


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_gateway(kiali_client, openshift_client, browser, pick_namespace):
    gateway = get_yaml(istio_objects_path.strpath, GATEWAY)
    gateway_dict = get_dict(istio_objects_path.strpath, GATEWAY)
    namespace = pick_namespace(BOOKINFO_2)

    _istio_config_test(kiali_client, openshift_client, browser,
                       gateway_dict,
                       gateway,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.GATEWAY.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': gateway_dict.metadata.name}
                        ],
                       namespace=namespace,
                       kind='Gateway',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=REVIEWS,
                       check_service_details=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_gateway_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    gateway_name = 'gatewaytocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_gateways(openshift_client, gateway_name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_gateway_create(gateway_name, 'www.google.com', namespaces=namespaces)
    finally:
        _delete_gateways(openshift_client, gateway_name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_sidecar_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    sidecar_name = 'sidecartocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_sidecars(openshift_client, sidecar_name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_sidecar_create(name=sidecar_name, egress_host='bookinfo/details',
                                  labels='<name>=<value>', namespaces=namespaces)
    finally:
        _delete_sidecars(openshift_client, sidecar_name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_authpolicy_deny_all_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    authpolicy_name = 'authpolicydenyalltocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_authpolicy_create(name=authpolicy_name,
                                     policy=AuthPolicyType.DENY_ALL.text,
                                     namespaces=namespaces)
    finally:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_authpolicy_allow_all_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    authpolicy_name = 'authpolicyallowallcreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_authpolicy_create(name=authpolicy_name,
                                     policy=AuthPolicyType.ALLOW_ALL.text,
                                     namespaces=namespaces)
    finally:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_authpolicy_rules_allow_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    authpolicy_name = 'authpolicyrulesallowtocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_authpolicy_create(name=authpolicy_name,
                                     policy=AuthPolicyType.RULES.text,
                                     namespaces=namespaces,
                                     policy_action=AuthPolicyActionType.ALLOW.text)
    finally:
        _delete_authpolicies(openshift_client, authpolicy_name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_authpolicy_rules_deny_disabled(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    authpolicy_name = 'authpolicyrulesdenydisabled'
    namespaces = [BOOKINFO_1, namespace]
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.test_authpolicy_create(name=authpolicy_name,
                                 policy=AuthPolicyType.RULES.text,
                                 namespaces=namespaces,
                                 policy_action=AuthPolicyActionType.DENY.text)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_peerauth_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    name = 'peerauthtocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_peerauths(openshift_client, name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_peerauth_create(name=name, mtls_mode=MutualTLSMode.PERMISSIVE.text,
                                   labels='app=value', namespaces=namespaces,
                                   mtls_ports={'8080': MutualTLSMode.STRICT.text})
    finally:
        _delete_peerauths(openshift_client, name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_peerauth_create_disabled(kiali_client, openshift_client, browser, pick_namespace):
    """
    MTLS Ports require Labels
    """
    namespace = pick_namespace(BOOKINFO_2)
    name = 'peerauthtocreatedisabled'
    namespaces = [BOOKINFO_1, namespace]
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.test_peerauth_create(name=name, mtls_mode=MutualTLSMode.PERMISSIVE.text,
                               namespaces=namespaces,
                               expected_created=False,
                               mtls_ports={'8080': MutualTLSMode.STRICT.text})


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_requestauth_create(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    name = 'requestauthtocreate'
    namespaces = [BOOKINFO_1, namespace]
    try:
        _delete_requestauths(openshift_client, name, namespaces)
        tests = IstioConfigPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
        tests.test_requestauth_create(name=name,
                                      labels='app=value',
                                      namespaces=namespaces,
                                      jwt_rules={'issuer': 'value1'})
    finally:
        _delete_requestauths(openshift_client, name, namespaces)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group3
def test_requestauth_create_disabled(kiali_client, openshift_client, browser, pick_namespace):
    namespace = pick_namespace(BOOKINFO_2)
    name = 'requestauthtocreatedisabled'
    namespaces = [BOOKINFO_1, namespace]
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.test_requestauth_create(name=name,
                                  labels='app=value',
                                  namespaces=namespaces,
                                  jwt_rules={'audiences': 'value1'},
                                  expected_created=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group1
def test_service_entry(kiali_client, openshift_client, browser):
    yaml = get_yaml(istio_objects_path.strpath, SERVICE_ENTRY)
    _dict = get_dict(istio_objects_path.strpath, SERVICE_ENTRY)

    _istio_config_test(kiali_client, openshift_client, browser,
                       _dict,
                       yaml,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.SERVICE_ENTRY.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': _dict.metadata.name}
                        ],
                       namespace=BOOKINFO_1,
                       kind='ServiceEntry',
                       api_version='networking.istio.io/v1alpha3',
                       service_name=DETAILS,
                       check_service_details=False)


@pytest.mark.p_crud_resource
@pytest.mark.p_crud_group4
def test_auth_policy(kiali_client, openshift_client, browser):
    yaml = get_yaml(istio_objects_path.strpath, AUTH_POLICY)
    _dict = get_dict(istio_objects_path.strpath, AUTH_POLICY)

    _istio_config_test(kiali_client, openshift_client, browser,
                       _dict,
                       yaml,
                       [
                        {'name': IstioConfigPageFilter.ISTIO_TYPE.text,
                         'value': IstioConfigObjectType.AUTHORIZATION_POLICY.text},
                        {'name': IstioConfigPageFilter.ISTIO_NAME.text,
                         'value': _dict.metadata.name}
                        ],
                       namespace=BOOKINFO_2,
                       kind='AuthorizationPolicy',
                       api_version='security.istio.io/v1beta1',
                       service_name=DETAILS,
                       check_service_details=False,
                       error_messages=[KIA0101, KIA0102, KIA0004, KIA0001])


def _istio_config_create(openshift_client, config_dict, config_yaml, kind, api_version,
                         namespace=BOOKINFO_1):
    openshift_client.delete_istio_config(name=config_dict.metadata.name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)

    openshift_client.create_istio_config(body=config_yaml,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def _istio_config_delete(openshift_client, name, kind, api_version, namespace=BOOKINFO_1):
    openshift_client.delete_istio_config(name=name,
                                         namespace=namespace,
                                         kind=kind,
                                         api_version=api_version)


def _istio_config_list(kiali_client, name, namespace=BOOKINFO_1):
    return kiali_client.istio_config_list(namespaces=[namespace], config_names=[name])


def _ui_istio_config_delete(tests, name, namespace=BOOKINFO_1):
    tests.delete_istio_config(name=name,
                              namespace=namespace)


def _create_dest_rule_vs(openshift_client, destination_rule_conf, namespace=BOOKINFO_1):
    destination_rule = get_yaml(istio_objects_path.strpath, destination_rule_conf)
    destination_rule_dict = get_dict(istio_objects_path.strpath, destination_rule_conf)
    _istio_config_create(openshift_client, destination_rule_dict, destination_rule,
                         'DestinationRule',
                         'networking.istio.io/v1alpha3',
                         namespace)


def _delete_dest_rule_vs(openshift_client, destination_rule_conf, namespace=BOOKINFO_1):
    destination_rule_dict = get_dict(istio_objects_path.strpath, destination_rule_conf)
    _istio_config_delete(openshift_client, destination_rule_dict.metadata.name,
                         'DestinationRule',
                         'networking.istio.io/v1alpha3',
                         namespace)


def _create_gateway_vs(openshift_client, gateway_conf, namespace=BOOKINFO_1):
    gateway = get_yaml(istio_objects_path.strpath, gateway_conf)
    gateway_dict = get_dict(istio_objects_path.strpath, gateway_conf)
    _istio_config_create(openshift_client, gateway_dict, gateway,
                         'Gateway',
                         'networking.istio.io/v1alpha3',
                         namespace)


def _delete_gateway_vs(openshift_client, gateway_conf, namespace=BOOKINFO_1):
    gateway_dict = get_dict(istio_objects_path.strpath, gateway_conf)
    _istio_config_delete(openshift_client, gateway_dict.metadata.name,
                         'Gateway',
                         'networking.istio.io/v1alpha3',
                         namespace)


def _delete_gateways(openshift_client, name, namespaces):
    for namespace in namespaces:
        _istio_config_delete(openshift_client, name=name, kind='Gateway',
                             api_version='networking.istio.io/v1alpha3', namespace=namespace)


def _delete_sidecars(openshift_client, name, namespaces):
    for namespace in namespaces:
        _istio_config_delete(openshift_client, name=name, kind='Sidecar',
                             api_version='networking.istio.io/v1alpha3', namespace=namespace)


def _delete_authpolicies(openshift_client, name, namespaces):
    for namespace in namespaces:
        _istio_config_delete(openshift_client, name=name, kind='AuthorizationPolicy',
                             api_version='security.istio.io/v1beta1', namespace=namespace)


def _delete_peerauths(openshift_client, name, namespaces):
    for namespace in namespaces:
        _istio_config_delete(openshift_client, name=name, kind='PeerAuthentication',
                             api_version='security.istio.io/v1beta1', namespace=namespace)


def _delete_requestauths(openshift_client, name, namespaces):
    for namespace in namespaces:
        _istio_config_delete(openshift_client, name=name, kind='RequestAuthentication',
                             api_version='security.istio.io/v1beta1', namespace=namespace)


def _istio_config_test(kiali_client, openshift_client, browser, config_dict,
                       config_yaml, filters, namespace, kind, api_version,
                       service_name, check_service_details=False,
                       delete_istio_config=True,
                       error_messages=[]):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    if not namespace:
        namespace = BOOKINFO_1

    try:
        _istio_config_create(
            openshift_client, config_dict, config_yaml, kind, api_version, namespace)

        tests.assert_all_items(namespaces=[namespace], filters=filters)

        _istio_config_details_test(kiali_client,
                                   openshift_client,
                                   browser,
                                   config_dict,
                                   config_yaml,
                                   kind,
                                   api_version,
                                   namespace,
                                   error_messages=error_messages)

        if check_service_details:
            _service_details_test(kiali_client,
                                  openshift_client,
                                  browser,
                                  config_dict,
                                  config_yaml,
                                  kind,
                                  api_version,
                                  service_name,
                                  namespace)

        if delete_istio_config:
            _ui_istio_config_delete(tests, config_dict.metadata.name, namespace)
            assert len(_istio_config_list(kiali_client, config_dict.metadata.name, namespace)) == 0
    finally:
        if delete_istio_config:
            _istio_config_delete(openshift_client, config_dict.metadata.name,
                                 kind, api_version, namespace)


def _istio_config_details_test(kiali_client, openshift_client, browser, config_dict,
                               config_yaml, kind, api_version, namespace=BOOKINFO_1,
                               error_messages=[]):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    tests.assert_details(name=config_dict.metadata.name,
                         object_type=kind,
                         namespace=namespace,
                         error_messages=error_messages,
                         apply_filters=False)


def _service_details_test(kiali_client, openshift_client, browser, config_dict,
                          config_yaml, kind, api_version, service_name, namespace=BOOKINFO_1):
    tests = ServicesPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    tests.assert_details(name=service_name, namespace=namespace, force_refresh=True)


def _vs_gateway_link_test(kiali_client, openshift_client, browser, config_dict,
                          kind, vs_name, namespace=BOOKINFO_1):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)

    tests.load_details_page(vs_name, namespace, force_refresh=False, load_only=True)

    tests.click_on_gateway(config_dict.metadata.name, namespace)

    tests.assert_details(name=config_dict.metadata.name,
                         object_type=kind,
                         namespace=namespace,
                         error_messages=[],
                         apply_filters=False)
