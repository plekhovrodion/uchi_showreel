import json,sys
exp=json.load(open('hashes.json'))
bad=0
for k,v in sorted(exp.items()):
    try: s=open(f'svg/{k}.svg',encoding='utf-8').read()
    except FileNotFoundError: continue
    h=0x811c9dc5
    for ch in s: h=((h^ord(ch))*0x01000193)&0xffffffff
    ok=format(h,'x')==v; bad+=not ok
    print(k,'OK' if ok else 'MISMATCH')
sys.exit(bad)
