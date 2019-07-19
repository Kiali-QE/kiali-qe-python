from os import environ

from kiali_qe.utils import get_dict
from kiali_qe.utils.path import conf_path

# overide with environment variables
_env_override_list = {
        'kiali.hostname': 'KIALI_HOSTNAME',
        'kiali.username': 'KIALI_USERNAME',
        'kiali.password': 'KIALI_PASSWORD',
        'kiali.auth_type': 'KIALI_AUTH_TYPE',
        'kiali.token': 'KIALI_TOKEN',
        'selenium.web_driver': 'SELENIUM_WEB_DRIVER',
        'selenium.capabilities.platform': 'SELENIUM_PLATFORM',
        'selenium.capabilities.browser': 'SELENIUM_BROWESR',
        'selenium.capabilities.zalenium.recordVideo': 'ZAL_RECORD_VIDEO',
        'selenium.capabilities.zalenium.idleTimeout': 'ZAL_IDLE_TIMEOUT'
    }


def setup_conf(filename, override_list):
    cfg = get_dict(conf_path.strpath, filename)
    for y_key, e_key in override_list.items():
        if environ.get(e_key) is not None:
            cfg.set(y_key, environ.get(e_key))
    return cfg


env = setup_conf('env.yaml', _env_override_list)
