from datetime import datetime
from time import sleep

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection

from kiali_qe.components.browser import KialiBrowser
from kiali_qe.fixtures.zalenium import set_browser, update_suite_status
from kiali_qe.utils.log import logger


@pytest.fixture(scope='session')
def browser(cfg, rest_client):
    selenium = _get_selenium(cfg)
    selenium.maximize_window()
    selenium.get(
        'http://{}:{}@{}'.format(cfg.kiali.username, cfg.kiali.password, cfg.kiali.hostname))
    # load KialiBrowser
    kiali_browser = KialiBrowser(
        selenium, logger=logger,
        kiali_versions={'core': cfg.kiali.version.core, 'console': cfg.kiali.version.console})
    # ugly hack to pass browser object to zalenium fixtures
    # needs to remove this global assignment
    set_browser(kiali_browser)
    yield kiali_browser
    # update suite status on zalenium
    update_suite_status()
    kiali_browser.selenium.quit()


def _get_selenium(cfg):
    # load desired_capabilities
    capabilities = {}
    for key, value in cfg.selenium.capabilities.items():
        if key == 'zalenium':   # update zalenium capabilities
            for z_key, z_value in value.items():
                capabilities['zal:' + z_key] = z_value
        else:   # update selenium capabilities
            capabilities[key] = value
    # load driver
    driver = None
    # try to get the driver more times (workaround for zalenium issue in OS)
    maximum_try = 5
    for x in range(1, maximum_try):
        try:
            logger.info('Trying to create web driver. Attempt: {} of {}'.format(x, maximum_try))
            driver = _get_driver(cfg, capabilities)
            break
        except WebDriverException as ex:
            logger.warn('Failed to create driver. Exception:{}'.format(ex))
            sleep(5)
            continue
    return driver


def _get_driver(cfg, capabilities):
    logger.debug('Creating web driver')
    start_time = datetime.now()
    # set resolve_ip to false to make it work in cases when remote driver is running in OpenShift
    command_executor = RemoteConnection(cfg.selenium.web_driver, resolve_ip=False)
    # increase the timeout because we are waiting for new pod to be created which takes some time
    command_executor.set_timeout(120)
    driver = webdriver.Remote(command_executor, desired_capabilities=capabilities)
    # reset the timeout to default, only driver creation is taking so much time
    command_executor.reset_timeout()
    _delta = datetime.now() - start_time
    logger.debug('Web driver created successfully. Time taken: {}ms'.format(
        int(_delta.total_seconds() * 1000)))
    return driver
