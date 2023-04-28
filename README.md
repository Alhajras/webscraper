# webscraper
## Create a network for both angular and django to communicate
`docker network create webcrawler-network`

## Building and running django in docker
- From the root project run the following command
`docker build -t crawler-django backend/webscraper/`.

- Run `docker image ls` to check if the build exist.

- To run the container run: `docker run -p 8000:8000 crawler-django`.

## Building and running angular in docker
- From the root project run the following command
`docker build -t crawler-angular frontend/app/`.

- Run `docker image ls` to check if the build exist.

- To run the container run: `docker run -p 4200:4200 crawler-angular`.

