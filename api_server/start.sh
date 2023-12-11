#!/bin/sh
apt-get update && \
    apt-get upgrade -y && \
    apt-get install \
    nano
# apt-get update
# apt-get install default-jre -y
# export JAVA_HOME=/usr/bin/
mv data/*.csv /tmp/data/
pip install --upgrade pip
pip install -r requirements.txt
pip install "uvicorn[standard]"