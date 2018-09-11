from kiali_qe.entities import EntityBase


class Application(EntityBase):

    def __init__(self, name, namespace, istio_sidecar=None):
        self.name = name
        self.namespace = namespace
        self.istio_sidecar = istio_sidecar

    def __str__(self):
        return 'name:{}, namespace:{}, sidecar:{}'.format(
            self.name, self.namespace, self.istio_sidecar)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.namespace), repr(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, Application):
            return False
        if self.name != other.name:
            return False
        if self.namespace != other.namespace:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
        return True


class ApplicationDetails(EntityBase):

    def __init__(self, name,
                 istio_sidecar=False, **kwargs):
        if name is None:
            raise KeyError("'name' should not be 'None'")
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.workloads = kwargs['workloads']\
            if 'workloads' in kwargs else None

    def __str__(self):
        return 'name:{}, sidecar:{}'.format(
            self.name, self.istio_sidecar)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, repr(self.name), repr(self.istio_sidecar))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, ApplicationDetails):
            return False
        if self.name != other.name:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
        return True


class AppWorkload(EntityBase):

    def __init__(self, name, services, istio_sidecar=False):
        self.name = name
        self.istio_sidecar = istio_sidecar
        self.services = services

    def __str__(self):
        return 'name:{}, istio_sidecar:{}, services:{}'.format(
            self.name, self.istio_sidecar, self.services)

    def __repr__(self):
        return "{}({}, {}, {})".format(
            type(self).__name__, repr(self.name),
            repr(self.istio_sidecar), repr(self.services))

    def __eq__(self, other):
        return self.is_equal(other)

    def is_equal(self, other, advanced_check=True):
        # basic check
        if not isinstance(other, AppWorkload):
            return False
        if self.name != other.name:
            return False
        if self.services != other.services:
            return False
        # advanced check
        if advanced_check:
            if self.istio_sidecar != other.istio_sidecar:
                return False
        return True
