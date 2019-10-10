# FECH Wagtail

## Run project

    python manage.py migrate
    python manage.py runserver

## Run project w/ Docker

    python manage.py migrate
    docker build -t fech-api .
    docker run -d -p 8000:8000 --name fech-container -v /home/ubuntu/fech:/code fech-api
    