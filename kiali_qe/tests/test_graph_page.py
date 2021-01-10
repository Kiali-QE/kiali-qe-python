import pytest
from kiali_qe.components.enums import (
    GraphPageBadgesFilter,
    GraphPageDisplayFilter,
    GraphType,
    GraphPageLayout,
    EdgeLabelsFilter,
    TimeIntervalUIText,
    GraphRefreshInterval
)
from kiali_qe.pages import GraphPage
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger

ISTIO_SYSTEM = 'istio-system'
BOOKINFO = 'bookinfo'


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_duration(browser):
    # get page instance
    page = GraphPage(browser)
    # test options
    options_defined = [item.text for item in TimeIntervalUIText]
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
    namespace = ISTIO_SYSTEM
    page.namespace.check(namespace)
    # test options
    options_defined = [item.text for item in GraphType]
    p_type = page.type
    side_panel = page.side_panel
    options_listed = p_type.options
    assert is_equal(options_defined, options_listed), \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
    for option in options_defined:
        p_type.select(option)
        assert namespace == side_panel.get_namespace()
        assert not side_panel.get_workload()
        assert not side_panel.get_service()
        assert not side_panel.get_application()


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
    assert is_equal(edge_options_defined, edge_options_listed), \
        ('Radio Options mismatch: defined:{}, listed:{}'
         .format(edge_options_defined, edge_options_listed))
    # enable disable each filter
    for filter_name in options_listed:
        _filter_test(page, filter_name)
    # select each filter in radio
    for filter_name in edge_options_listed:
        _filter_test(page, filter_name, uncheck=False)


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_find_hide(browser):
    # get page instance
    page = GraphPage(browser)
    page.namespace.check(BOOKINFO)
    # test find and hide inputs
    _find_text = 'version=v1'
    _hide_text = 'version=v2'
    page.graph_find.fill(_find_text)
    page.graph_hide.fill(_hide_text)
    assert _find_text == page.graph_find.text, \
        ('Find query mismatch: defined:{}, shown:{}'
         .format(_find_text, page.graph_find.text))
    assert _hide_text == page.graph_hide.text, \
        ('Hide query mismatch: defined:{}, shown:{}'
         .format(_hide_text, page.graph_hide.text))
    assert page.graph_find.is_clear_displayed
    assert page.graph_hide.is_clear_displayed
    # empty the find
    assert page.graph_find.clear()
    assert page.graph_find.is_empty
    assert '' == page.graph_find.text, \
        ('Find query mismatch: defined:{}, shown:{}'
         .format('', page.graph_find.text))
    # empty the hide
    assert page.graph_hide.clear()
    assert page.graph_hide.is_empty
    assert '' == page.graph_hide.text, \
        ('Hide query mismatch: defined:{}, shown:{}'
         .format('', page.graph_hide.text))
    assert not page.graph_find.is_clear_displayed
    assert not page.graph_hide.is_clear_displayed


@pytest.mark.p_atomic
@pytest.mark.p_ro_group3
def test_layout(browser):
    # get page instance
    page = GraphPage(browser)
    page.namespace.check(ISTIO_SYSTEM)
    # test default layout
    p_layout = page.layout
    active_items = p_layout.active_items
    assert [GraphPageLayout.DAGRE] == active_items, \
        ('Options mismatch: defined:{}, listed:{}'.format(GraphPageLayout.DAGRE, active_items))
    # test selected layout
    p_layout.check(GraphPageLayout.COLA)
    active_items = p_layout.active_items
    assert [GraphPageLayout.COLA] == active_items, \
        ('Options mismatch: defined:{}, listed:{}'.format(GraphPageLayout.COLA, active_items))
    p_layout.check(GraphPageLayout.COSE)
    active_items = p_layout.active_items
    assert [GraphPageLayout.COSE] == active_items, \
        ('Options mismatch: defined:{}, listed:{}'.format(GraphPageLayout.COSE, active_items))


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
