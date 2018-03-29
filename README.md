# kiali-qe-python
Based on pytest Testing Framework, using Widgetastic testing tools.

# project structure

* kiali_qe/project           - the package where Kiali UI Views and Entities are located. All new pages in Kiali should have Views and Pages added here.
* kiali_qe/rest_api          - the package where Kiali REST API Client is located. In tests the API calls are used to verify data consistency between UI and REST API.
* kiali_qe/tests             - the package where tests are added.
* kiali_qe/widgetastic_kiali - the package where Widgetastic framework is adjusted for Kiali UI which is written in React.


# run tests

Run in virtual environment only created and activated by running:
```
source setup.sh
source .kiali-qe/bin/activate
```

Configure the environment to run.
in conf/env.yaml file make sure you have set correct values as defined in conf/env.yaml.template


For running execute following command in activated python virtual environment.
```
py.test
```



