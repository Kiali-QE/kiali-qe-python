

class EntityBase(object):

    def is_in(self, items):
        for item in items:
            if self.is_equal(item):
                return True
        return False

    def is_equal(self, item):
        raise NotImplemented('Should be implemented on sub class')
