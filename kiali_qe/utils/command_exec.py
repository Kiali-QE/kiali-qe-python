import os


def oc_apply(yaml_file, namespace):
    add_command_text = "oc apply " + (
        " -n " + namespace if namespace else ""
        ) + " -f " + yaml_file
    add_command_result = os.popen(add_command_text).read()
    return add_command_result.__contains__("created")\
        or add_command_result.__contains__("configured")


def oc_delete(yaml_file, namespace):
    delete_command_text = "oc delete " + (
        " -n " + namespace if namespace else ""
        ) + " -f " + yaml_file
    delete_command_result = os.popen(delete_command_text).read()
    return delete_command_result.__contains__("deleted")


def oc_idle(service_name, namespace):
    idle_command_text = "oc idle {} -n {}".format(service_name, namespace)
    os.popen(idle_command_text).read()
