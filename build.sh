#!/usr/bin/env bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run migrations
/opt/render/project/src/.venv/bin/python manage.py migrate --noinput || true

# Load the fixture (ignore errors so deploy continues if items already exist)
# The '|| true' is valid in bash (Render runs builds in bash).
/opt/render/project/src/.venv/bin/python manage.py loaddata listings_fixture.from_local.json || true

# Collect static
/opt/render/project/src/.venv/bin/python manage.py collectstatic --noinput
