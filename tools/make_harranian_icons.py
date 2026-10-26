# Builds the Harranian rite's crescent-standard icons from its silver-and-gold Gemini painting on flat green, through
# make_faith_icon.py: the rite's own (as painted) and colour variants for custom faiths (harranian_01..06, listed in
# the Levantine religion's custom_faith_icons). The silver and the gold accents (disc, tassel caps) are recoloured
# apart (--palette, --inlay with --accent warm).
# Usage: make_harranian_icons.py <crescent_standard.png> [<preview.png>]
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
src = sys.argv[1]
preview = sys.argv[2] if len(sys.argv) > 2 else None

SILVER = '#1c1c22,#8a909c,#eef1f6'
GOLD = '#2e1d06,#a8822f,#fbe7a1'
BRONZE = '#2a1708,#8c5a2b,#e8b27a'
COPPER = '#2d0f08,#a3452a,#f6b08c'
IRON = '#121212,#4d4f54,#b9bcc2'
LAPIS = '#0a1430,#2f4f9e,#a9c1f2'

# icon name: (crescent and pole, accents) - None for the rite's own icon, as painted
ICONS = {
    'harranian': None,
    'harranian_01': (GOLD, SILVER),
    'harranian_02': (GOLD, GOLD),
    'harranian_03': (BRONZE, GOLD),
    'harranian_04': (IRON, GOLD),
    'harranian_05': (SILVER, COPPER),
    'harranian_06': (LAPIS, GOLD),
}

for name, colours in ICONS.items():
    cmd = [sys.executable, os.path.join(HERE, 'make_faith_icon.py'), src, name]
    if colours:
        cmd += ['--palette', colours[0], '--inlay', colours[1], '--accent', 'warm']
    subprocess.run(cmd, check=True)

if preview:
    sheet = Image.new('RGBA', (110 * len(ICONS), 110), (52, 48, 46, 255))
    for i, n in enumerate(ICONS):
        im = Image.open(MOD + f'gfx/interface/icons/faith/{n}.dds').convert('RGBA')
        sheet.alpha_composite(im, (i * 110 + 5, 5))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS).save(preview)
