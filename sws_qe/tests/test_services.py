from project.sws_view import ServiceListView


def test_service_search(browser, rest_api):
    view = ServiceListView(browser)
    assert get_services_set(rest_api.list_services())
    #for row in view.get_all():
    #    assert row
    #view.simple_search('sws')
    #for row in view.get_all():
    #    assert "sws" in row[0].text


def get_services_set(services):
    """
    Return the set of services which contains only necessary fields,
    such as 'name' and 'namespace'
    """
    return set((service.name, service.namespace) for service in services)
