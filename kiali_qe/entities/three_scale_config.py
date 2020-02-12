from kiali_qe.entities import EntityBase


class ThreeScaleHandler(EntityBase):

    def __init__(self, name, service_id, system_url, access_token=None):
        self.name = name
        self.service_id = service_id
        self.system_url = system_url
        self.access_token = access_token

    def __str__(self):
        return 'name:{}, service_id:{}, system_url:{}, access_token:{}'.format(
            self.name, self.service_id, self.system_url, self.access_token)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            type(self).__name__, repr(self.name), repr(self.service_id),
            repr(self.system_url), repr(self.access_token))

    def __eq__(self, other):
        return self.is_equal(other, advanced_check=True)

    def __hash__(self):
        return (hash(self.name) ^ hash(self.service_id) ^ hash(self.system_url))

    def is_equal(self, other, advanced_check=False):
        # basic check
        if not isinstance(other, ThreeScaleHandler):
            return False
        if self.name != other.name:
            return False
        if self.service_id != other.service_id:
            return False
        if self.system_url != other.system_url:
            return False
        # advanced check
        if advanced_check:
            if self.access_token != other.access_token:
                return False
        return True
