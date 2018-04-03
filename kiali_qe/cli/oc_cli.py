import subprocess
import json
import pytest


class OCCliClient(object):

    def __init__(self, url, username, password):
        """Simple CLI client for Openshift

        Args:
            url: String with the URL of the Openshift (e.g. 'https://hostname:8443')
            username: OC username
            password: OC password
        """
        self.url = url
        self.username = username
        self.password = password

    def login(self):
        try:
            subprocess.check_call("oc login {} --username={} --password={}".format(self.url, self.username, self.password), shell=True)
        except Exception:
            pytest.xfail('oc login failed')

    def get_json(self, command):
        return json.loads(subprocess.check_output("{} -o json".format(command), shell=True))