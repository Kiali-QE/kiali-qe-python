from kiali_qe.entities import EntityBase
from kiali_qe.utils import is_equal


class IstioConfig(EntityBase):

    def __init__(self, name, namespace, object_type, validation=None):
        self.name = name
        self.namespace = namespace
        self.object_type = object_type
        self.validation = validation

    def __str__(self):
        return 'name:{}, namespace:{}, object_type:{}, validation:{}'.format(
            self.name, self.namespace, self.object_type, self.validation)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace),
            repr(self.object_type), repr(self.validation))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def __hash__(self):
        return (hash(self.name) ^ hash(self.namespace) ^ hash(self.object_type))

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, IstioConfig):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        # advanced check
        if advanced_check:
            if self.object_type != other.object_type:
                return False
            if self.validation != other.validation:
                return False
        return True


class IstioConfigDetails(EntityBase):

    def __init__(self, name, _type, text, validation=None, error_messages=[]):
        self.name = name
        self._type = _type
        self.text = text
        self.validation = validation
        self.error_messages = error_messages

    def __str__(self):
        return 'name{}, text:{}, {}'.format(
            self.name, self.text, self.validation)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, repr(self.name), repr(self.text), repr(self.validation))

    def __eq__(self, other):
        return self.is_equal(other)

    def __hash__(self):
        return (hash(self.name) ^ hash(self._type))

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, IstioConfigDetails):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if advanced_check:
            if self.validation != other.validation:
                return False
        return True


class Action(EntityBase):

    def __init__(self, handler, instances):
        self.handler = handler
        self.instances = instances

    def __str__(self):
        return 'handler:{}, actions:{}'.format(self.handler, self.action)

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.handler), repr(self.instances))

    def is_equal(self, other):
        return isinstance(other, Action)\
         and self.handler == other.handler\
         and is_equal(self.instances, other.instances)

    @classmethod
    def get_from_rest(cls, action):
        _handler = action['handler']
        _instances = action['instances']
        return Action(handler=_handler, instances=_instances)


class Rule(EntityBase):

    def __init__(self, name, namespace, object_type):
        self.name = name
        self.namespace = namespace
        self.object_type = object_type

    def __str__(self):
        return 'name:{}, namespace:{}, object_type:{}'.format(
            self.name, self.namespace, self.object_type)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace), repr(self.object_type))

    def __hash__(self):
        return (hash(self.name) ^ hash(self.namespace))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Rule):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        if self.object_type != other.object_type:
            return False
        if not advanced_check:
            return True
        return True
