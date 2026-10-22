#!/usr/bin/env python3
"""Superpone título y marca MR- sobre art_src/banner_raw.png -> docs/img/banner.webp"""
from PIL import Image, ImageDraw, ImageFont
import pathlib
R = pathlib.Path(__file__).resolve().parent.parent
im = Image.open(R/'art_src/banner_raw.png').convert('RGB'); W, H = im.size
sombra = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sombra)
for x in range(int(W*.66)): d.line([(x, 0), (x, H)], fill=int(205*(1-x/(W*.66))**1.3))
im.paste((14, 18, 16), mask=sombra)
d = ImageDraw.Draw(im)
f = lambda n, s, i=0: ImageFont.truetype(n, s, index=i)
tit = f('/System/Library/Fonts/Supplemental/Baskerville.ttc', int(H*.13), 1)
sub = f('/System/Library/Fonts/Supplemental/Baskerville.ttc', int(H*.075), 2)
peq = f('/System/Library/Fonts/Supplemental/Baskerville.ttc', int(H*.040), 0)
x, y = int(W*.05), int(H*.27)
d.text((x, y-int(H*.10)), 'TRADUCCIÓN NO OFICIAL · FOUNDRY VTT v13 · v14', font=peq, fill=(214, 178, 110))
d.text((x, y), 'Legend in', font=tit, fill=(244, 240, 228))
d.text((x, y+int(H*.15)), 'the Mist', font=tit, fill=(244, 240, 228))
d.text((x+4, y+int(H*.33)), 'en español', font=sub, fill=(150, 200, 150))
d.text((x+4, y+int(H*.47)), 'Interfaz · hojas · diálogos · chat · Cómo jugar', font=peq, fill=(205, 208, 196))
mono = Image.open(R/'../mr-nadir/brand/MR_11_Formal_Marfil_Transparente.png').convert('RGBA')
mono.thumbnail((int(W*.12), int(H*.12))); im.paste(mono, (x, H-mono.height-int(H*.05)), mono)
(R/'docs/img').mkdir(parents=True, exist_ok=True)
im.save(R/'docs/img/banner.webp', quality=88)
im.resize((1280, 640)).save(R/'docs/img/social.png')
