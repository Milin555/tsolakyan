#!/usr/bin/env python3
"""
Generate stand-in product imagery for the template.

    python build-placeholders.py

These are designed tiles, not broken boxes — soft duotone panels in the
brand's own palette so an unfinished demo still reads as intentional.
Replace them with the client's photographs before pitching: drop files
into assets/img/ named p01.jpg … p12.jpg and re-run nothing.

Requires Pillow:  pip install pillow
"""
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    raise SystemExit('Pillow is not installed.  Run:  pip install pillow')

import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
OUT  = ROOT / 'assets' / 'img'
W, H = 900, 1350                       # 2:3, matches the card aspect

# soft pairs that sit comfortably beside kidswear / ethnic photography
PAIRS = [
    ((0xF6, 0xDF, 0xE2), (0xE8, 0xB4, 0xBE)),   # blush
    ((0xE3, 0xEF, 0xE6), (0xB2, 0xD3, 0xC0)),   # mint
    ((0xFA, 0xF0, 0xD6), (0xF1, 0xD08, 0x8A)[0:3] if False else (0xEF, 0xD3, 0x8C)),  # butter
    ((0xE0, 0xEA, 0xF4), (0xAF, 0xC6, 0xDE)),   # powder blue
    ((0xEC, 0xE5, 0xF2), (0xC7, 0xB4, 0xD8)),   # lilac
    ((0xFB, 0xE6, 0xDA), (0xF0, 0xBC, 0x9C)),   # peach
    ((0xE8, 0xEC, 0xE2), (0xBD, 0xC9, 0xB0)),   # sage
    ((0xFA, 0xE2, 0xDD), (0xEE, 0xA9, 0x9B)),   # coral
]


def font(size, bold=False):
    for name in (('arialbd.ttf', 'arial.ttf') if bold else ('arial.ttf',)):
        p = pathlib.Path('C:/Windows/Fonts') / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def gradient(top, bottom):
    """Vertical two-stop gradient, then a soft radial highlight."""
    base = Image.new('RGB', (1, H))
    px = base.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    img = base.resize((W, H), Image.BILINEAR)

    glow = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(glow)
    d.ellipse([-W * .25, -H * .18, W * 1.25, H * .62], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img.paste(Image.new('RGB', (W, H), (255, 255, 255)), (0, 0), glow)
    return img


def tile(index, label, monogram):
    top, bottom = PAIRS[index % len(PAIRS)]
    img = gradient(top, bottom)
    d = ImageDraw.Draw(img)

    ink = (0x3A, 0x33, 0x2E)
    ring_r = 108
    cx, cy = W // 2, int(H * 0.44)
    d.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
              outline=ink + (0,), width=2)

    f_mono = font(78, bold=True)
    w = d.textlength(monogram, font=f_mono)
    d.text((cx - w / 2, cy - 52), monogram, font=f_mono, fill=ink)

    f_lab = font(26)
    w = d.textlength(label.upper(), font=f_lab)
    d.text((cx - w / 2, cy + ring_r + 42), label.upper(), font=f_lab, fill=ink)

    f_note = font(20)
    note = 'REPLACE WITH PRODUCT PHOTO'
    w = d.textlength(note, font=f_note)
    d.text((cx - w / 2, H - 78), note, font=f_note, fill=(0x8A, 0x81, 0x79))
    return img


PRODUCTS = [
    ('p01', 'Lehenga Choli',  'VK'), ('p02', 'Kurta Set',      'VK'),
    ('p03', 'Sharara Set',    'VK'), ('p04', 'Anarkali',       'VK'),
    ('p05', 'Dhoti Kurta',    'VK'), ('p06', 'Frock',          'VK'),
    ('p07', 'Nehru Jacket',   'VK'), ('p08', 'Gharara',        'VK'),
    ('p09', 'Co-ord Set',     'VK'), ('p10', 'Pathani Suit',   'VK'),
    ('p11', 'Party Gown',     'VK'), ('p12', 'Festive Set',    'VK'),
]

CATEGORIES = [('c01', 'Girls'), ('c02', 'Boys'), ('c03', 'Festive'), ('c04', 'New In')]


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)

    for i, (name, label, mono) in enumerate(PRODUCTS):
        img = tile(i, label, mono)
        img.resize((600, 900), Image.LANCZOS).save(OUT / f'{name}-600.webp', 'WEBP', quality=84, method=6)
        img.resize((1000, 1500), Image.LANCZOS).save(OUT / f'{name}-1000.webp', 'WEBP', quality=84, method=6)
        img.resize((800, 1200), Image.LANCZOS).save(OUT / f'{name}-800.jpg', 'JPEG', quality=82, optimize=True)

    for i, (name, label) in enumerate(CATEGORIES):
        img = tile(i + 3, label, 'VK').resize((800, 1000), Image.LANCZOS)
        img.save(OUT / f'{name}.webp', 'WEBP', quality=84, method=6)

    # wide hero slides
    for i, label in enumerate(('Festive Edit', 'Girls Collection', 'Boys Collection')):
        h = tile(i, label, 'VK').resize((1600, 2400), Image.LANCZOS)
        h.crop((0, 700, 1600, 1700)).save(OUT / f'hero{i+1}.webp', 'WEBP', quality=84, method=6)

    total = sum(f.stat().st_size for f in OUT.glob('*'))
    print(f'  {len(list(OUT.glob("*")))} files, {total/1048576:.2f} MB')
    print('  Replace with real photographs before pitching — see README.')
