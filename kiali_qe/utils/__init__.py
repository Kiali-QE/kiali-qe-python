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
    return MyDotMap(get_yaml(path, yaml_file))


def get_yaml(path, yaml_file):
    with open(os.path.join(path, yaml_file), 'r') as yaml_data:
        return yaml.safe_load(yaml_data)


def is_equal(object_a, object_b):
    if isinstance(object_a, list):
        if len(object_a) == len(object_b):
            for item_a in object_a:
                if isinstance(item_a, str) or isinstance(item_a, float)\
                 or isinstance(item_a, int) or isinstance(item_a, unicode):
                    if item_a not in object_b:
                        return False
                elif isinstance(item_a, dict):
                    _is_in = False
                    for item_b in object_b:
                        if cmp(item_a, item_b) == 0:
                            _is_in = True
                            break
                    if not _is_in:
                        return False

                else:
                    if not item_a.is_in(object_b):
                        return False
            return True
        else:
            return False
    elif isinstance(object_a, dict):
        return cmp(object_a, object_b) == 0
