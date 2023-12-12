#!/bin/sh
apt-get update && \
    apt-get upgrade -y && \
    apt-get install \
    nano
mv data/*.csv /tmp/data/
pip install --upgrade pip
pip install -r requirements.txt
pip install "uvicorn[standard]"
# uvicorn main:app --host 0.0.0.0