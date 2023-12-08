FROM mysql:latest
ENV LANG=C.UTF-8
ENV MYSQL_ROOT_PASSWORD=root
WORKDIR /home
RUN cd /home
COPY ./init.sql /docker-entrypoint-initdb.d/
#https://stackoverflow.com/questions/39052949/docker-copy-file-from-one-container-to-another
EXPOSE 3306
EXPOSE 33060