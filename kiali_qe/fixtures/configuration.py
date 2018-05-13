from os import environ

import pytest

from kiali_qe.utils import get_dict
from kiali_qe.utils.path import conf_path


@pytest.fixture(scope='session')
def cfg():
    cfg = get_dict(conf_path.strpath, 'env.yaml')
    # overide with environment variables
    _override_list = {
        'kiali.hostname': 'KIALI_HOSTNAME',
        'kiali.username': 'KIALI_USERNAME',
        'kiali.password': 'KIALI_PASSWORD',
        'selenium.web_driver': 'SELENIUM_WEB_DRIVER',
        'selenium.capabilities.platform': 'SELENIUM_PLATFORM',
        'selenium.capabilities.browser': 'SELENIUM_BROWESR',
        'selenium.capabilities.zalenium.recordVideo': 'ZAL_RECORD_VIDEO',
        'selenium.capabilities.zalenium.idleTimeout': 'ZAL_IDLE_TIMEOUT'
    }
    for y_key, e_key in _override_list.items():
        if environ.get(e_key) is not None:
            cfg.set(y_key, environ.get(e_key))
    return cfg
