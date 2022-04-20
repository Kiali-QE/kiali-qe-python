mport pytest
import os

from kiali_qe.components.enums import (
    ApplicationVersionEnum,
    HelpMenuEnum,
    ApplicationVersionUpstreamEnum
)
from kiali_qe.pages import RootPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger

ISTIO_SYSTEM = 'istio-system'


@pytest.mark.p_smoke
@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_about(browser, kiali_client):
    # load root page
    page = RootPage(browser)
    _about = page.navbar.about()
    assert _about.application_logo
    versions_ui = _about.versions
    _about.close()

    _response = kiali_client.get_response('getStatus')
    _products = _response['externalServices']

    if (any(d['name'] == ApplicationVersionEnum.ISTIO.text for d in _products)):
        version_enum = ApplicationVersionEnum
    else:
        version_enum = ApplicationVersionUpstreamEnum

    versions_defined = [item.text for item in version_enum]

    logger.debug('Versions information in UI:{}'.format(versions_ui))
    logger.debug('Application version keys: defined:{}, available:{}'.format(
        versions_defined, versions_ui.keys()))
    assert is_equal(versions_defined, versions_ui.keys())

    # compare each versions
    # get version details from REST API

    # kiali version
    _core_rest = '{}{}'.format(
        _response['status']['Kiali version'], ' ({})'.format(
            _response['status']['Kiali commit hash'])
        if _response['status']['Kiali commit hash'] != 'unknown' else '')
    # skip in case of code coverage run where the version is not set correctly during the build
    if "ENABLE_CODE_COVERAGE" not in os.environ or os.environ["ENABLE_CODE_COVERAGE"] != "true":
        assert versions_ui[version_enum.KIALI.text] == _core_rest

    # test other product versions

    assert versions_ui[version_enum.ISTIO.text] == _get_version(
        _products,
        version_enum.ISTIO.text)
    # check Prometheus version
    assert versions_ui[version_enum.PROMETHEUS.text] == _get_version(
        _products, 'Prometheus')
    # check Kubernetes version
    assert versions_ui[version_enum.KUBERNETES.text] == _get_version(
        _products, 'Kubernetes')


def _get_version(versions, key):
    for item in versions:
        if item['name'] == key:
            return item['version']


@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_help_menu(browser):
    # load root page
    page = RootPage(browser)
    # test available menus
    options_defined = [item.text for item in HelpMenuEnum]
    options_listed = page.navbar.help_menu.options
    logger.debug('help menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Help menus mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.p_atomic
@pytest.mark.p_ro_group8
def test_masthead_status(openshift_client, browser):
    # load root page
    page = RootPage(browser)
    oc_apps = openshift_client.get_failing_applications(ISTIO_SYSTEM)
    ui_statuses = page.navbar.get_masthead_tooltip()
    assert is_equal(oc_apps, list(ui_statuses.keys()))