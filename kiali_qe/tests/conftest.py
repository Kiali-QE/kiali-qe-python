import urllib3

# disable InsecureRequestWarning,
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


def pytest_configure(config):
    # disable pytest warnings plugin in order to keep our own warning logging
    # we might want to remove this one
    config.pluginmanager.set_blocked('warnings')
    # also disable the pytest logging system since its triggering issues with our own
    config.pluginmanager.set_blocked('logging-plugin')


pytest_plugins = (
    'kiali_qe.fixtures.browser',
    'kiali_qe.fixtures.configuration',
    'kiali_qe.fixtures.log',
    'kiali_qe.fixtures.rest_client',
    'kiali_qe.fixtures.zalenium',
)
