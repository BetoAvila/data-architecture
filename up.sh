#!/bin/sh

# Script to iteratively setup Docker environment

# Stops containers from compose command
# Removes and prunes images, volumes and networks unused
# Recomposes without cache
# Clears screen and
# Gets into api container

docker compose down
docker volume rm -f app-vol
docker volume prune -af
docker image rm -f data-architecture-db data-architecture-api data-architecture-client
docker image prune -af
docker network rm -f front-net back-net
docker network prune -f
docker compose build --no-cache
docker compose up -d
clear
docker exec -it data-architecture-api-1 /bin/bash

# docker exec -it data-architecture-client-1 /bin/bash