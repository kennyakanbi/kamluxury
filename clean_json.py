import re, json, sys, html

IN = 'listings_fixture.json'
OUT = 'listings_fixture.cleaned.json'
RAW_OUT = 'listings_fixture.cleaned.raw.txt'

# read input with replacement so we don't crash on encoding oddities
with open(IN, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

orig_len = len(text)

# 1) Remove C0 control characters except TAB(0x09), LF(0x0A), CR(0x0D)
# pattern removes: \x00-\x08 \x0B \x0C \x0E-\x1F \x7F
ctrl_pattern = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
clean1 = ctrl_pattern.sub('', text)
removed_count = orig_len - len(clean1)

# 2) Basic fixes for "???" artifacts (common when smart quotes/em-dash lost)
#   - Replace sequences of 4+ '?' with em-dash
#   - Replace sequences of 2-3 '?' with right single quote (possessive / contractions) or a single apostrophe
# This is heuristic — adjust if it mangles text you care about.
clean2 = re.sub(r'\?{4,}', '—', clean1)
clean2 = re.sub(r'\?{2,3}', '’', clean2)

# 3) Unescape stray HTML entities if any (e.g. &amp; etc.)
clean3 = html.unescape(clean2)

# Save a raw cleaned text for inspection
with open(RAW_OUT, 'w', encoding='utf-8') as f:
    f.write(clean3)

# 4) Validate JSON by parsing; if successful, pretty-dump
try:
    parsed = json.loads(clean3)
except Exception as e:
    # show context around first error position if possible
    msg = str(e)
    print('JSON_PARSE_ERROR:', msg)
    # attempt to get position out of message (Python error messages often include 'char N')
    m = re.search(r'char (\d+)', msg)
    if m:
        pos = int(m.group(1))
        start = max(0, pos-120)
        end = min(len(clean3), pos+120)
        context = clean3[start:end]
        print('Context (around position {}):'.format(pos))
        # print python-style repr for control characters visibility
        print(repr(context))
    else:
        print('Could not extract error position from parser message.')
    sys.exit(2)

# pretty dump to OUT
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print('CLEAN_SUCCESS: removed_ctrl_count=%d -> wrote %s (pretty) and %s (raw cleaned text)' % (removed_count, OUT, RAW_OUT))
sys.exit(0)
