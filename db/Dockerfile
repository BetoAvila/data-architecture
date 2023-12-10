FROM mysql:8.1.0
ENV LANG=C.UTF-8
ENV MYSQL_ROOT_PASSWORD=root
WORKDIR /home
RUN cd /home
USER root
COPY ./init.sql /docker-entrypoint-initdb.d/