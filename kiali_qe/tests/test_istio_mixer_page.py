from kiali_qe.pages import IstioMixerPage
from kiali_qe.tests.common import pagination_feature_test


def test_pagination_feature(browser):
    # get page instance
    page = IstioMixerPage(browser)
    pagination_feature_test(page)
