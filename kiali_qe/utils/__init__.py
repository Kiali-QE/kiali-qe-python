import yaml
from dotmap import DotMap
import operator
import os
from functools import reduce
from kiali_qe.components.enums import IstioConfigValidation


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
    with open(get_yaml_path(path, yaml_file), 'r') as yaml_data:
        return yaml.safe_load(yaml_data)


def get_yaml_path(path, yaml_file):
    return os.path.join(path, yaml_file)


def is_equal(object_a, object_b):
    if isinstance(object_a, list):
        if len(object_a) == len(object_b):
            for item_a in object_a:
                if isinstance(item_a, str) or isinstance(item_a, float)\
                 or isinstance(item_a, int) or isinstance(item_a, bytes):
                    if item_a not in object_b:
                        return False
                elif isinstance(item_a, dict):
                    _is_in = False
                    for item_b in object_b:
                        if _cmp_dict(item_a, item_b):
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
        return _cmp_dict(object_a, object_b)


def _cmp_dict(a, b):
    return a == b


def is_sublist(list_a, list_b):
    return set(list_a).issubset(set(list_b))


def get_validation(_valid, _not_valid, _warning):
    if _valid:
        return IstioConfigValidation.VALID
    elif _not_valid:
        return IstioConfigValidation.NOT_VALID
    elif _warning:
        return IstioConfigValidation.WARNING
    else:
        return IstioConfigValidation.NA


def to_linear_string(source):
    return str(source).\
            replace('\n', ' ').\
            replace('{', '').\
            replace('}', '').\
            replace('"', '').\
            replace(',', '').\
            replace('[', '').\
            replace(']', '').\
            replace('{', '').\
            replace('}', '').\
            replace(':', '').\
            replace('\'', '').lower()


def get_texts_of_elements(elements):
    texts = []
    for _element in elements:
        texts.append(_element.text.strip())
    return texts


def word_in_text(word, text, contains=True):
    if contains:
        return word in text
    else:
        return word not in text


def get_url(products, key):
    for item in products:
        if item['name'] == key and 'url' in item:
            return item['url']
