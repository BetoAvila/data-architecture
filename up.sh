#!/bin/sh
docker compose down
docker volume rm -f app-vol
docker image rm -f data-architecture-db data-architecture-api data-architecture-client
docker network rm -f front-net back-net
docker image prune -af
docker compose build --no-cache
docker compose up -d
clear
docker exec -it data-architecture-api-1 /bin/bash

# docker exec -it data-architecture-client-1 /bin/bash