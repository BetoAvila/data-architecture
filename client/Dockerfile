FROM apache/spark:3.3.3-python3
ENV LANG=C.UTF-8
WORKDIR /home/
RUN cd /home
COPY . .
USER root
RUN mv mysql-connector-j-8.1.0.jar /opt/spark/jars
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install \
    nano
RUN pip install --upgrade pip
RUN pip install -r requirements.txt