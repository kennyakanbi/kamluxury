#!/usr/bin/env bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Ensure admin user (reads ADMIN_USER, ADMIN_EMAIL, ADMIN_PASS from env)
python manage.py ensure_admin_user || true

# Merge/update listings from fixture (safe: updates existing by slug, creates if missing)
python manage.py import_listings_from_fixture --file listings_fixture.from_local.json || true

# Collect static assets
python manage.py collectstatic --noinput
