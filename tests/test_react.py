import pytest
import unittest
import time

from project.react_view import TableView
"""
def test_button_click(browser):
    view = ButtonsView(browser)
    view.wait_displayed()
    assert view.defaultButton.active
    assert view.primaryButton.active"""

def test_table_view(browser):
    view = TableView(browser)
    view.wait_displayed()
    for row in view.table:
        assert row
    search = view.search
    search.simple_search('kube')
    view.wait_displayed()
    search.is_empty
    for row in view.table:
        assert row
