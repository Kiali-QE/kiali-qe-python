import pytest
import unittest
import time

from project.react_view import ButtonsView

def test_button_click(browser):
    view = ButtonsView(browser)
    assert view.defaultButton.active
    assert view.primaryButton.active
