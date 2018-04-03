# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import allure
import pytest
import yaml
import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium import webdriver

from rest_api.kiali_api import KialiAPI
from cli.kiali_cli import KialiCli

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
    success = False
    # try to get the driver more times (workaround for zalenium issue in OS)
    for x in range(0, 3):
        try:
            driver = get_driver(cfg)
        except WebDriverException:
            print "Failed to create driver, trying again"
            time.sleep(5)
            continue
        success = True
        break
    # trying one more time
    if not success:
        time.sleep(5)
        driver = get_driver(cfg)
    request.addfinalizer(driver.quit)
    driver.maximize_window()
    global selenium_browser
    selenium_browser = driver
    return driver


def get_driver(cfg):
    print "Creating driver"
    webdriver_options = cfg['webdriver_options']
    desired_capabilities = webdriver_options['desired_capabilities']

    # set resolve_ip to false to make it work in cases when remote driver is running in OpenShift
    driver = webdriver.Remote(
        command_executor=RemoteConnection(webdriver_options['command_executor'],resolve_ip=False),
        desired_capabilities={'platform': desired_capabilities['platform'],
                              'browserName': desired_capabilities['browserName'],
                              'unexpectedAlertBehaviour': desired_capabilities['unexpectedAlertBehaviour']}
        )
    return driver


@pytest.fixture(scope='function')
def browser(selenium, cfg):
    selenium.get(cfg['kiali_url'])
    return CustomBrowser(selenium)


@pytest.fixture(scope='function')
def rest_api(cfg):
    return KialiAPI(cfg['kiali_url'])


@pytest.fixture(scope='function')
def kiali_cli(cfg):
    oc_cli = cfg['oc_cli_options']
    return KialiCli(url=oc_cli['oc_url'],
                    username=oc_cli['oc_username'],
                    password=oc_cli['oc_password'])


def pytest_exception_interact(node, call, report):
    if selenium_browser is not None:
        allure.attach(
            'Error screenshot',
            selenium_browser.get_screenshot_as_png(),
            allure.attach_type.PNG)
        allure.attach('Error traceback',
                      str(report.longrepr),
                      allure.attach_type.TEXT)
