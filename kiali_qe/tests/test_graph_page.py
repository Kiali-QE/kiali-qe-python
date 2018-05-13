import pytest

from kiali_qe.components.enums import GraphPageLayout
from kiali_qe.pages import GraphPage


def test_layout(browser):
    # get page instance
    page = GraphPage(browser)
    # test options
    options_defined = [item.text for item in GraphPageLayout]
    options_listed = page.layout.options
    assert options_defined == options_listed, \
        ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


@pytest.mark.skip(reason="This page changed on recent version of GUI")
def test_buttons(browser):
    # get page instance
    page = GraphPage(browser)
    # test circuit breaker
    page.circuit_breaker.on()
    assert page.circuit_breaker.is_on is True
    page.circuit_breaker.off()
    assert page.circuit_breaker.is_on is False
    # test route_rules
    page.route_rules.on()
    assert page.route_rules.is_on is True
    page.route_rules.off()
    assert page.route_rules.is_on is False
    # test edge_labels
    page.edge_labels.on()
    assert page.edge_labels.is_on is True
    page.edge_labels.off()
    assert page.edge_labels.is_on is False
    # test node_labels
    page.node_labels.on()
    assert page.node_labels.is_on is True
    page.node_labels.off()
    assert page.node_labels.is_on is False
