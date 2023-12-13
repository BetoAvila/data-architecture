#!/bin/sh
apt-get update && \
    apt-get upgrade -y && \
    apt-get install \
    nano
mkdir /home/data
pip install --upgrade pip
pip install -r requirements.txt
apt-get install -y curl
