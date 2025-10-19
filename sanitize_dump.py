import os, json, io, sys, re

# make sure this matches your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

buf = io.StringIO()
call_command('dumpdata', 'listings', '--indent', '2', stdout=buf)

s = buf.getvalue()

# Remove any ASCII control characters except for \n, \r, \t
# (JSON must not contain other control characters)
s_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)

# parse and re-dump ensuring unicode preserved
data = json.loads(s_clean)
with open('listings_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('WROTE: listings_fixture.json (UTF-8, sanitized)')
