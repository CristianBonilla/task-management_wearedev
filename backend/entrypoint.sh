#!/bin/sh
set -e

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Starting Gunicorn on 0.0.0.0:8000"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
