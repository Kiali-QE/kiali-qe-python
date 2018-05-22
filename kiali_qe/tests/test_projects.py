from project.kiali_view import ServiceListView


def test_project_list(browser, rest_api, openshift_api):
    os_rest_projects = get_projects_set(openshift_api.list_projects())
    view = ServiceListView(browser)
    kiali_rest_projects = get_projects_from_services(rest_api.list_services())
    ui_projects = get_projects_from_services(view.get_all())
    assert len(os_rest_projects) != 0, ("REST projects should not be empty")
    assert len(kiali_rest_projects) != 0, ("Kiali REST projects should not be empty")
    assert len(ui_projects) != 0, ("UI projects should not be empty")
    assert kiali_rest_projects == ui_projects, \
        ("Lists of projects mismatch! UI:{}, Kiali REST:{}"
         .format(ui_projects, kiali_rest_projects))
    assert kiali_rest_projects.issubset(os_rest_projects), ("OS REST Projects should contain KIALI REST Projects")


def get_projects_set(projects):
    """
    Return the set of projects which contains only necessary fields,
    such as 'name'
    """
    return set((project.name) for project in projects)


def get_projects_from_services(services):
    """
    Return the set of namespaces from the list of provided services.
    """
    return set((service.namespace) for service in services)
