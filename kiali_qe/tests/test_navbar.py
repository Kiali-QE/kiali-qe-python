import pytest

from kiali_qe.components.enums import ApplicationVersionEnum, MaistraEnum, HelpMenuEnum
from kiali_qe.pages import RootPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_about(browser, kiali_client):
    # load root page
    page = RootPage(browser)
    _about = page.navbar.about()
    assert _about.application_logo
    versions_ui = _about.versions
    _about.close()

    _response = kiali_client.get_response('getStatus')
    _products = _response['externalServices']

    if (any(d['name'] == MaistraEnum.MAISTRA.text for d in _products)):
        versions_defined = [item.text for item in MaistraEnum]
    else:
        versions_defined = [item.text for item in ApplicationVersionEnum]

    logger.debug('Versions information in UI:{}'.format(versions_ui))
    logger.debug('Application version keys: defined:{}, available:{}'.format(
        versions_defined, versions_ui.keys()))
    assert is_equal(versions_defined, versions_ui.keys())

    # compare each versions
    # get version details from REST API

    # kiali core version
    _core_rest = '{} ({})'.format(
        _response['status']['Kiali core version'], _response['status']['Kiali core commit hash'])
    assert versions_ui[ApplicationVersionEnum.KIALI_CORE.text] == _core_rest

    # versions mismatch between console on UI
    # TODO: check with manual test team and enable this
    # _console_rest = '{} ({})'.format(
    #     _response['status']['Kiali core version'], _response['status']['Kiali console version'])
    # assert versions_ui[ApplicationVersionEnum.KIALI_UI.text] == _console_rest

    # test other product versions

    # If Maistra Project version exists, then Check Maistra version or check istio version

    if (any(d['name'] == MaistraEnum.MAISTRA.text for d in _products)):
        assert versions_ui[MaistraEnum.MAISTRA.text] == _get_version(_products,
                                                                     MaistraEnum.MAISTRA.text)
    else:
        assert versions_ui[ApplicationVersionEnum.ISTIO.text] == _get_version(
            _products,
            ApplicationVersionEnum.ISTIO.text)
    # check Prometheus version
    assert versions_ui[ApplicationVersionEnum.PROMETHEUS.text] == _get_version(
        _products, 'Prometheus')
    # check Kubernetes version
    assert versions_ui[ApplicationVersionEnum.KUBERNETES.text] == _get_version(
        _products, 'Kubernetes')


def _get_version(versions, key):
    for item in versions:
        if item['name'] == key:
            return item['version']


@pytest.mark.p_atomic
@pytest.mark.p_ro_group6
def test_help_menu(browser):
    # load root page
    page = RootPage(browser)
    # test available menus
    options_defined = [item.text for item in HelpMenuEnum]
    options_listed = page.navbar.help_menu.options
    logger.debug('help menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Help menus mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
