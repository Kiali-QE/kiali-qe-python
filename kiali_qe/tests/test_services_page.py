from kiali_qe.pages import ServicesPage
from kiali_qe.tests.common import pagination_feature_test


def test_pagination_feature(browser):
    # load page instance
    page = ServicesPage(browser)
    pagination_feature_test(page)
