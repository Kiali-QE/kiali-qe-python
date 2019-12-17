import pytest

from selenium.common.exceptions import NoSuchElementException
from kiali_qe.tests import ValidationsTest, ConfigValidationObject, ServiceValidationObject
from kiali_qe.utils.path import istio_objects_validation_path


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


@pytest.mark.p_group_last
def test_two_gateways_same_host(kiali_client):
    """ More than one Gateway for the same host port combination
    """
    error_message = 'More than one Gateway for the same host port combination'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_1, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto',
                namespace=BOOKINFO,
                error_messages=[error_message]),
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto-copy',
                namespace=BOOKINFO2,
                error_messages=[error_message])
        ],
        ignore_common_errors=False)


@pytest.mark.p_group_last
def test_gateway_no_matching_workload(kiali_client):
    """ No matching workload found for gateway selector in this namespace
    """
    error_message = 'No matching workload found for gateway selector in this namespace'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_2, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='Gateway',
                object_name='bookinfo-gateway-auto-not-match',
                namespace=BOOKINFO,
                error_messages=[error_message])
        ])


@pytest.mark.p_group_last
def test_more_drs_same_host_port(kiali_client):
    """ More than one Gateway for the same host port combination
    """
    error_message = 'More than one DestinationRules for the same host subset combination'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_3, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr1-auto',
                namespace=BOOKINFO,
                error_messages=[error_message]),
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr2-auto',
                namespace=BOOKINFO,
                error_messages=[error_message])
        ],
        ignore_common_errors=False)


@pytest.mark.p_group_last
def test_no_matching_entry_dr(kiali_client):
    """ This host has no matching entry in the service registry
        (service, workload or service entries)
    """
    error_message = 'This host has no matching entry in the service '\
        'registry (service, workload or service entries)'
    error_message2 = 'This subset\'s labels are not found in any matching host'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_4, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-no-match-entry-auto',
                namespace=BOOKINFO,
                error_messages=[error_message,
                                error_message2,
                                error_message2,
                                error_message2])
        ])


@pytest.mark.p_group_last
def test_subset_label_not_found(kiali_client):
    """ This subset’s labels are not found in any matching host
    """
    error_message = 'This subset\'s labels are not found in any matching host'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_5, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-no-subset-label-auto',
                namespace=BOOKINFO,
                error_messages=[error_message,
                                error_message])
        ])


@pytest.mark.p_group_last
def test_mesh_policy_not_found(kiali_client):
    """ MeshPolicy enabling mTLS is missing
    """
    error_message = 'MeshPolicy enabling mTLS is missing'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_6, namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[error_message])
        ])


@pytest.mark.p_group_last
def test_mtls_settings_overridden(kiali_client):
    """ mTLS settings of a non-local Destination Rule are overridden
    """
    error_message = 'mTLS settings of a non-local Destination Rule are overridden'
    error_message2 = 'MeshPolicy enabling mTLS is missing'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_7, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[error_message2]),
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-overridden-auto',
                namespace=BOOKINFO,
                error_messages=[error_message])
        ])


@pytest.mark.p_group_last
def test_meshpolicy_permissive_ok(kiali_client):
    """ MeshPolicy enabling mTLS found, permissive policy is needed:
        MeshPolicy to enable PERMISSIVE mode to all the workloads in the mesh
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
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
                object_type='MeshPolicy',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_meshpolicy_mtls_enable_ok(kiali_client):
    """ MeshPolicy enabling mTLS found, permissive policy is needed:
        DestinatonRule to enable mTLS instead of disabling it (change the mode to ISTIO_MUTUAL)
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
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
                object_type='MeshPolicy',
                object_name='default',
                namespace=ISTIO_SYSTEM,
                error_messages=['Mesh-wide Destination Rule enabling mTLS is missing'])
        ])


@pytest.mark.p_group_last
def test_vs_to_non_existing_gateway(kiali_client):
    """ VirtualService is pointing to a non-existent gateway
    """
    error_message = 'VirtualService is pointing to a non-existent gateway'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_10, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='details-vs-non-existing-gateway-auto',
                namespace=BOOKINFO,
                error_messages=[error_message])
        ])


@pytest.mark.p_group_last
def test_vs_not_defined_protocol(kiali_client):
    """ VirtualService doesn’t define any route protocol
    """
    error_message = 'VirtualService doesn\'t define any valid route protocol'
    try:
        tests = ValidationsTest(
            kiali_client=kiali_client,
            objects_path=istio_objects_validation_path.strpath)
        tests.test_istio_objects(
            scenario=SCENARIO_11, namespace=BOOKINFO,
            config_validation_objects=[
                ConfigValidationObject(
                    object_type='VirtualService',
                    object_name='details-not-defined-protocol',
                    namespace=BOOKINFO,
                    error_messages=[error_message])
            ])
    except NoSuchElementException:
        # because vs should have protocol defined
        pass


@pytest.mark.p_group_last
def test_dr_fqdn_ok(kiali_client):
    """ Host in DR is given in FQDN
    """
    tests = ValidationsTest(
        kiali_client=kiali_client,
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
def test_dr_fqdn_not_exist(kiali_client):
    """ Host in DR is given in FQDN which does not exist
    """
    error_message = 'This host has no matching entry in '\
        'the service registry (service, workload or service entries)'
    error_message2 = 'This subset\'s labels are not found in any matching host'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_13, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='DestinationRule',
                object_name='reviews-dr-wrong-fqdn-auto',
                namespace=BOOKINFO,
                error_messages=[error_message,
                                error_message2,
                                error_message2,
                                error_message2])
        ])


@pytest.mark.p_group_last
def test_deployment_port_not_found(kiali_client):
    """ Deployment exposing same port as Service not found
    """
    error_message = 'Deployment exposing same port as Service not found'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_service_validation(
        scenario=SCENARIO_14, service_name='ratings-java-svc',
        namespace='bookinfo',
        service_validation_objects=[
            ServiceValidationObject(
                error_message=error_message)])


@pytest.mark.p_group_last
def test_port_name_suffix(kiali_client):
    """ Port name must follow <protocol>[-suffix] form
    """
    error_message = 'Port name must follow <protocol>[-suffix] form'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_service_validation(
        scenario=SCENARIO_15, service_name='ratings-java-svc-suffix',
        namespace='bookinfo',
        service_validation_objects=[
            ServiceValidationObject(
                error_message=error_message)])


@pytest.mark.p_group_last
def test_vs_less_than_100_weight(kiali_client):
    """ VirtualService has only weight < 100
    """
    error_message = 'The weight is assumed to be 100 because there is only one route destination'
    tests = ValidationsTest(
        kiali_client=kiali_client,
        objects_path=istio_objects_validation_path.strpath)
    tests.test_istio_objects(
        scenario=SCENARIO_16, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                object_type='VirtualService',
                object_name='virtual-service-less-100-weight-auto',
                namespace=BOOKINFO,
                error_messages=[error_message])
        ])
