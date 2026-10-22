#!/usr/bin/env python3
"""Une work/trad/*.py con work/src/*.json y escribe compendium/mist-engine-fvtt.<pack>.json para Babele."""
import json, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R/'work/trad'))
import example, themebooks, doc_status, doc_documentation, doc_howtoplay, pregen_finn, pregen_seede, pregen_rosa
SRC = lambda p: json.load(open(R/f'work/src/{p}.json'))

def d_de(doc, *glob):
    """diccionario inglés→español de un documento; falla si falta alguna cadena"""
    out = {}
    for t in doc['textos']:
        es = next((g[t] for g in glob if t in g), None)
        if es is None: raise SystemExit(f'sin traducir en {doc["name"]}: {t[:70]!r}')
        out[t] = es
    return out

def por_indice(doc, T):
    return {doc['textos'][i]: es for i, es in T.items()}

def escribir(pack, label, mapping, entries, folders=None):
    j = {'label': label, 'mapping': mapping, 'entries': entries}
    if folders: j['folders'] = folders
    json.dump(j, open(R/f'compendium/mist-engine-fvtt.{pack}.json', 'w'), ensure_ascii=False, indent=1)
    print(pack, len(entries))

LITM = lambda p: {'path': p, 'converter': 'litm'}

# libros de tema
d = SRC('litm-themebooks'); N = themebooks.N
ent, fol = {}, {}
for i, doc in d.items():
    if doc['tipo'] == 'folders': fol[doc['name']] = N[doc['name']]; continue
    D = d_de(doc, N)
    ent[i] = {'name': N[doc['name']], 'system': D}
escribir('litm-themebooks', 'Libros de tema LiTM', {'system': LITM('system'), 'description': 'system.description'}, ent, fol)

# actores
for pack, label, mods in (('pregen-characters', 'Personajes pregenerados', (('TBY0ztdIZgWGTbZE', pregen_finn), ('nYX2RhQqHlYx0G4A', pregen_seede), ('wgniQ6W1R9qTxop5', pregen_rosa))),
                          ('example-actors', 'Actores de ejemplo', (('CWxjPHe0ln8V5JcF', example),))):
    d = SRC(pack); glob = {}
    for i, m in mods: glob.update(por_indice(d[i], m.T))
    ent = {}
    for i, doc in d.items():
        D = d_de(doc, glob)
        ent[i] = {'name': D[doc['name']], 'tokenName': D[doc['name']], 'system': D, 'items': D}
    escribir(pack, label, {'system': LITM('system'), 'items': LITM('items'), 'tokenName': {'path': 'prototypeToken.name', 'converter': 'name'}}, ent)

# diarios
d = SRC('system-documentation'); ent = {}
for i, m in (('TSjCkXJj1PSzrvTc', doc_status), ('TrgMWh3RyxxBkZoB', doc_documentation), ('ua8ifZXpIZ8AdaZT', doc_howtoplay)):
    G = por_indice(d[i], m.T); D = d_de(d[i], G)
    ent[i] = {'name': D[d[i]['name']], 'pages': D}
escribir('system-documentation', 'Documentación del sistema', {'pages': LITM('pages')}, ent)
