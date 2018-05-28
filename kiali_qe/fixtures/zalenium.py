import pytest

from kiali_qe.utils.log import logger

ZALENIUM_MESSAGE = 'zaleniumMessage'
ZALENIUM_TEST_STATUS = 'zaleniumTestPassed'


report = {
        'passed': [],
        'skipped': [],
        'failed': [],
        'duration': 0.0,
        'total_passed': 0,
        'total_skipped': 0,
        'total_failed': 0,
        'total': 0,
        }

_browser = None


def set_browser(browser):
    global _browser
    _browser = browser


def update_suite_status():
    if report['total_failed'] > 0 or report['total_passed'] == 0:
        _update_zalenium_cookie('suite_failed')
    else:
        _update_zalenium_cookie('suite_passed')


def _get_test_name(location):
    path, lineno, domaininfo = location
    return '{}.{}::{}'.format(path, lineno, domaininfo)


def _update_cookie(name, value):
    if _browser is None:
        logger.warn('There is no browser object!')
        return
    _browser.selenium.add_cookie({'name': name, 'value': value})


def _update_zalenium_cookie(test_status, test_name=None):
    if test_status == 'start':
        _update_cookie(ZALENIUM_MESSAGE, '[T] Start: {}'.format(test_name))
    elif test_status == 'passed':
        _update_cookie(ZALENIUM_MESSAGE, '[T] Passed: {}'.format(test_name))
    elif test_status == 'failed':
        _update_cookie(ZALENIUM_MESSAGE, '[T] Failed: {}'.format(test_name))
    elif test_status == 'skiped':
        _update_cookie(ZALENIUM_MESSAGE, '[T] Skipped: {}'.format(test_name))
    elif test_status == 'suite_passed':
        _update_cookie(ZALENIUM_TEST_STATUS, 'true')
    elif test_status == 'suite_failed':
        _update_cookie(ZALENIUM_TEST_STATUS, 'false')


@pytest.mark.hookwrapper
def pytest_runtest_setup(item):
    test_name = _get_test_name(item.location)
    # add status on cookie to publish it on zalenium video
    _update_zalenium_cookie('start', test_name)
    yield


def pytest_runtest_makereport(item, call, __multicall__):
    rep = __multicall__.execute()
    report['duration'] += rep.duration

    test_status = None
    if rep.when == "call":
        if rep.passed:
            report['passed'].append(rep.nodeid)
            report['total_passed'] += 1
            test_status = 'passed'
        if rep.failed:
            report['failed'].append(rep.nodeid)
            report['total_failed'] += 1
            test_status = 'failed'
    else:
        if rep.skipped:
            report['skipped'].append(rep.nodeid)
            report['total_skipped'] += 1
            test_status = 'skiped'

    if test_status is not None:
        report['total'] += 1
        test_name = _get_test_name(item.location)
        _update_zalenium_cookie(test_status, test_name)

    return rep


# def pytest_sessionfinish(session, exitstatus):
#    if report['passed']:
#        update_zalenium_cookie('suite_passed')
#    elif report['failed']:
#        update_zalenium_cookie('suite_failed')
