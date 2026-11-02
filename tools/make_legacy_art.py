# A Gemini panorama -> a dynasty legacy track's illustration, gfx/interface/illustrations/legacy_tracks/<track>.dds:
# 4216x368 like vanilla's, uncompressed. The game stretches it across the perk row, so it must keep that 11.5:1 shape; a
# painting Gemini can make (about 21:9) gives only a thin full-width band, so the band is taken a little taller and squeezed
# into the strip (--stretch, the horizontal stretch: 1.2 is hardly visible in a painting).
# usage: python make_legacy_art.py <painting> <track> [--y <band centre, 0-1 of the height>] [--stretch 1.2] [--preview p.png]
import struct
import sys
import numpy as np
from PIL import Image

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
W, H = 4216, 368

args = sys.argv[1:]
src, track = args[0], args[1]
opt = {k: args[args.index(k) + 1] for k in ('--y', '--stretch', '--preview') if k in args}
centre = float(opt.get('--y', 0.5))
stretch = float(opt.get('--stretch', 1.2))


def dds(rgba):
    """Uncompressed A8R8G8B8 DDS, no mips"""
    h, w = rgba.shape[:2]
    header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, 0x100F, h, w, w * 4, 0, 1, b'\0' * 44,
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0, 0, 0, 0)
    return header + rgba[..., [2, 1, 0, 3]].tobytes()


im = Image.open(src).convert('RGBA')
band = round(im.width * H / W * stretch)
assert band <= im.height, 'the painting is too low for this stretch'
top = min(max(0, round(centre * im.height - band / 2)), im.height - band)
strip = im.crop((0, top, im.width, top + band)).resize((W, H), Image.LANCZOS)
out = MOD + f'gfx/interface/illustrations/legacy_tracks/{track}.dds'
open(out, 'wb').write(dds(np.array(strip)))
print('wrote', out, 'from rows', top, 'to', top + band)
if '--preview' in opt:
    strip.resize((W // 3, H // 3), Image.LANCZOS).save(opt['--preview'])
