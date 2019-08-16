import pytest

from kiali_qe.components.enums import HelpMenuEnum, MainMenuEnum, UserMenuEnum
from kiali_qe.pages import RootPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger


@pytest.mark.p_atomic
@pytest.mark.p_ro_group5
def test_menu(browser, kiali_client):
    # load root page
    page = RootPage(browser)
    # test available menus
    _response = kiali_client.get_response('getStatus')
    _products = _response['externalServices']
    options_defined = [item.text for item in MainMenuEnum]
    if (any((d['name'] == 'Jaeger' and 'url' not in d) for d in _products)):
        options_defined.remove(MainMenuEnum.DISTRIBUTED_TRACING.value)
    options_listed = page.main_menu.items
    logger.debug('menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Menus mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
    # navigate to menus
    for _menu in options_listed:
        if str(_menu) == MainMenuEnum.DISTRIBUTED_TRACING.text:
            continue
        logger.debug('Testing menu: {}'.format(_menu))
        page.main_menu.select(_menu)
        assert page.main_menu.selected == _menu


@pytest.mark.p_atomic
@pytest.mark.p_ro_group5
def test_toggle(browser):
    # load root page
    page = RootPage(browser)
    page.main_menu.collapse()
    assert page.main_menu.is_collapsed
    page.main_menu.expand()
    assert not page.main_menu.is_collapsed


@pytest.mark.p_atomic
@pytest.mark.p_ro_group5
def test_help_menu(browser):
    # load root page
    page = RootPage(browser)
    options_defined = [item.text for item in HelpMenuEnum]
    options_listed = page.navbar.help_menu.options
    logger.debug('Menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Help menu mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.p_atomic
@pytest.mark.p_ro_group5
def test_user_menu(browser):
    # load root page
    page = RootPage(browser)
    options_defined = [item.text for item in UserMenuEnum]
    options_listed = page.navbar.user_menu.options
    logger.debug('Menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('User menu mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
