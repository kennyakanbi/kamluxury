#!/usr/bin/env bash
set -o errexit  # exit on error

pip install -r requirements.txt

# Run migrations and load your data automatically
python manage.py migrate --noinput

# Load your listings data (optional, remove if not needed every deploy)
python manage.py loaddata listings_fixture.cleaned.json || true

python manage.py collectstatic --noinput
