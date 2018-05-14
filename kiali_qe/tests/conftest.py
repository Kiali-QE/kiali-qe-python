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
from rest_api.openshift_api import OpenshiftAPI

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
    command_executor = RemoteConnection(webdriver_options['command_executor'], resolve_ip=False)
    # increase the timeout because we are waiting for new pod to be created which takes some time
    command_executor.set_timeout(120)
    driver = webdriver.Remote(
        command_executor,
        desired_capabilities={'platform': desired_capabilities['platform'],
                              'browserName': desired_capabilities['browserName'],
                              'unexpectedAlertBehaviour': desired_capabilities['unexpectedAlertBehaviour']}
    )
    # reset the timeout to default, only driver creation is taking so much time
    command_executor.reset_timeout()
    return driver


@pytest.fixture(scope='function')
def browser(selenium, cfg):
    selenium.get('http://{}:{}@{}'.format(cfg['kiali_username'], cfg['kiali_password'], cfg['kiali_hostname']))
    return CustomBrowser(selenium)


@pytest.fixture(scope='function')
def rest_api(cfg):
    return KialiAPI(host=cfg['kiali_hostname'],
                    username=cfg['kiali_username'],
                    password=cfg['kiali_password'])


@pytest.fixture(scope='function')
def openshift_api(cfg):
    return OpenshiftAPI()


def pytest_exception_interact(node, call, report):
    if selenium_browser is not None:
        allure.attach(
            'Error screenshot',
            selenium_browser.get_screenshot_as_png(),
            allure.attach_type.PNG)
        allure.attach('Error traceback',
                      str(report.longrepr),
                      allure.attach_type.TEXT)
