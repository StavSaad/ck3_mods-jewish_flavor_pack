# Builds one recoloured copy (<icon>_custom) of each Levantine god's rite icon and of the main rites' icons that have no
# colour set of their own, through make_faith_icon.py --palette. The originals stay with their own rites (the god-named
# rites of 00_jip_rite_icons.txt, Baalism, Yahwism, Ashurism); the copies are for everything else: new rites that take
# no god's name (the faiths' fallback packs in 00_jip_rite_icons.txt) and the custom faith icon list (jip_canaanite.txt).
# A warm (gold, bronze, stone) icon becomes silver, a cool (silver, blue) one gold.
# Usage: make_custom_rite_icons.py [--preview <png>]
import colorsys
import os
import subprocess
import sys
import tempfile

from PIL import Image

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
ICONS = MOD + 'gfx/interface/icons/faith/'

# icon: faith (the fallback pack it joins)
SOURCES = {
    # Mesopotamianism
    'mesopotamian': 'mesopotamian', 'jip_rite_marduk': 'mesopotamian', 'jip_rite_shamash': 'mesopotamian',
    'jip_rite_ishtar': 'mesopotamian', 'jip_rite_nanna': 'mesopotamian', 'jip_rite_nabu': 'mesopotamian', 'jip_rite_nergal': 'mesopotamian',
    'jip_rite_tammuz': 'mesopotamian', 'jip_rite_nusku': 'mesopotamian', 'jip_rite_enlil': 'mesopotamian',
    # Arameanism
    'jip_rite_dushara': 'aramean', 'jip_rite_bel': 'aramean', 'jip_rite_allat': 'aramean', 'jip_rite_rimmon': 'aramean',
    'jip_rite_atargatis': 'aramean', 'jip_rite_elagabal': 'aramean', 'jip_rite_gad': 'aramean',
    'jip_rite_rakibel': 'aramean', 'jip_rite_shamin': 'aramean', 'jip_rite_sahar': 'aramean',
    # Canaanism
    'jip_baal': 'canaanite', 'jip_yahwism': 'canaanite', 'jip_rite_chemosh': 'canaanite', 'jip_rite_milcom': 'canaanite',
    'jip_rite_qos': 'canaanite', 'jip_rite_eshmun': 'canaanite', 'jip_rite_adonis': 'canaanite',
    'jip_rite_dagon': 'canaanite', 'jip_rite_hammon': 'canaanite', 'jip_rite_melqart': 'canaanite',
    'jip_rite_anat': 'canaanite', 'jip_rite_astarte': 'canaanite', 'jip_rite_kothar': 'canaanite',
    'jip_rite_asherah': 'canaanite', 'jip_rite_yarikh': 'canaanite',
}

SILVER = '#16181c,#7c838d,#eef1f5'
GOLD = '#2a1f05,#9c7a22,#f4dc8a'
# Where the warmth test picks badly: Dushara's red stone would turn olive in gold
PALETTE = {'jip_rite_dushara': SILVER}


def is_warm(im):
    """The icon's opaque pixels are mostly saturated orange-to-yellow (gold, bronze, sandstone)."""
    px = [p for p in im.resize((50, 50)).getdata() if p[3] > 128]
    warm = 0
    for r, g, b, _ in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s > 0.2 and 0.03 <= h <= 0.17:
            warm += 1
    return warm > len(px) * 0.4


def names(faith):
    return [k + '_custom' for k, f in SOURCES.items() if f == faith]


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    for src in SOURCES:
        im = Image.open(ICONS + src + '.dds').convert('RGBA')
        big = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
        bg = Image.new('RGBA', (big.width + 80, big.height + 80), (0, 255, 0, 255))
        bg.alpha_composite(big, (40, 40))
        png = os.path.join(tmp, src + '.png')
        bg.convert('RGB').save(png)
        palette = PALETTE.get(src) or (SILVER if is_warm(im) else GOLD)
        subprocess.run([sys.executable, MOD + 'tools/make_faith_icon.py', png, src + '_custom', '--palette', palette],
                       check=True, stdout=subprocess.DEVNULL)
    print(len(SOURCES), 'icons written')
    if '--preview' in sys.argv:
        keys = list(SOURCES)
        sheet = Image.new('RGBA', (110 * 11, 220 * ((len(keys) + 10) // 11)), (60, 60, 60, 255))
        for i, k in enumerate(keys):
            x, y = (i % 11) * 110, (i // 11) * 220
            sheet.alpha_composite(Image.open(ICONS + k + '.dds').convert('RGBA').resize((100, 100)), (x + 5, y + 5))
            sheet.alpha_composite(Image.open(ICONS + k + '_custom.dds').convert('RGBA').resize((100, 100)), (x + 5, y + 110))
        sheet.save(sys.argv[sys.argv.index('--preview') + 1])
