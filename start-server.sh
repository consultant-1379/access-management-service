#!/bin/bash
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    ( cd ams; python manage.py makemigrations; python manage.py migrate; python manage.py create_groups; python manage.py createsuperuser --no-input)
fi
( cd ams; gunicorn ams.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
