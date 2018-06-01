from kiali_qe.components.enums import GraphPageFilter, GraphPageLayout
from kiali_qe.pages import GraphPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger


def test_layout(browser, cfg):
    # get page instance
    page = GraphPage(browser, cfg)
    # test options
    options_defined = [item.text for item in GraphPageLayout]
    options_listed = page.layout.options
    assert options_defined == options_listed, \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


def test_filter(browser, cfg):
    # get page instance
    page = GraphPage(browser, cfg)
    # test available filters
    options_defined = [item.text for item in GraphPageFilter]
    options_listed = page.filter.items
    logger.debug('options[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
    # enable disable each filter
    for filter_name in options_listed:
        _filter_test(page, filter_name)


def _filter_test(page, filter_name):
    # test filter checked
    page.filter.check(filter_name)
    assert page.filter.is_checked(filter_name) is True
    # test filter unchecked
    page.filter.uncheck(filter_name)
    assert page.filter.is_checked(filter_name) is False
