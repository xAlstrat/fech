# FECH Wagtail

## Run project

    python manage.py migrate
    python manage.py runserver

## Run project w/ Docker

    docker build -t fech-api .
    docker run -d -p 8000:8000 --name fech-container -v /home/ubuntu/fech:/code fech-api
    docker exec -ti fech-container python manage.py migrate
    