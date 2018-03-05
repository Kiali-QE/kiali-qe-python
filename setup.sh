#!/bin/bash

HOME=`pwd`

# Install virtualenv, libcurl-devel, gcc, wget, unzip, openssl-devel
yum install python-virtualenv wget unzip libcurl-devel unzip gcc openssl-devel redhat-rpm-config -y


# Setup virtual environment
virtualenv .cf-ui
source .cf-ui/bin/activate

# Install base requirements
pip install -r requirements.txt
pip install -U pip

## Begin - Install mgmtsystem

# Needed for RHEL7
cat /etc/os-release | grep -q "Red Hat Enterprise Linux"
if [ $? -eq "0" ]
then
    echo -e "\nInstalling RHEL dependencies..."
    pip install setuptools --upgrade
fi

pip uninstall --yes pycurl
export PYCURL_SSL_LIBRARY=nss
pip install pycurl

## Requirement for Fedora 27 (https://github.com/siznax/wptools/issues/68)
if grep -q -i "fedora 27" /etc/os-release
then 
pip install --no-cache-dir --compile --ignore-installed --install-option="--with-openssl" pycurl
fi

pip install mgmtsystem==1.6.1

## End - Install mgmtsystem

# Install Chromdriver - PATH must include "."
rm -f chromedriver
wget https://chromedriver.storage.googleapis.com/2.28/chromedriver_linux64.zip
unzip chromedriver_linux64.zip

# Unpack 'oc'
./install_oc.sh

# setup test recorder
pip install http://pypi.python.org/packages/source/v/vnc2flv/vnc2flv-20100207.tar.gz
mkdir -p records

# setup flv2gif converter
pip install moviepy

echo -e "\nSetup Complete."
