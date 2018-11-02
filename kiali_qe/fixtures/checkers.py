import pytest

from kiali_qe.utils.log import logger

DEFAULT_BOOKINFO_NAMESPACE = 'bookinfo'


@pytest.fixture
def pick_namespace(openshift_client):

    def _pick_namespace(name):
        """
        Checks if required namespace exists, if not it picks the default namespace to
        run test against and logs warning.

        :param name: name of required namespace
        :returns: name of required namespace if exists, default namespace otherwise
        """
        if openshift_client.namespace_exists(name):
            logger.debug('{} namespace is available'.format(name))
            return name
        else:
            logger.warning('This tests requires {} namespace to be available to run the test safely \
in parallel!!! Using default namespace {}. Ignore if you run tests sequentially.'.format(
                name,
                DEFAULT_BOOKINFO_NAMESPACE)
                )
            return DEFAULT_BOOKINFO_NAMESPACE

    return _pick_namespace
