# Builds every sign-of-Tanit icon of the Levantine religion (canaanite_religion) from one silver Gemini painting on
# flat green, through make_faith_icon.py: the silver as painted (for custom faiths), the gold of Tanitism (and of
# Canaanism until Baal's emblem comes), and colour variants for
# custom faiths (canaanite_01..06, listed in the religion's custom_faith_icons).
# Usage: make_tanit_icons.py <silver_tanit.png> [<preview.png>]
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
src = sys.argv[1]
preview = sys.argv[2] if len(sys.argv) > 2 else None

# icon name: (palette shadow,mid,highlight or None for the painting's own silver, also write a reformed version)
ICONS = {
    'punic': (None, True),                                # silver, for custom faiths
    'canaanite': ('#2e1d06,#a8822f,#fbe7a1', True),       # Tanitism and, for now, Canaanism: gold
    'canaanite_01': ('#2a1708,#8c5a2b,#e8b27a', False),   # bronze
    'canaanite_02': ('#2d0f08,#a3452a,#f6b08c', False),   # copper
    'canaanite_03': ('#1e0a1e,#6e2a6a,#d9a3d2', False),   # Tyrian purple
    'canaanite_04': ('#0a1430,#2f4f9e,#a9c1f2', False),   # lapis blue
    'canaanite_05': ('#082420,#2f8a78,#a8eadb', False),   # turquoise
    'canaanite_06': ('#121212,#4d4f54,#b9bcc2', False),   # iron
}

for name, (palette, reformed) in ICONS.items():
    cmd = [sys.executable, os.path.join(HERE, 'make_faith_icon.py'), src, name]
    if reformed:
        cmd.append('--reformed')
    if palette:
        cmd += ['--palette', palette]
    subprocess.run(cmd, check=True)

if preview:
    names = []
    for name, (_, reformed) in ICONS.items():
        names.append(name)
        if reformed:
            names.append(name + '_reformed')
    sheet = Image.new('RGBA', (110 * len(names), 110), (52, 48, 46, 255))
    for i, n in enumerate(names):
        im = Image.open(MOD + f'gfx/interface/icons/faith/{n}.dds').convert('RGBA')
        sheet.alpha_composite(im, (i * 110 + 5, 5))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS).save(preview)
