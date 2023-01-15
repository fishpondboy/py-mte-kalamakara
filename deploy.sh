#!/bin/bash
source env/bin/activate
git pull
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
killall gunicorn
gunicorn kalamakara.wsgi --daemon