FROM python:3.11-slim
USER root
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
# ENV PYSPARK_SUBMIT_ARGS='--packages org.apache.spark:spark-avro_2.13:3.3.3  pyspark-shell'
WORKDIR /home/
RUN cd /home
RUN mkdir /tmp/data && mkdir /tmp/logs
COPY . .
COPY ./data/*.csv /tmp/data/
# RUN mv mysql-connector-j-8.1.0.jar /opt/spark/jars
# RUN apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install \
#     nano
RUN chmod +x start.sh
RUN ./start.sh
