import imp

from py.path import local  # @UnresolvedImport

_kiali_qe_package_dir = local(imp.find_module('kiali_qe')[1])

#: The project root, ``kiali-qe-pyhton/``
project_path = _kiali_qe_package_dir.dirpath()


#: conf yaml storage, ``kiali-qe-pyhton/conf/``
conf_path = project_path.join('conf')

#: datafile storage, ``kiali-qe-pyhton/data/``
data_path = project_path.join('data')

#: istio objects yaml storage, ``kiali-qe-pyhton/data/resources/istio_objects``
istio_objects_path = data_path.join('resources/istio_objects')

#: log storage, ``kiali-qe-pyhton/log/``
log_path = project_path.join('log')

#: results path for tests, ``kiali-qe-pyhton/results/``
results_path = project_path.join('results')


def get_rel_path(absolute_path_str):
    """Get a relative path for object in the project root
    Args:
        absolute_path_str: An absolute path to a file anywhere under `project_path`
    Note:
        This will be a no-op for files that are not in `project_path`
    """
    target_path = local(absolute_path_str)
    # relto returns empty string when no path parts are relative
    return target_path.relto(project_path) or absolute_path_str
