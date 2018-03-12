# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import allure
import pytest
import yaml
import os
import sys

from selenium import webdriver

from widgetastic.browser import Browser

selenium_browser = None


class CustomBrowser(Browser):
    @property
    def product_version(self):
        return '1.0.0'


@pytest.fixture(scope='session')
def cfg():
    with open('conf/env.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg


@pytest.fixture(scope='session')
def selenium(request, cfg):
    webdriver_options = cfg['webdriver_options']
    desired_capabilities = webdriver_options['desired_capabilities']
    driver = webdriver.Remote(
        command_executor=webdriver_options['command_executor'],
        desired_capabilities={'platform': desired_capabilities['platform'],
                              'browserName': desired_capabilities['browserName'],
                              'unexpectedAlertBehaviour': desired_capabilities['unexpectedAlertBehaviour']}
        )
    request.addfinalizer(driver.quit)
    driver.maximize_window()
    global selenium_browser
    selenium_browser = driver
    return driver


@pytest.fixture(scope='function')
def browser(selenium, cfg):
    selenium.get(cfg['sws_url'])
    return CustomBrowser(selenium)


def pytest_exception_interact(node, call, report):
    if selenium_browser is not None:
        allure.attach(
            'Error screenshot', selenium_browser.get_screenshot_as_png(), allure.attach_type.PNG)
        allure.attach('Error traceback', str(report.longrepr), allure.attach_type.TEXT)
