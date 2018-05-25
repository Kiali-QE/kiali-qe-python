from kiali_qe.tests import ServicesPageTest


def test_pagination_feature(rest_client, browser):
    tests = ServicesPageTest(rest_client=rest_client, browser=browser)
    tests.assert_pagination_feature()


def test_namespaces(rest_client, browser):
    tests = ServicesPageTest(rest_client=rest_client, browser=browser)
    tests.assert_namespaces()


def test_filter_options(rest_client, browser):
    tests = ServicesPageTest(rest_client=rest_client, browser=browser)
    tests.assert_filter_options()


def test_filter_feature(rest_client, browser):
    tests = ServicesPageTest(rest_client=rest_client, browser=browser)
    tests.assert_filter_feature()
