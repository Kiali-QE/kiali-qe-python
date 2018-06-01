from kiali_qe.components.enums import ApplicationVersionEnum, HelpMenuEnum
from kiali_qe.pages import RootPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger


def test_about(browser, cfg, kiali_client):
    # load root page
    page = RootPage(browser, cfg)
    _about = page.navbar.about()
    assert _about.application_name == 'Kiali'
    versions_ui = _about.versions
    logger.debug('Versions information in UI:{}'.format(versions_ui))
    versions_defined = [item.text for item in ApplicationVersionEnum]
    logger.debug('Application version keys: defined:{}, available:{}'.format(
        versions_defined, versions_ui.keys()))
    assert is_equal(versions_defined, versions_ui.keys())

    # compare each versions
    # get version details from REST API
    _response = kiali_client.status()
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
    _products = _response['products']
    # check istio version
    assert versions_ui[ApplicationVersionEnum.ISTIO.text] == _get_version(_products, 'Istio')
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


def test_help_menu(browser, cfg):
    # load root page
    page = RootPage(browser, cfg)
    # test available menus
    options_defined = [item.text for item in HelpMenuEnum]
    options_listed = page.navbar.help_menu.options
    logger.debug('help menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Help menus mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
