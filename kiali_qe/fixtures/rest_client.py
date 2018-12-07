import json
import pytest

from kiali_qe.rest.kiali_api import KialiExtendedClient
from kiali_qe.rest.openshift_api import OpenshiftExtendedClient
from kiali_qe.utils.conf import env as cfg
from kiali_qe.utils.log import logger


@pytest.fixture(scope='session')
def kiali_client():
    logger.debug('Creating kiali rest client')
    logger.debug('Kiali hostname: {}'.format(cfg.kiali.hostname))
    _client = KialiExtendedClient(hostname=cfg.kiali.hostname,
                                  username=cfg.kiali.username,
                                  password=cfg.kiali.password)
    # update kiali version details
    _response = _client.get_response('getStatus')
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
def openshift_client():
    logger.debug('Creating opeshift rest client')
    _client = OpenshiftExtendedClient()
    logger.info('Openshift versions:\n{}'.format(json.dumps(_client.version, indent=2)))
    return _client
