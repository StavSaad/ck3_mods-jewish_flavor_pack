# Builds Mesopotamianism's winged-disc icons from its gold-and-lapis Gemini painting on flat green, through
# make_faith_icon.py: the faith's own (as painted, with a reformed version) and colour variants for custom faiths
# (mesopotamian_01..06, listed in the Levantine religion's custom_faith_icons). The metal and the blue inlay are
# recoloured apart (--palette, --inlay).
# Usage: make_mesopotamian_icons.py <winged_disc.png> [<preview.png>]
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
src = sys.argv[1]
preview = sys.argv[2] if len(sys.argv) > 2 else None

GOLD = None                                    # as painted
SILVER = '#1c1c1e,#8a8d93,#eef0f4'
BRONZE = '#2a1708,#8c5a2b,#e8b27a'
LAPIS = None                                   # as painted
CARNELIAN = '#2a0606,#9e2a23,#f2a38c'
TURQUOISE = '#062420,#23907e,#a6eedd'
OBSIDIAN = '#0a0a0c,#2e2f36,#8a8d99'

# icon name: (metal, inlay, also write a reformed version)
ICONS = {
    'mesopotamian': (GOLD, LAPIS, True),
    'mesopotamian_01': (GOLD, CARNELIAN, False),
    'mesopotamian_02': (GOLD, TURQUOISE, False),
    'mesopotamian_03': (SILVER, LAPIS, False),
    'mesopotamian_04': (SILVER, CARNELIAN, False),
    'mesopotamian_05': (BRONZE, TURQUOISE, False),
    'mesopotamian_06': (GOLD, OBSIDIAN, False),
}

for name, (metal, stone, reformed) in ICONS.items():
    cmd = [sys.executable, os.path.join(HERE, 'make_faith_icon.py'), src, name]
    if reformed:
        cmd.append('--reformed')
    if metal:
        cmd += ['--palette', metal]
    if stone:
        cmd += ['--inlay', stone]
    elif metal:
        # A metal change alone must still leave the lapis as painted: recolour the lapis to itself
        cmd += ['--inlay', '#0c1640,#2a44a6,#9fb4f0']
    subprocess.run(cmd, check=True)

if preview:
    names = []
    for name, (_, _, reformed) in ICONS.items():
        names.append(name)
        if reformed:
            names.append(name + '_reformed')
    sheet = Image.new('RGBA', (110 * len(names), 110), (52, 48, 46, 255))
    for i, n in enumerate(names):
        im = Image.open(MOD + f'gfx/interface/icons/faith/{n}.dds').convert('RGBA')
        sheet.alpha_composite(im, (i * 110 + 5, 5))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS).save(preview)
