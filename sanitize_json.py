import sys, json, re
if len(sys.argv) != 3:
    print('Usage: python sanitize_json.py input.json output.json')
    sys.exit(1)
inp, outp = sys.argv[1], sys.argv[2]
raw = open(inp, 'rb').read()
text = raw.decode('utf-8', errors='replace')

def escape_ctrl(ch):
    o = ord(ch)
    # allow tab (9), lf (10), cr (13)
    if o in (9,10,13):
        return ch
    if 0 <= o <= 0x1F:
        return '\\\\u%04x' % o
    return ch

fixed = ''.join(escape_ctrl(ch) for ch in text)

with open(outp, 'w', encoding='utf-8') as f:
    f.write(fixed)

# verify
try:
    json.loads(open(outp, 'r', encoding='utf-8').read())
    print('Wrote cleaned JSON to', outp)
    print('Cleaned file parses as valid JSON.')
except Exception as e:
    print('Wrote cleaned JSON to', outp)
    print('But still invalid:', e)
