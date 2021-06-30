# Kiali GUI Automation
Kiali GUI QE automation framework. This framework based on pytest Testing Framework, using Widgetastic testing tools.

### Project structure

* `kiali_qe/`: Root directory for all the source code.
    * `components`: This directory contains custom browser, UI components(widgets)
    *  `entities`: This directory contains entities/modes to create comparable data across UI and REST.
    *  `fixtures`: Type of fixtures available here
    *  `pages`: UI pages as python `class`
    *  `rest`: REST clients
    *  `tests`: tests
    *  `utils`: supporting utilities

### Configurations
All the configurations will be available in one location. That is `env.yaml`. This file is located at `conf/env.yaml`

### To run tests

Run in virtual environment only created and activated by running:
```sh
# clone this repository
$ git clone https://github.com/Kiali-QE/kiali-qe-python.git kiali-qe-python
$ cd kiali-qe-python/

# create virtual environment
$ virtualenv .env
# enable virtual environment
$ source .env/bin/activate

# install requirements
$ pip install -r requirements.txt

# update conf/env.yaml (kiali hostname, token and selenium driver url) 

# Tests use OpenShift API.
# Needs to be logged in once in to OpenShift before to run tests.
# When we login in to OpenShift, ".kube/config" file will be created with auth token.
# This token will be used in tests to access OpenShift
# oc - OpenShift Command Line Interface (CLI) can be downloaded from OpenShift Help -> Command line tools
$ oc login https://<openshift>:8443 --username=<username> --password=<password> --insecure-skip-tls-verify=true

# The token necessary in env.yaml can be read after login
$ oc whoami -t

# run all tests
$ pytest -s
# see the log on log/kiali_qe.log
```

### Log file
All the logs will be created under `log/`

