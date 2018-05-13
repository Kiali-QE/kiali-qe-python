from kiali_qe.pages import ServicesPage
from kiali_qe.tests import common_tests


def test_pagination_feature(browser):
    # load page instance
    page = ServicesPage(browser)
    common_tests.test_pagination_feature(page)
