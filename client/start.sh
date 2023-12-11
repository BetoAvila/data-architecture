#!/bin/sh
apt-get update && \
    apt-get upgrade -y && \
    apt-get install \
    nano
pip install --upgrade pip
pip install -r requirements.txt
apt-get install -y curl
