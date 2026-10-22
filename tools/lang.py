#!/usr/bin/env python3
"""Genera lang/es.json: parte del es.json del sistema (mist-engine-fvtt) y aplica correcciones + glosario."""
import json, re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
SYS = R.parent.parent / 'systems/mist-engine-fvtt/lang'

def flat(d, p=''):
    o = {}
    for k, v in d.items():
        if isinstance(v, dict): o.update(flat(v, p + k + '.'))
        else: o[p + k] = v
    return o

def nest(f):
    out = {}
    for k, v in f.items():
        c = out; ps = k.split('.')
        for x in ps[:-1]: c = c.setdefault(x, {})
        c[ps[-1]] = v
    return out

en = flat(json.load(open(SYS / 'en.json')))
es = flat(json.load(open(SYS / 'es.json')))
P = 'MIST_ENGINE.'
FIX = json.load(open(R / 'tools/correcciones.json'))
for k, v in FIX.items():
    assert k in es, k
    es[k] = v

# glosario global sobre todo el texto
SUBS = [
    (r'\bDJ\b', 'Narrador'), (r'\bGM\b', 'Narrador'), (r'Camaradería', 'Compañía'), (r'¿Estás seguro que', '¿Seguro que'),
    (r'How To Play', 'Cómo jugar'), (r'Gestión de Tours', 'Gestión de tours'),
]
for k in es:
    for a, b in SUBS: es[k] = re.sub(a, b, es[k])
faltan = [k for k in en if k not in es]
assert not faltan
json.dump(nest(es), open(R / 'lang/es.json', 'w'), ensure_ascii=False, indent=2)
print(len(es), 'claves')
