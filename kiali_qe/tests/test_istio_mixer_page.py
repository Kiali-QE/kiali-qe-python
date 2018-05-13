from kiali_qe.pages import IstioMixerPage
from kiali_qe.tests import common_tests


def test_pagination_feature(browser):
    # get page instance
    page = IstioMixerPage(browser)
    common_tests.test_pagination_feature(page)
