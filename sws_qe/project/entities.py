
class Service(object):
    """
    Service class provides information details on Service list and details page.

    Args:
        name: name of the service
        namespace: namespace where service is located
    """

    def __init__(self, name, namespace):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        if namespace is None:
            raise KeyError("'namespace' should not be 'None'")
        self.name = name
        self.namespace = namespace


class Rule(object):
    """
    Rule class provides information details on Rule list and details page.

    Args:
        name: name of the rule
        namespace: namespace where rule is located
    """

    def __init__(self, name, namespace, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        if namespace is None:
            raise KeyError("'namespace' should not be 'None'")
        self.name = name
        self.namespace = namespace
        self.match = kwargs['match'] if 'match' in kwargs else None
        self.handler = kwargs['handler'] if 'handler' in kwargs else None
        self.instances = kwargs['instances'] if 'instances' in kwargs else None
