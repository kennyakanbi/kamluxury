#!/usr/bin/env bash
set -euo pipefail

echo "Which python: $(which python || true)"
python --version || true
echo "Which gunicorn: $(which gunicorn || true)"

# Install dependencies (Render usually does this automatically, but safe to run)
pip install -r requirements.txt

# Migrate, collectstatic, create admin (ensure_admin_user should be safe to run)
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Only try to ensure admin if env vars are present
if [ -n "${ADMIN_USER-:-}" ] && [ -n "${ADMIN_PASS-:-}" ]; then
  python manage.py ensure_admin_user || true
fi

# Exec gunicorn so it takes PID 1
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --log-file -
