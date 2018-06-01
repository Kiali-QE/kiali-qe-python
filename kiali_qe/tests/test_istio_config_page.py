from kiali_qe.tests import IstioConfigPageTest


def test_pagination_feature(kiali_client, openshift_client, browser, cfg):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser, cfg=cfg)
    tests.assert_pagination_feature()


def test_namespaces(kiali_client, openshift_client, browser, cfg):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser, cfg=cfg)
    tests.assert_namespaces()


def test_filter_options(kiali_client, openshift_client, browser, cfg):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser, cfg=cfg)
    tests.assert_filter_options()


def test_filter_feature(kiali_client, openshift_client, browser, cfg):
    tests = IstioConfigPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser, cfg=cfg)
    tests.assert_filter_feature()
