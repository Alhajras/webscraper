# Debian bullseye
FROM python:3.10-bullseye as webcrawler

# Python environmental variable that allows the Python output to be sent straight to the terminal when set to a non-empty string or executed with the -u option on the command line.
# This is useful when log messages are needed in real time
ENV PYTHONUNBUFFERED 1


# Setup Python environment.
WORKDIR /configs
COPY . .
RUN apt-get update
RUN pip install -r requirements.txt

# Django default port
EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]
