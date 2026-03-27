#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

mkdir -p "${MEDIA_ROOT:-${RENDER_DISK_PATH:-.}/media}"

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py createsuperuser --no-input || true
