import pytest
from kiali_qe.components import Notification
from kiali_qe.pages import RootPage
from kiali_qe.utils.log import logger


@pytest.mark.p_atomic
@pytest.mark.p_group8
def test_login(browser):
    # load root page
    page = RootPage(browser, auto_login=False)
    # do login
    _login = page.login()
    logger.debug('Login status:{}'.format(_login))
    assert _login
    # assert notifications
    logger.debug('Notifications on screen:{}'.format(page.notifications.items))
    assert not page.notifications.contains(_type=Notification.TYPE_DANGER)
    assert not page.notifications.contains(_type=Notification.TYPE_WARNING)


@pytest.mark.p_atomic
@pytest.mark.p_group8
def test_invalid_login(browser):
    # load root page
    page = RootPage(browser, auto_login=False)
    # do login with invalid credentials
    _login = page.login(username='iam-invalid', password='secret')
    logger.debug('Login status:{}'.format(_login))
    logger.debug('Notifications on screen:{}'.format(page.notifications.items))
    assert not _login
    assert page.notifications.contains(
        _type='danger', text='Unauthorized. Error in username or password')
