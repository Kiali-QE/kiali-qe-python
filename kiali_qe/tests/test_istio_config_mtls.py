import pytest

from kiali_qe.tests import OverviewPageTest
from kiali_qe.utils import get_yaml_path
from kiali_qe.utils.path import istio_objects_mtls_path
from kiali_qe.utils.command_exec import oc_apply, oc_delete
from kiali_qe.components.enums import MeshWideTLSType


'''
Tests are divided into groups using different services and namespaces. This way the group of tests
can be run in parallel.
'''

BOOKINFO = 'bookinfo'
SCENARIO_1 = "scenario1.yaml"
SCENARIO_2 = "scenario2.yaml"
SCENARIO_3 = "scenario3.yaml"
SCENARIO_4 = "scenario4.yaml"
SCENARIO_5 = "scenario5.yaml"
SCENARIO_6 = "scenario6.yaml"
SCENARIO_7 = "scenario7.yaml"
SCENARIO_8 = "scenario8.yaml"
SCENARIO_9 = "scenario9.yaml"
SCENARIO_10 = "scenario10.yaml"
SCENARIO_11 = "scenario11.yaml"
SCENARIO_12 = "scenario12.yaml"
SCENARIO_13 = "scenario13.yaml"
SCENARIO_14 = "scenario14.yaml"
SCENARIO_15 = "scenario15.yaml"
SCENARIO_16 = "scenario16.yaml"


@pytest.mark.p_group_last
def test_scenario1(kiali_client, openshift_client, browser):
    """ Policy is in permissive mode, it allows mTLS connections """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_1,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'disable-mtls', error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default', error_messages=[])
                        ])


@pytest.mark.p_group_last
def test_scenario2(kiali_client, openshift_client, browser):
    """ Policy explicitly asks for mTLS connections
        but DestinationRule disables workload mtls connections
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_2, namespace=BOOKINFO,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'disable-mtls',
                                error_messages=[
                                    'Policy with TLS strict mode found, it should be permissive']),
                            ConfigValidationObject(
                                'Policy', 'default',
                                error_messages=[
                                    'Destination Rule enabling namespace-wide mTLS is missing'])
                        ])


@pytest.mark.p_group_last
def test_scenario3(kiali_client, openshift_client, browser):
    """ MeshPolicy explicitly ask for mTLS connections
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_3, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'disable-mtls',
                                namespace=BOOKINFO,
                                error_messages=[
                                    'MeshPolicy enabling mTLS found, permissive policy is needed']),
                            ConfigValidationObject(
                                'MeshPolicy', 'default',
                                namespace='istio-system', error_messages=[]),
                            ConfigValidationObject(
                                'DestinationRule', 'default',
                                namespace='istio-system', error_messages=[])
                        ],
                        tls_type=MeshWideTLSType.ENABLED,
                        namespace_tls_objects=[
                            NamespaceTLSObject(
                                'bookinfo',
                                MeshWideTLSType.PARTLY_ENABLED),
                            NamespaceTLSObject(
                                'istio-system',
                                MeshWideTLSType.ENABLED),
                            NamespaceTLSObject(
                                'default',
                                MeshWideTLSType.ENABLED)
                        ])


@pytest.mark.p_group_last
def test_scenario4(kiali_client, openshift_client, browser):
    """ MeshPolicy allows non-mTLS connections in the service mesh
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_4, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'disable-mtls',
                                namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'MeshPolicy', 'default',
                                namespace='istio-system', error_messages=[]),
                            ConfigValidationObject(
                                'DestinationRule', 'default',
                                namespace='istio-system',
                                error_messages=[])
                        ],
                        tls_type=MeshWideTLSType.PARTLY_ENABLED,
                        namespace_tls_objects=[
                            NamespaceTLSObject(
                                'bookinfo',
                                MeshWideTLSType.PARTLY_ENABLED),
                            NamespaceTLSObject(
                                'istio-system',
                                MeshWideTLSType.DISABLED),
                            NamespaceTLSObject(
                                'default',
                                MeshWideTLSType.DISABLED)
                        ])


@pytest.mark.p_group_last
def test_scenario5(kiali_client, openshift_client, browser):
    """ There aren't any Policy defining mTLS settings
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_5, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'disable-mtls',
                                namespace=BOOKINFO, error_messages=[])
                        ],
                        tls_type=MeshWideTLSType.DISABLED,
                        namespace_tls_objects=[
                            NamespaceTLSObject(
                                'bookinfo',
                                MeshWideTLSType.PARTLY_ENABLED),
                            NamespaceTLSObject(
                                'istio-system',
                                MeshWideTLSType.DISABLED),
                            NamespaceTLSObject(
                                'default',
                                MeshWideTLSType.DISABLED)
                        ])


@pytest.mark.p_group_last
def test_scenario6(kiali_client, openshift_client, browser):
    """ Destination Rule valid: it doesn't define any mTLS setting
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_6,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'reviews', error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default',
                                error_messages=[
                                    'Destination Rule enabling namespace-wide mTLS is missing'])
                        ])


@pytest.mark.p_group_last
def test_scenario7(kiali_client, openshift_client, browser):
    """ classic ns-wide mTLS config
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_7, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule',
                                'enable-mtls', namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default',
                                namespace=BOOKINFO, error_messages=[])
                        ],
                        tls_type=MeshWideTLSType.DISABLED,
                        namespace_tls_objects=[
                            NamespaceTLSObject(
                                'bookinfo',
                                MeshWideTLSType.ENABLED),
                            NamespaceTLSObject(
                                'istio-system',
                                MeshWideTLSType.DISABLED),
                            NamespaceTLSObject(
                                'default',
                                MeshWideTLSType.DISABLED)
                        ])


@pytest.mark.p_group_last
def test_scenario8(kiali_client, openshift_client, browser):
    """ DR mesh-wide enables clients start mTLS connections
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_8,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                error_messages=['MeshPolicy enabling mTLS is missing']),
                            ConfigValidationObject(
                                'Policy', 'default', error_messages=[])
                        ],
                        tls_type=MeshWideTLSType.PARTLY_ENABLED)


@pytest.mark.p_group_last
def test_scenario9(kiali_client, openshift_client, browser):
    """ there isn't any Destination Rule enabling services start mTLS connection
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_9,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'Policy', 'default',
                                error_messages=[
                                    'Destination Rule enabling namespace-wide mTLS is missing'])
                        ])


@pytest.mark.p_group_last
def test_scenario10(kiali_client, openshift_client, browser):
    """ Permissive mode allow mTLS connections to services
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_10, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default',
                                namespace=BOOKINFO, error_messages=[])
                        ])


@pytest.mark.p_group_last
def test_scenario11(kiali_client, openshift_client, browser):
    """ STRICT mode allow only mTLS connections to services
    """

    _test_istio_objects(kiali_client, openshift_client, browser,
                        SCENARIO_11, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default',
                                namespace=BOOKINFO, error_messages=[])
                        ])


@pytest.mark.p_group_last
def test_scenario12(kiali_client, openshift_client, browser):
    """ STRICT mode allow only mTLS connections to services
    """

    _test_istio_objects(kiali_client, openshift_client, browser,
                        SCENARIO_12, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'MeshPolicy', 'default',
                                namespace='istio-system', error_messages=[])
                        ])


@pytest.mark.p_group_last
def test_scenario13(kiali_client, openshift_client, browser):
    """ STRICT mode allow only mTLS connections to services to the whole service mesh
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_13, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                namespace=BOOKINFO, error_messages=[]),
                            ConfigValidationObject(
                                'MeshPolicy', 'default',
                                namespace='istio-system',
                                error_messages=[
                                    'Mesh-wide Destination Rule enabling mTLS is missing'])
                        ],
                        tls_type=MeshWideTLSType.PARTLY_ENABLED)


@pytest.mark.p_group_last
def test_scenario14(kiali_client, openshift_client, browser):
    """ there isn't any policy enabling mTLS on service clients
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_14, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'enable-mtls',
                                namespace=BOOKINFO,
                                error_messages=[
                                    'Policy enabling namespace-wide mTLS is missing'])
                        ])


@pytest.mark.p_group_last
def test_scenario15(kiali_client, openshift_client, browser):
    """ MeshPolicy in STRICT mode + DestinationRule enabling mTLS mesh-wide (classic scenario)
        Policy ns-level in PERMISSIVE mode + DR disabling mTLS ns-wide.

    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_15, namespace=None,
                        config_validation_objects=[
                            ConfigValidationObject(
                                'DestinationRule', 'default',
                                namespace=BOOKINFO,
                                error_messages=[]),
                            ConfigValidationObject(
                                'Policy', 'default',
                                namespace=BOOKINFO,
                                error_messages=[])
                        ])


@pytest.mark.p_group_last
def test_scenario16(kiali_client, openshift_client, browser):
    """ MeshPolicy OK
    """

    _test_istio_objects(kiali_client, openshift_client, browser, SCENARIO_16, namespace=None,
                        config_validation_objects=[
                        ],
                        tls_type=MeshWideTLSType.ENABLED,
                        namespace_tls_objects=[
                            NamespaceTLSObject(
                                'bookinfo',
                                MeshWideTLSType.ENABLED),
                            NamespaceTLSObject(
                                'istio-system',
                                MeshWideTLSType.ENABLED),
                            NamespaceTLSObject(
                                'default',
                                MeshWideTLSType.ENABLED)
                        ])


def _istio_config_create(yaml_file, namespace):
    _istio_config_delete(yaml_file, namespace=namespace)

    oc_apply(yaml_file=yaml_file,
             namespace=namespace)


def _istio_config_delete(yaml_file, namespace):
    oc_delete(yaml_file=yaml_file,
              namespace=namespace)


def _test_istio_objects(kiali_client, openshift_client, browser, scenario, namespace=BOOKINFO,
                        config_validation_objects=[], tls_type=None, namespace_tls_objects=[]):
    """
        All the testing logic goes here.
        It creates the provided scenario yaml into provider namespace.
        And then validates the provided Istio objects if they have the error_messages

    """
    yaml_file = get_yaml_path(istio_objects_mtls_path.strpath, scenario)

    try:
        _istio_config_create(yaml_file, namespace=namespace)

        for _object in config_validation_objects:
            _test_validation_errors(kiali_client,
                                    object_type=_object.object_type,
                                    object_name=_object.object_name,
                                    namespace=_object.namespace,
                                    error_messages=_object.error_messages)

        if tls_type:
            _test_mtls_settings(kiali_client, openshift_client, browser, tls_type,
                                namespace_tls_objects)
    finally:
        _istio_config_delete(yaml_file, namespace=namespace)


def _test_validation_errors(kiali_client, object_type, object_name, namespace,
                            error_messages=[]):
    # get config detals from rest
    config_details_rest = kiali_client.istio_config_details(
        namespace=namespace,
        object_type=object_type,
        object_name=object_name)

    assert len(error_messages) == len(config_details_rest.error_messages), \
        'Error messages are different Expected:{}, Got:{}'.\
        format(error_messages,
               config_details_rest.error_messages)

    for error_message in error_messages:
        assert error_message in config_details_rest.error_messages, \
            'Error messages:{} is not in List:{}'.\
            format(error_message,
                   config_details_rest.error_messages)


def _test_mtls_settings(kiali_client, openshift_client, browser, tls_type, namespace_tls_objects):
    """
        Validates both Mesh-wide mTLS settings in toolbar,
        and namespace wide TLS settings per namespace in Overview page.
    """
    _tests = OverviewPageTest(
            kiali_client=kiali_client, openshift_client=openshift_client,
            browser=browser)
    actual_mtls_type = _tests.get_mesh_wide_tls()
    assert actual_mtls_type == tls_type, \
        'Mesh-wide TLS type expected: {} got: {}'.format(tls_type, actual_mtls_type)
    if namespace_tls_objects:
        overview_items = _tests.page.content.all_items
        for tls_object in namespace_tls_objects:
            for overview_item in overview_items:
                if overview_item.namespace == tls_object.namespace:
                    assert tls_object.tls_type == overview_item.tls_type, \
                        'Namespace TLS type expected: {} got: {}'.format(tls_object.tls_type,
                                                                         overview_item.tls_type)


class ConfigValidationObject(object):

    def __init__(self, object_type, object_name, namespace=BOOKINFO, error_messages=[]):
        self.namespace = namespace
        self.object_type = object_type
        self.object_name = object_name
        self.error_messages = error_messages


class NamespaceTLSObject(object):

    def __init__(self, namespace, tls_type):
        self.namespace = namespace
        self.tls_type = tls_type
