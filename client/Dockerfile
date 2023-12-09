FROM python:3.11-slim
ENV LANG=C.UTF-8
WORKDIR /home/
COPY . .
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install \
    nano
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3306
EXPOSE 33060