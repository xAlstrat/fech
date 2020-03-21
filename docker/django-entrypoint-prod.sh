#!/usr/bin/env bash

until python manage.py migrate
do
    echo "Waiting for postgres ready..."
    sleep 2
done

gunicorn fech.wsgi:application --bind 0.0.0.0:8000 --workers 3