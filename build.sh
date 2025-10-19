#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files for WhiteNoise
python manage.py collectstatic --noinput
