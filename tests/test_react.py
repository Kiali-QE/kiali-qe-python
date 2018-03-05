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
    time.sleep(5)
    for row in view.table:
        assert row
    search = view.search
    time.sleep(5)
    search.simple_search('sws')
    time.sleep(5)
    view.wait_displayed()
    search.is_empty
    for row in view.table:
        assert "sws" in row[0].text
    time.sleep(5)
"""
def test_graph(browser):"""
    
