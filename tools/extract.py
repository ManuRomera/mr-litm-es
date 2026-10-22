#!/usr/bin/env python3
"""Vuelca los compendios compilados del sistema (LevelDB) y extrae las cadenas traducibles a work/src/<pack>.json"""
import json, re, subprocess, shutil, pathlib, tempfile, sys
R = pathlib.Path(__file__).resolve().parent.parent
SYS = R.parent.parent / 'systems/mist-engine-fvtt'
NODE = r'''
import {ClassicLevel} from '/Applications/Foundry Virtual Tabletop.app/Contents/Resources/app/node_modules/classic-level/index.js';
import fs from 'fs';
const db = new ClassicLevel(process.argv[2], {keyEncoding:'utf8', valueEncoding:'json'}); const o = {};
for await (const [k,v] of db.iterator()) o[k]=v; await db.close(); fs.writeFileSync(process.argv[3], JSON.stringify(o));
'''
SKIP_KEYS = {'img','src','folder','type','color','customFontColor','tabCategory','attribute','visionMode','_id','_stats','_key','ownership','sort','sorting','flags','effects','prototypeToken','width','height','caption','format','level','title','video','image','ownership','permission'}
def volcar(pack):
    tmp = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(SYS/'packs'/pack, tmp/'db')
    (tmp/'d.mjs').write_text(NODE); subprocess.run(['node', str(tmp/'d.mjs'), str(tmp/'db'), str(tmp/'o.json')], check=True)
    return json.load(open(tmp/'o.json'))
def hojas(o, clave=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP_KEYS and not (k == 'title'): continue
            yield from hojas(v, k)
    elif isinstance(o, list):
        for v in o: yield from hojas(v, clave)
    elif isinstance(o, str) and re.search(r'[A-Za-z]{3,}', o) and not re.match(r'^[A-Za-z0-9]{16}$', o) and not re.match(r'^(systems|icons|modules|worlds)/|^#[0-9a-f]{3,8}$', o): yield o
def main():
    (R/'work/src').mkdir(parents=True, exist_ok=True)
    for pack in ['litm-themebooks', 'pregen-characters', 'example-actors', 'system-documentation']:
        db = volcar(pack); out = {}
        json.dump(db, open(R/f'work/src/raw.{pack}.json', 'w'))
        # documentos de primer nivel con sus hijos reunidos
        for k, v in db.items():
            tipo = k.split('!')[1]
            if '.' in tipo: continue
            doc = dict(v); hijos = []
            for k2, v2 in db.items():
                if k2.startswith(f'!{tipo}.') and k2.split('!')[2].split('.')[0] == v['_id']: hijos.append(v2)
            out[v['_id']] = {'tipo': tipo, 'name': v['name'], 'textos': sorted(set(hojas(doc)) | {s for h in hijos for s in hojas(h)}),
                             'hijos': [{'id': h['_id'], 'name': h.get('name'), 'type': h.get('type')} for h in hijos]}
        json.dump(out, open(R/f'work/src/{pack}.json', 'w'), ensure_ascii=False, indent=1)
        print(pack, len(out), sum(len(d['textos']) for d in out.values()), 'cadenas', sum(len(s) for d in out.values() for s in d['textos']), 'caracteres')
main()
