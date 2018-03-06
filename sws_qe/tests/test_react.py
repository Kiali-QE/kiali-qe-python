from project.sws_view import ServiceListView


def test_service_search(browser):
    view = ServiceListView(browser)
    view.wait_displayed()
    for row in view.services:
        assert row
    search = view.search
    search.simple_search('sws')
    view.wait_displayed()
    search.is_empty
    for row in view.services:
        assert "sws" in row[0].text
