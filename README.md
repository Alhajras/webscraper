# webscraper
## Building and running django in docker
From the root project run the following command
`docker build -t crawler-django backend/webscraper/`.

Run `docker image ls` to check if the build exist.

To run the container run: `docker run -p 8000:8000 crawler-django`.
