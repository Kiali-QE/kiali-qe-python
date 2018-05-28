from kiali_qe.tests import ServicesPageTest


def test_pagination_feature(kiali_client, browser):
    tests = ServicesPageTest(kiali_client=kiali_client, browser=browser)
    tests.assert_pagination_feature()


def test_namespaces(kiali_client, browser):
    tests = ServicesPageTest(kiali_client=kiali_client, browser=browser)
    tests.assert_namespaces()


def test_filter_options(kiali_client, browser):
    tests = ServicesPageTest(kiali_client=kiali_client, browser=browser)
    tests.assert_filter_options()


def test_filter_feature(kiali_client, browser):
    tests = ServicesPageTest(kiali_client=kiali_client, browser=browser)
    tests.assert_filter_feature()
