import sys, json
if len(sys.argv) != 2:
    print('Usage: python inspect_json_error.py <file.json>')
    sys.exit(1)
fname = sys.argv[1]
raw = open(fname, "rb").read()
try:
    json.loads(raw.decode("utf-8"))
    print("JSON is valid")
    sys.exit(0)
except json.JSONDecodeError as e:
    pos = e.pos
    print("JSONDecodeError:", e.msg)
    print("Error position (char index):", pos)
    start = max(0, pos - 200)
    end = min(len(raw), pos + 200)
    snippet = raw[start:end].decode("utf-8", errors="replace")
    rel = pos - start
    print("\n--- context (240 bytes around error) ---\n")
    print(snippet)
    print("\n" + " " * rel + "^ <-- problem here (relative index {})".format(rel))
    offending = raw[pos:pos+4]  # show up to 4 bytes
    print("\nOffending bytes (hex):", offending.hex(), "len:", len(offending))
    print("Byte ords:", [b for b in offending])
