from project.sws_view import ServiceListView


def test_service_search(browser):
    view = ServiceListView(browser)
    for row in view.services:
        assert row
    view.simple_search('sws')
    for row in view.services:
        assert "sws" in row[0].text
