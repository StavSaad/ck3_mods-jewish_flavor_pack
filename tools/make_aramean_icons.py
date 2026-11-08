# Builds Arameanism's recoloured icons (0.15 plan, section 14) from the mod's existing faith and rite icons, through
# make_faith_icon.py --palette: each source icon is laid on flat green at 4x, then recoloured by its brightness.
#  aramean_01..06   the custom faiths' colours, from Hadad's lightning forks (jip_rite_hadad)
#  jip_rite_baalshamin  Bel's eagle (jip_rite_bel) in silver and lapis, the Lord of Heaven
#  jip_rite_elagabal    Shamash's sun disc (jip_rite_shamash) as black stone and gold, the sun god of Emesa
#  jip_rite_allat       Anat's lion-headed axe and spear (jip_rite_anat) in silver, Allat the warrior
# Usage: make_aramean_icons.py [--preview <png>]
import os
import subprocess
import sys
import tempfile

from PIL import Image

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
ICONS = MOD + 'gfx/interface/icons/faith/'

# icon name: (source icon, palette shadow,mid,highlight)
RECOLOURS = {
    'aramean_01': ('jip_rite_hadad', '#2a1708,#8c5a2b,#e8b27a'),  # bronze
    'aramean_02': ('jip_rite_hadad', '#2d0f08,#a3452a,#f6b08c'),  # copper
    'aramean_03': ('jip_rite_hadad', '#1e0a1e,#6e2a6a,#d9a3d2'),  # purple
    'aramean_04': ('jip_rite_hadad', '#0a1430,#2f4f9e,#a9c1f2'),  # lapis blue
    'aramean_05': ('jip_rite_hadad', '#082420,#2f8a78,#a8eadb'),  # turquoise
    'aramean_06': ('jip_rite_hadad', '#2a1f05,#9c7a22,#f4dc8a'),  # gold
    'jip_rite_baalshamin': ('jip_rite_bel', '#0b1633,#4f6fae,#e3ebf8'),
    'jip_rite_elagabal': ('jip_rite_shamash', '#080706,#3a3128,#e0b452'),
    'jip_rite_allat': ('jip_rite_anat', '#15171b,#6f7680,#e9edf2'),
}


def on_green(src, path):
    im = Image.open(ICONS + src + '.dds').convert('RGBA')
    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    bg = Image.new('RGBA', (im.width + 80, im.height + 80), (0, 255, 0, 255))
    bg.alpha_composite(im, (40, 40))
    bg.convert('RGB').save(path)


tmp = tempfile.mkdtemp()
for name, (src, palette) in RECOLOURS.items():
    png = os.path.join(tmp, src + '.png')
    if not os.path.exists(png):
        on_green(src, png)
    subprocess.run([sys.executable, MOD + 'tools/make_faith_icon.py', png, name, '--palette', palette], check=True)

if '--preview' in sys.argv:
    names = list(RECOLOURS)
    sheet = Image.new('RGBA', (110 * len(names), 110), (60, 60, 60, 255))
    for i, n in enumerate(names):
        sheet.alpha_composite(Image.open(ICONS + n + '.dds').convert('RGBA').resize((100, 100)), (i * 110 + 5, 5))
    sheet.save(sys.argv[sys.argv.index('--preview') + 1])
