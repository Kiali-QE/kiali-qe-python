import requests
import os
import urllib3


urllib3.disable_warnings()


class RestAPIClient(object):

    def __init__(self, url, entry='api', verify=False):
        """Simple REST API client for container management systems

        Args:
            url: String with the URL of the Kiali server (e.g. 'http://jdoe:password@hostname')
            entry: Entry point of the REST API
            verify: 'True' if we want to verify SSL, 'False' otherwise
        """
        self.api_entry = "{}/{}".format(url, entry)
        self.verify = verify

    def get(self, entity_type, name=None, namespace=None, convert=None):
        """Sends a request to fetch an entity of specific type

        Fetches a single entity if its name is provided or all of given type if name is ommited.

        Note:
            Some entities are tied to namespaces (projects).
            To fetch these by name, namespace has to be provided as well.

            convert: The convert method to use for the json content (e.g. eval_strings).

        Return:
            Tuple containing status code and json response with requested entity/entities.
        """
        path = '{}s'.format(entity_type)
        if name is not None:
            if namespace is not None:
                path = os.path.join('namespaces/{}'.format(namespace), path)
            path = os.path.join(path, '{}'.format(name))
        r = self.raw_get(path)
        json_content = r.json() if r.ok else None
        if json_content and convert:
            json_content = convert(json_content)
        return (r.status_code, json_content)

    def get_json(self, path, headers=None, params=None):
        r = self.raw_get(path, headers, params)
        return (r.json() if r.ok else None)

    def raw_get(self, path, headers=None, params=None):
        return requests.get(
            os.path.join(self.api_entry, path),
            verify=self.verify,
            headers=headers,
            params=params)
