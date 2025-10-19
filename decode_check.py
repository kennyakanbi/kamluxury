import base64, json, sys, re

b = open('listings_fixture.b64','rb').read()

# try strict decode first
try:
    data = base64.b64decode(b, validate=True)
    method = 'strict'
except Exception as e_strict:
    # sanitize: remove any char not in base64 alphabet
    sanitized = re.sub(rb'[^A-Za-z0-9+/=]', b'', b)
    print('STRICT_FAIL:', e_strict)
    print('Sanitizing input: removed non-base64 characters.')
    print('Original length:', len(b), 'Sanitized length:', len(sanitized))
    # show a short preview (first 200 chars) of sanitized (safe hex)
    print('Sanitized preview (hex, first 200 bytes):', sanitized[:200].hex())
    try:
        data = base64.b64decode(sanitized, validate=True)
        method = 'sanitized-strict'
    except Exception as e_san:
        try:
            # last resort: decode without validation (allows non-base64 whitespace etc.)
            data = base64.b64decode(sanitized, validate=False)
            method = 'sanitized-lenient'
            print('SANITIZED_STRICT_FAIL:', e_san)
        except Exception as e_final:
            print('ALL_DECODE_FAIL:', e_final)
            sys.exit(1)

# now validate JSON
try:
    json.loads(data.decode('utf-8'))
except Exception as e_json:
    print('DECODE_OK_BUT_JSON_INVALID:', e_json)
    # write the decoded bytes anyway so you can inspect
    open('listings_fixture.decoded.b64bin', 'wb').write(data)
    print('Wrote raw decoded bytes to listings_fixture.decoded.b64bin for inspection.')
    sys.exit(2)

# success: write json file
open('listings_fixture.json','wb').write(data)
print('SUCCESS: decoded with method', method, '-> wrote listings_fixture.json')
sys.exit(0)
