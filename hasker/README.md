Hasker: analog of stackoverflow on Django 4.1

Requirements

Python 3.9
Django 4.1
PostgreSQL
Python packages:
psycopg2 (on production)
django-rest-swagger
djangorestframework-simplejwt
Pillow

ubuntu /bin/bash

apt-get update
apt-get upgrade
apt-get install git
git clone https://github.com/polovinkin87/hasker.git

docker compose build
docker compose up