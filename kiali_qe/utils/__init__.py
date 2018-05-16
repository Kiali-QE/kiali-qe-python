import yaml
from dotmap import DotMap
import operator
import os


class MyDotMap(DotMap):

    def __init__(self, *args, **kwargs):
        DotMap.__init__(self, *args, **kwargs)

    def set(self, key, value):
        keys = key.split('.')
        reduce(operator.getitem, keys[:-1], self)[keys[-1]] = value

    def to_dict(self):
        return self.toDict()


def get_dict(path, yaml_file):
    with open(os.path.join(path, yaml_file), 'r') as yaml_data:
        yaml_dict = yaml.safe_load(yaml_data)
    return MyDotMap(yaml_dict)


def is_equal(list_a, list_b):
    if len(list_a) == len(list_b):
        for item in list_a:
            if isinstance(item, str) or isinstance(item, float)\
             or isinstance(item, int) or isinstance(item, unicode):
                if item not in list_a:
                    return False
            else:
                if not item.is_in(list_b):
                    return False
        return True
