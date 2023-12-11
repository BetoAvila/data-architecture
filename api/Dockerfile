FROM python:3.11-slim
USER root
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
WORKDIR /home/
RUN cd /home
RUN mkdir /tmp/data && mkdir /tmp/logs
COPY . .
RUN chmod +x start.sh
RUN ./start.sh