import pytest

from selenium.common.exceptions import NoSuchElementException
from kiali_qe.tests import ValidationsTest, ConfigValidationObject, ServiceValidationObject
from kiali_qe.utils.path import istio_objects_validation_path
from kiali_qe.components.error_codes import (
    KIA0205,
    KIA0401,
    KIA0301,
    KIA0302,
    KIA0201,
    KIA0202,
    KIA0203,
    KIA1102,
    KIA0701,
    KIA0601,
    KIA1104,
    KIA0204,
    KIA0001,
    KIA0004,
    KIA0002,
    KIA0003,
    KIA1103,
    KIA1004,
    KIA1006,
    KIA0105,
    KIA1106,
    KIA1107,
    KIA1101
)


'''
Tests are divided into groups using different services and namespaces. This way the group of tests
can be run in parallel.
'''

BOOKINFO = 'bookinfo'
BOOKINFO2 = 'bookinfo2'
ISTIO_SYSTEM = 'istio-system'
SCENARIO_1 = "two_gateways_same_host.yaml"
SCENARIO_2 = "no_matching_workload_gateway.yaml"
SCENARIO_3 = "more_destination_rules.yaml"
SCENARIO_4 = "no_matching_entry_registry.yaml"
SCENARIO_5 = "subset_label_not_found.yaml"
SCENARIO_6 = "missing_mesh_policy.yaml"
SCENARIO_7 = "mtls_settings_overridden.yaml"
SCENARIO_8 = "mesh_policy_permissive.yaml"
SCENARIO_9 = "mesh_policy_mtls_enable.yaml"
SCENARIO_10 = "non_existing_gateway.yaml"
SCENARIO_11 = "not_defined_protocol.yaml"
SCENARIO_12 = "destination_rule_fqdn.yaml"
SCENARIO_13 = "destination_rule_wrong_fqdn.yaml"
SCENARIO_14 = "ratings_java_svc.yaml"
SCENARIO_15 = "port_name_suffix_missing.yaml"
SCENARIO_16 = "virtual-service-less-than-100-weight.yaml"
SCENARIO_17 = "wrong-host-label-sidecar.yaml"
SCENARIO_18 = "duplicate-no-workload-sidecar.yaml"
SCENARIO_19 = "duplicate-workload-sidecar.yaml"
SCENARIO_20 = "default-sidecar-with-workload.yaml"
SCENARIO_21 = "mesh_policy_disable.yaml"
SCENARIO_22 = "auth-policy-mtls.yaml"
SCENARIO_23 = "vs_subset_service_entry.yaml"
SCENARIO_24 = "vs_wrong_subset_no_dr.yaml"
SCENARIO_25 = "duplicate-vs-gateway.yaml"
SCENARIO_26 = "vs_destination_host_not_found.yaml"
SCENARIO_27 = "request_auth_no_workload.yaml"
SCENARIO_28 = "two_gateways_different_selectors.yaml"


@pytest.mark.p_group_last
def test_two_gateways_same_host(kiali_client, openshift_client):
    """ More than one Gateway for the same host port combination
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_1, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0301]),
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto-copy',
                namespace=BOOKINFO2,
                error_messages=[KIA0301])
        ],
        ignore_common_errors=False)


@pytest.mark.p_group_last
def test_two_gateways_different_selectors(kiali_client, openshift_client):
    """ More than one Gateway for the same host port combination referring to different selectors
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_28, namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Gateway',
                object_name='istio-gateway-prv',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA0302]),
            ConfigValidationObject(
                object_type='Gateway',
                object_name='istio-gateway-pub',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA0302])
        ],
        ignore_common_errors=False)


@pytest.mark.p_group_last
def test_gateway_no_matching_workload(kiali_client, openshift_client):
    """ No matching workload found for gateway selector in this namespace
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_2, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto-not-match',
                namespace=BOOKINFO,
                error_messages=[KIA0302])
        ])


@pytest.mark.p_group_last
def test_more_drs_same_host_port(kiali_client, openshift_client):
    """ More than one DestinationRules for the same host subset combination
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_3, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr1-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0201]),
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr2-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0201])
        ],
        ignore_common_errors=False)


@pytest.mark.p_group_last
def test_no_matching_entry_dr(kiali_client, openshift_client):
    """ This host has no matching entry in the service registry
        (service, workload or service entries)
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_4, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-no-match-entry-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0202,
                                KIA0203,
                                KIA0203,
                                KIA0203])
        ])


@pytest.mark.p_group_last
def test_subset_label_not_found(kiali_client, openshift_client):
    """ This subset’s labels are not found in any matching host
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_5, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-no-subset-label-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0203,
                                KIA0203])
        ])


@pytest.mark.p_group_last
def test_mesh_policy_not_found(kiali_client, openshift_client):
    """ PeerAuthentication enabling mTLS is missing
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_6, namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA0205])
        ])


@pytest.mark.p_group_last
def test_mtls_settings_overridden(kiali_client, openshift_client):
    """ mTLS settings of a non-local Destination Rule are overridden
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_7, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA0205]),
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-overridden-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0204])
        ])


@pytest.mark.p_group_last
def test_meshpolicy_permissive_ok(kiali_client, openshift_client):
    """ PeerAuthentication enabling mTLS found, permissive policy is needed:
        PeerAuthentication to enable PERMISSIVE mode to all the workloads in the mesh
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_8, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                object_type='PeerAuthentication',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_meshpolicy_mtls_enable_ok(kiali_client, openshift_client):
    """ PeerAuthentication enabling mTLS found, permissive policy is needed:
        DestinatonRule to enable mTLS instead of disabling it (change the mode to ISTIO_MUTUAL)
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_9, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                object_type='PeerAuthentication',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA0401])
        ])


@pytest.mark.p_group_last
def test_vs_to_non_existing_gateway(kiali_client, openshift_client):
    """ VirtualService is pointing to a non-existent gateway
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_10, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='details-vs-non-existing-gateway-auto',
                namespace=BOOKINFO,
                error_messages=[KIA1102])
        ])


@pytest.mark.p_group_last
def test_vs_not_defined_protocol(kiali_client, openshift_client):
    """ VirtualService doesn’t define any route protocol
    """
    try:
        tests = ValidationsTest(
            kiali_client=kiali_client,
            openshift_client=openshift_client,
            objects_path=istio_objects_validation_path.strpath)
        tests.test_istio_objects(
            scenario=SCENARIO_11, namespace=BOOKINFO,
            config_validation_objects=[
                ConfigValidationObject(
                    object_type='VirtualService',
                    object_name='details-not-defined-protocol',
                    namespace=BOOKINFO,
                    error_messages=[KIA1103])
            ])
    except NoSuchElementException:
        # because vs should have protocol defined
        pass


@pytest.mark.p_group_last
def test_dr_fqdn_ok(kiali_client, openshift_client):
    """ Host in DR is given in FQDN
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_12, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr-fqdn-auto',
                namespace=BOOKINFO,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_dr_fqdn_not_exist(kiali_client, openshift_client):
    """ Host in DR is given in FQDN which does not exist
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_13, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr-wrong-fqdn-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0202,
                                KIA0203,
                                KIA0203,
                                KIA0203])
        ])


@pytest.mark.p_group_last
def test_deployment_port_not_found(kiali_client, openshift_client):
    """ Deployment exposing same port as Service not found
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_service_validation(
        scenario=SCENARIO_14, service_name='ratings-java',
        namespace='bookinfo',
        service_validation_objects=[
            ServiceValidationObject(
                error_message=KIA0701)])


@pytest.mark.p_group_last
def test_port_name_suffix(kiali_client, openshift_client):
    """ Port name must follow <protocol>[-suffix] form
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_service_validation(
        scenario=SCENARIO_15, service_name='ratings-java-svc-suffix',
        namespace='bookinfo',
        service_validation_objects=[
            ServiceValidationObject(
                error_message=KIA0601)])


@pytest.mark.p_group_last
def test_vs_less_than_100_weight(kiali_client, openshift_client):
    """ VirtualService has only weight < 100
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_16, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='virtual-service-less-100-weight-auto',
                namespace=BOOKINFO,
                error_messages=[KIA1104])
        ])


@pytest.mark.p_group_last
def test_sidecar_errors(kiali_client, openshift_client):
    """ Multiple errors
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_17, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='wrong-host-sidecar-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0004,
                                KIA0001,
                                KIA1004])
        ])


@pytest.mark.p_group_last
def test_duplicate_sidecar_errors(kiali_client, openshift_client):
    """ More than one selector-less Sidecar in the same namespace
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_18, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='dupliacate-sidecar1-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0002]),
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='dupliacate-sidecar2-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0002])
        ])


@pytest.mark.p_group_last
def test_duplicate_workload_sidecar_errors(kiali_client, openshift_client):
    """ More than one selector-less Sidecar in the same namespace
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_19, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='dupliacate-workload-sidecar1-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0003]),
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='dupliacate-workload-sidecar2-auto',
                namespace=BOOKINFO,
                error_messages=[KIA0003])
        ])


@pytest.mark.p_group_last
def test_default_workload_sidecar(kiali_client, openshift_client):
    """ Global default sidecar should not have workloadSelector
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_20, namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Sidecar',
                object_name='default-sidecar-workload-auto',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA1006, KIA0004])
        ])


@pytest.mark.p_group_last
def test_meshpolicy_disabled_ok(kiali_client, openshift_client):
    """ PeerAuthentication disabling mtls for the whole namespace (mode = DISABLE)
        Destination Rule disabling mTLS for a whole namespace (mode = DISABLE)
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_21, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='disable-mtls',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                object_type='PeerAuthentication',
                object_name='default',
                namespace=BOOKINFO,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_authpolicy_validations_mtls(kiali_client, openshift_client):
    """ KIA0105 This field requires mTLS to be enabled
        from.source.{namespaces | notNamespaces | principals | notPrincipals}
        when.key = {source.principal | source.namespace | connection.sni }
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_22, namespace=BOOKINFO2,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='AuthorizationPolicy',
                object_name='authpolicymtls',
                namespace=BOOKINFO2,
                error_messages=([KIA0105, KIA0105, KIA0105, KIA0105, KIA0105, KIA0105, KIA0105]
                                if not openshift_client.is_auto_mtls() else []))
        ])


@pytest.mark.p_group_last
def test_vs_subset_validations_service_entry(kiali_client, openshift_client):
    """ KIA1107 Subset found as ServiceEntry exists
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_23, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='orahub-vs',
                namespace=BOOKINFO,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_vs_subset_validations_no_service_entry(kiali_client, openshift_client):
    """ KIA1107 Subset not found as ServiceEntry missing
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_24, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='orahub-vs-no-dr',
                namespace=BOOKINFO,
                error_messages=[KIA1107, KIA1107])
        ])


@pytest.mark.p_group_last
def test_vs_duplicate_gateway(kiali_client, openshift_client):
    """ KIA1106 More than one Virtual Service for same host
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_25, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='admin-vs-2',
                namespace=BOOKINFO,
                error_messages=[KIA1106]),
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='admin-vs',
                namespace=BOOKINFO,
                error_messages=[KIA1106]),
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='user-vs-2',
                namespace=BOOKINFO,
                error_messages=[KIA1106]),
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='user-vs',
                namespace=BOOKINFO,
                error_messages=[KIA1106])
        ])


@pytest.mark.p_group_last
def test_vs_destination_host_not_found(kiali_client, openshift_client):
    """ KIA1101 DestinationWeight on route doesn't have a
            valid service (host not found)
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_26, namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='foo-dev',
                namespace=ISTIO_SYSTEM,
                error_messages=[KIA1101])
        ])


@pytest.mark.p_group_last
def test_request_auth_workload_not_found(kiali_client, openshift_client):
    """ KIA0003, KIA0004, KIA0002
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
        openshift_client=openshift_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_27, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-dup-1',
                namespace=BOOKINFO,
                error_messages=[KIA0003]),
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-dup-2',
                namespace=BOOKINFO,
                error_messages=[KIA0003]),
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-matching',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-no-matching',
                namespace=BOOKINFO,
                error_messages=[KIA0004]),
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-ns-wise',
                namespace=BOOKINFO,
                error_messages=[KIA0002]),
            ConfigValidationObject(
                object_type='RequestAuthentication',
                object_name='httpbin-ns-wise-1',
                namespace=BOOKINFO,
                error_messages=[KIA0002])
        ])
