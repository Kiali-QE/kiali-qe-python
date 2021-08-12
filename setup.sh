#!/bin/bash

HOME=`pwd`

pip3.6 install virtualenv

virtualenv install

# Setup virtual environment
virtualenv .kiali-qe
source .kiali-qe/bin/activate

# Install base requirements
pip3.6 install -r requirements.txt

# Needed for RHEL7
cat /etc/os-release | grep -q "Red Hat Enterprise Linux"
if [ $? -eq "0" ]
then
    echo -e "\nInstalling RHEL dependencies..."
    pip3 install setuptools --upgrade
fi
