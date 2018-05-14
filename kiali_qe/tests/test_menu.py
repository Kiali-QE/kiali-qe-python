from kiali_qe.components.enums import MainMenuEnum
from kiali_qe.pages import RootPage
from kiali_qe.tests.common import check_equal
from kiali_qe.utils.log import logger


def test_menu(browser):
    # load root page
    page = RootPage(browser)
    # test available menus
    options_defined = [item.text for item in MainMenuEnum]
    options_listed = page.main_menu.items
    logger.debug('menus[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert check_equal(options_defined, options_listed), \
        ('Menus mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
    # navigate to menus
    for _menu in options_listed:
        logger.debug('Testing menu: {}'.format(_menu))
        page.main_menu.select(_menu)
        assert page.main_menu.selected == _menu


def test_toggle(browser):
    # load root page
    page = RootPage(browser)
    page.main_menu.collapse()
    assert page.main_menu.is_collapsed
    page.main_menu.expand()
    assert not page.main_menu.is_collapsed
