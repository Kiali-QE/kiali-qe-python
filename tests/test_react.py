import pytest

from project import ButtonsView

def test_button_click(browser):
    view = TestView(browser)
    assert view.defaultButton.is_displayed
    assert view.button1.is_displayed
    assert view.button2.is_displayed
    assert view.button3.is_displayed
