#!/bin/sh

echo "Apply database migrations"
# Применить миграции
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata users/fixtures/auth.json

exec "$@"