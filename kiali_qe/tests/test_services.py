from project.kiali_view import ServiceListView


def test_service_list(browser, rest_api):
    view = ServiceListView(browser)
    ui_services = get_services_set(view.get_all())
    rest_services = get_services_set(rest_api.list_services())
    assert ui_services == rest_services, \
        ("Lists of services mismatch! UI:{}, REST:{}"
         .format(ui_services, rest_services))


def test_service_search(browser, rest_api):
    view = ServiceListView(browser)
    search = 'istio'
    view.simple_search(search)
    ui_services = get_services_set(view.get_all())
    for service in ui_services:
        assert search in service[0]
        assert search in service[1]


def get_services_set(services):
    """
    
    Return the set of services which contains only necessary fields,
    such as 'name' 'namespace', 'replicas', 'available_replicas'
    """
    return set((service.name, service.namespace,
                str(service.replicas), str(service.available_replicas)) for service in services)
