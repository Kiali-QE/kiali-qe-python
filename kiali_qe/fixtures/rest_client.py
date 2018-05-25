import json

import pytest

from kiali_qe.rest.kiali_api import KialiExtendedClient
from kiali_qe.rest.openshift_api import OpenshiftAPI
from kiali_qe.utils.log import logger


@pytest.fixture(scope='session')
def kiali_client(cfg):
    logger.debug('Creating kiali rest client')
    _client = KialiExtendedClient(
        host=cfg.kiali.hostname, username=cfg.kiali.username, password=cfg.kiali.password)
    # update kiali version details
    _response = _client.status()
    _status = _response['status']
    cfg.kiali.version.core = _status['Kiali core version']
    cfg.kiali.version.console = _status['Kiali console version']

    # There is an issue to show video recordings when we use special chars in build details
    # https://github.com/zalando/zalenium/issues/572
    # cfg.selenium.capabilities.zalenium.build = 'console:{}, core:{}:{}'.format(
    #    cfg.kiali.version.console,
    #    cfg.kiali.version.core,
    #    _status['Kiali core commit hash'])
    cfg.selenium.capabilities.zalenium.build = '{}'.format(cfg.kiali.version.core)
    logger.info('Kiali versions:\n{}'.format(json.dumps(_response, indent=2)))
    return _client


@pytest.fixture(scope='session')
def openshift_client(cfg):
    logger.debug('Creating openshift rest client')
    return OpenshiftAPI()
