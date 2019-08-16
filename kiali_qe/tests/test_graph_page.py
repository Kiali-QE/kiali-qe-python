import pytest
from kiali_qe.components.enums import (
    GraphPageBadgesFilter,
    GraphPageDisplayFilter,
    GraphType,
    EdgeLabelsFilter,
    GraphPageDuration,
    GraphRefreshInterval
)
from kiali_qe.pages import GraphPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_duration(browser):
    # get page instance
    page = GraphPage(browser)
    # test options
    options_defined = [item.text for item in GraphPageDuration]
    duration = page.duration
    options_listed = duration.options
    logger.debug('Options[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_refresh_interval(browser):
    # get page instance
    page = GraphPage(browser)
    # test options
    options_defined = [item.text for item in GraphRefreshInterval]
    interval = page.interval
    options_listed = interval.options
    logger.debug('Options[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_type(browser):
    # get page instance
    page = GraphPage(browser)
    # test options
    options_defined = [item.text for item in GraphType]
    type = page.type
    options_listed = type.options
    assert is_equal(options_defined, options_listed), \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_filter(browser):
    # get page instance
    page = GraphPage(browser)
    # test available filters
    options_defined = [item.text for item in GraphPageBadgesFilter]
    for item in GraphPageDisplayFilter:
        options_defined.append(item.text)
    edge_options_defined = [item.text for item in EdgeLabelsFilter]
    options_listed = page.filter.items
    edge_options_listed = page.filter.radio_items
    logger.debug('Filter options[defined:{}, listed:{}]'
                 .format(options_defined, options_listed))
    logger.debug('Radio options[defined:{}, listed:{}]'
                 .format(edge_options_defined, edge_options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Filter Options mismatch: defined:{}, listed:{}'
         .format(options_defined, options_listed))
    assert is_equal(options_defined, options_listed), \
        ('Radio Options mismatch: defined:{}, listed:{}'
         .format(edge_options_defined, edge_options_listed))
    # enable disable each filter
    for filter_name in options_listed:
        _filter_test(page, filter_name)
    # select each filter in radio
    for filter_name in edge_options_listed:
        _filter_test(page, filter_name, uncheck=False)


def _filter_test(page, filter_name, uncheck=True):
    if filter_name == 'Service Nodes':  # with this option the whole graph is reloaded
        return
    # test filter checked
    page.filter.check(filter_name)
    assert page.filter.is_checked(filter_name) is True
    if uncheck:
        # test filter unchecked
        page.filter.uncheck(filter_name)
        assert page.filter.is_checked(filter_name) is False
