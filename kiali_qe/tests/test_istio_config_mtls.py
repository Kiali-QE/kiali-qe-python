import pytest

from kiali_qe.tests import ValidationsTest, ConfigValidationObject, NamespaceTLSObject
from kiali_qe.utils.path import istio_objects_mtls_path
from kiali_qe.components.enums import MeshWideTLSType
from kiali_qe.components.error_codes import (
    KIA0207,
    KIA0501,
    KIA0208,
    KIA0205,
    KIA0401,
    KIA0206
)

'''
Tests are divided into groups using different services and namespaces. This way the group of tests
can be run in parallel.
'''

BOOKINFO = 'bookinfo'
ISTIO_SYSTEM = 'istio-system'
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
SCENARIO_17 = "scenario17.yaml"
SCENARIO_18 = "scenario18.yaml"
SCENARIO_19 = "scenario19.yaml"
SCENARIO_20 = "scenario20.yaml"
SCENARIO_21 = "scenario21.yaml"


@pytest.mark.p_group_last
def test_scenario1(kiali_client, openshift_client, browser):
    """ PeerAuthentication is in permissive mode, it allows mTLS connections """

    tests = ValidationsTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
            objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(SCENARIO_1,
                             namespace=BOOKINFO,
                             config_validation_objects=[
                                 ConfigValidationObject(
                                     'DestinationRule', 'disable-mtls', namespace=BOOKINFO,
                                     error_messages=[]),
                                 ConfigValidationObject(
                                     'PeerAuthentication', 'default', namespace=BOOKINFO,
                                     error_messages=[])
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
def test_scenario2(kiali_client, openshift_client, browser):
    """ PeerAuthentication explicitly asks for mTLS connections
        but DestinationRule disables workload mtls connections
    """

    tests = ValidationsTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
            objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_2, namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                 'DestinationRule', 'disable-mtls',
                 namespace=BOOKINFO,
                 error_messages=[KIA0207]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[KIA0501])
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
def test_scenario3(kiali_client, openshift_client, browser):
    """ PeerAuthentication explicitly ask for mTLS connections
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_3, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'disable-mtls',
                namespace=BOOKINFO,
                error_messages=[KIA0208]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
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
    """ PeerAuthentication allows non-mTLS connections in the service mesh
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_4, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'disable-mtls',
                namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace='istio-system', error_messages=[]),
            ConfigValidationObject(
                'DestinationRule', 'default',
                namespace='istio-system',
                error_messages=[])
        ],
        tls_type=(MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                  else MeshWideTLSType.DISABLED),
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
    """ There aren't any PeerAuthentication defining mTLS settings
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_5, namespace=None,
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

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_6,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'reviews', namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[KIA0501])
        ],
        tls_type=MeshWideTLSType.DISABLED,
        namespace_tls_objects=[
            NamespaceTLSObject(
                'bookinfo',
                (MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                 else MeshWideTLSType.ENABLED)),
            NamespaceTLSObject(
                'istio-system',
                MeshWideTLSType.DISABLED),
            NamespaceTLSObject(
                'default',
                MeshWideTLSType.DISABLED)
        ])


@pytest.mark.p_group_last
def test_scenario7(kiali_client, openshift_client, browser):
    """ classic ns-wide mTLS config
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_7, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule',
                'enable-mtls', namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
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

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_8,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO,
                error_messages=[KIA0205]),
            ConfigValidationObject(
                'PeerAuthentication', 'default', namespace=BOOKINFO,
                error_messages=[])
        ],
        tls_type=(MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                  else MeshWideTLSType.DISABLED))


@pytest.mark.p_group_last
def test_scenario9(kiali_client, openshift_client, browser):
    """ there isn't any Destination Rule enabling services start mTLS connection
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_9,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[KIA0501])
        ])


@pytest.mark.p_group_last
def test_scenario10(kiali_client, openshift_client, browser):
    """ Permissive mode allow mTLS connections to services
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_10, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO, error_messages=[])
        ])


@pytest.mark.p_group_last
def test_scenario11(kiali_client, openshift_client, browser):
    """ STRICT mode allow only mTLS connections to services
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_11, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO, error_messages=[])
        ])


@pytest.mark.p_group_last
def test_scenario12(kiali_client, openshift_client, browser):
    """ PERMISSIVE mode allow mTLS connections to services to the whole mesh
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_12, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace='istio-system', error_messages=[])
        ])


@pytest.mark.p_group_last
def test_scenario13(kiali_client, openshift_client, browser):
    """ STRICT mode allow only mTLS connections to services to the whole service mesh
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_13, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO, error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace='istio-system',
                error_messages=[KIA0401])
        ],
        tls_type=(MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                  else MeshWideTLSType.ENABLED))


@pytest.mark.p_group_last
def test_scenario14(kiali_client, openshift_client, browser):
    """ there isn't any policy enabling mTLS on service clients
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_14, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO,
                error_messages=[KIA0206])
        ])


@pytest.mark.p_group_last
def test_scenario15(kiali_client, openshift_client, browser):
    """ PeerAuthentication in STRICT mode + DestinationRule enabling mTLS mesh-wide (classic scenario)
        PeerAuthentication ns-level in PERMISSIVE mode + DR disabling mTLS ns-wide.

    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_15, namespace=None,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'default',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[])
        ])


@pytest.mark.p_group_last
def test_scenario16(kiali_client, openshift_client, browser):
    """ PeerAuthentication OK
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_16, namespace=None,
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


@pytest.mark.p_group_last
def test_scenario17(kiali_client, openshift_client, browser):
    """ Destination Rule valid: it doesn't define any mTLS setting
        PeerAuth: STRICT
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_17,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'reviews', namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[KIA0501])
        ],
        tls_type=MeshWideTLSType.DISABLED,
        namespace_tls_objects=[
            NamespaceTLSObject(
                'bookinfo',
                (MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                 else MeshWideTLSType.ENABLED)),
            NamespaceTLSObject(
                'istio-system',
                MeshWideTLSType.DISABLED),
            NamespaceTLSObject(
                'default',
                MeshWideTLSType.DISABLED)
        ])


@pytest.mark.p_group_last
def test_scenario18(kiali_client, openshift_client, browser):
    """ Destination Rule valid: ISTIO_MUTUAL
        PeerAuth: PERMISSIVE
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_18,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'enable-mtls',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[])
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
def test_scenario19(kiali_client, openshift_client, browser):
    """ Destination Rule valid: Empty
        PeerAuth: DISABLE
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_19,
        namespace=BOOKINFO,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'reviews',
                namespace=BOOKINFO,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=BOOKINFO,
                error_messages=[])
        ],
        tls_type=MeshWideTLSType.DISABLED,
        namespace_tls_objects=[
            NamespaceTLSObject(
                'bookinfo',
                (MeshWideTLSType.PARTLY_ENABLED if not openshift_client.is_auto_mtls()
                 else MeshWideTLSType.DISABLED)),
            NamespaceTLSObject(
                'istio-system',
                MeshWideTLSType.DISABLED),
            NamespaceTLSObject(
                'default',
                MeshWideTLSType.DISABLED)
        ])


@pytest.mark.p_group_last
def test_scenario20(kiali_client, openshift_client, browser):
    """ Destination Rule valid: ISTIO_MUTUAL
        PeerAuth: DISABLE
    """

    tests = ValidationsTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
        objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(
        SCENARIO_20,
        namespace=ISTIO_SYSTEM,
        config_validation_objects=[
            ConfigValidationObject(
                'DestinationRule', 'default',
                namespace=ISTIO_SYSTEM,
                error_messages=[]),
            ConfigValidationObject(
                'PeerAuthentication', 'default',
                namespace=ISTIO_SYSTEM,
                error_messages=[])
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
def test_scenario21(kiali_client, openshift_client, browser):
    """ PeerAuthentication is DISABLE
        DestinationRule is DISABLE
    """

    tests = ValidationsTest(
            kiali_client=kiali_client, openshift_client=openshift_client, browser=browser,
            objects_path=istio_objects_mtls_path.strpath)
    tests.test_istio_objects(SCENARIO_21,
                             namespace=BOOKINFO,
                             config_validation_objects=[
                                 ConfigValidationObject(
                                     'DestinationRule', 'disable-mtls', namespace=BOOKINFO,
                                     error_messages=[]),
                                 ConfigValidationObject(
                                     'PeerAuthentication', 'default', namespace=BOOKINFO,
                                     error_messages=[])
                                 ],
                             tls_type=MeshWideTLSType.DISABLED,
                             namespace_tls_objects=[
                                NamespaceTLSObject(
                                    'bookinfo',
                                    MeshWideTLSType.DISABLED),
                                NamespaceTLSObject(
                                    'istio-system',
                                    MeshWideTLSType.DISABLED),
                                NamespaceTLSObject(
                                    'default',
                                    MeshWideTLSType.DISABLED)
                             ])
