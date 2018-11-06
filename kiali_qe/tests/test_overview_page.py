import pytest

from kiali_qe.tests import OverviewPageTest


@pytest.mark.p_atomic
@pytest.mark.p_group6
def test_filter_options(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_filter_options()


# putting to p_ro_top group although right now there are no tests changing health of app so
# it could be in p_ro_top_safe
@pytest.mark.p_ro_top
@pytest.mark.p_group6
def test_all_overviews(kiali_client, openshift_client, browser):
    tests = OverviewPageTest(
        kiali_client=kiali_client, openshift_client=openshift_client, browser=browser)
    tests.assert_all_items(filters=[])
