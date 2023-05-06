# Webscraper
## Using `docker compose` (Recommended)
The docker compose version supported is: `v2.16.0`
run `docker compose version` to print your local version. 

If you do not have docker compose you can install it from here [Docker compose](https://docs.docker.com/compose/install/)
- Building all images:
    ```
    docker compose build
    ```

- Run containers:
    ```
    docker compose up -d
    ```
- If you want to only run the pbs cluster run:
    ```
    docker compose up -d pbs-head-node pbs-sim-node
    ```
- To register the simulation node in the head node, first you have to invlike the head container and run the following: 
    ```
    . /etc/profile.d/pbs.sh
    qmgr -c "create node pbs-sim-node"
    ```
## Create a network for both angular and django to communicate
`docker network create webcrawler-network --subnet=173.16.38.0/18`

## Building and running django in docker
- From the root project run the following command
    ```
    docker build -t crawler-django backend/webscraper/
    ```

- Run `docker image ls` to check if the build exist.

- To run the container run:
    ```
    docker run -p 8000:8000 crawler-django
    ```

## Building and running angular in docker
- From the root project run the following command
    ```
    docker build -t crawler-angular frontend/app/
    ```

- Run `docker image ls` to check if the build exist.

- To run the container run:
    ```
    docker run -p 4200:4200 crawler-angular
    ```
