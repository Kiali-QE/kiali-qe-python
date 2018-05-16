from kiali_qe.entities import EntityBase
from kiali_qe.utils import is_equal


class Action(EntityBase):

    def __init__(self, handler, instances):
        self.handler = handler
        self.instances = instances

    def __str__(self):
        return 'handler:{}, actions:{}'.format(self.handler, self.action)

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.handler), repr(self.instances))

    def is_equal(self, item):
        return self.handler == item.handler and is_equal(self.instances, item.instances)

    @classmethod
    def get_from_rest(cls, action):
        _handler = action['handler']
        _instances = action['instances']
        return Action(handler=_handler, instances=_instances)


class Rule(EntityBase):

    def __init__(self, name, namespace, actions, match=None):
        self.name = name
        self.namespace = namespace
        self.actions = actions
        self.match = match

    def __str__(self):
        return 'name:{}, namespace:{}, match:{}, actions:{}'.format(
            self.name, self.namespace, self.match, self.actions)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__,
            repr(self.name), repr(self.namespace), repr(self.actions), repr(self.match))

    def is_equal(self, item):
        if self.name != item.name:
            return False
        if self.namespace != item.namespace:
            return False
        if not is_equal(self.actions, item.actions):
            return False
        return True
