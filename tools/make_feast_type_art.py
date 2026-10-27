# Builds a feast variant's art for the feast planning window, where the engine looks it up by the option's key:
# - gfx/interface/illustrations/activity_types/<variant>.dds: the tall painting (460x1100, like vanilla's
#   feast_type_tsagaan_sar.dds), cropped from a Gemini painting around a horizontal centre (0-1, default 0.5)
# - gfx/interface/icons/activity_types/<variant>_icon.dds: the small glyph (78x78 with mips), pure black with alpha like
#   vanilla's feast_type_generic_icon.dds, from a Gemini black silhouette on white, 46 px tall like vanilla's (a wide
#   glyph up to 62 px across)
# Usage: make_feast_type_art.py <variant> [--painting <image> [--x <0-1>]] [--icon <silhouette>] [--preview <png>]
# The variants are the options make_feast_override.py adds (jip_feast_type_akitu and so on).
import struct
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
VANILLA = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/'
ILL_W, ILL_H = 460, 1100
ICON, GLYPH_H, GLYPH_W = 78, 46, 62   # vanilla's glyphs stand about 46 px tall; wide ones may spread to 62

args = sys.argv[1:]
variant = args[0]
opt = {k: args[args.index(k) + 1] for k in ('--painting', '--x', '--icon', '--preview') if k in args}


def dds(levels, w, h):
    """Uncompressed A8R8G8B8 DDS; levels are RGBA arrays, largest first."""
    flags = 0x100F | (0x20000 if len(levels) > 1 else 0)
    caps = 0x1000 | (0x400008 if len(levels) > 1 else 0)
    header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, flags, h, w, w * 4, 0, len(levels), b'\0' * 44,
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, caps, 0, 0, 0, 0)
    return header + b''.join(lv[..., [2, 1, 0, 3]].tobytes() for lv in levels)


def premul_resize(rgba, size):
    arr = rgba.astype(np.float32) / 255
    pm = np.dstack([arr[..., :3] * arr[..., 3:4], arr[..., 3:4]])
    p = np.asarray(Image.fromarray((pm * 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)).astype(np.float32) / 255
    al = p[..., 3:4]
    rgb = np.where(al > 0, p[..., :3] / np.maximum(al, 1e-6), 0)
    return (np.dstack([rgb, al]).clip(0, 1) * 255).astype(np.uint8)


out = []
if '--painting' in opt:
    im = Image.open(opt['--painting']).convert('RGB')
    w, h = im.size
    # Crop to 460:1100 around the chosen centre, then scale
    if w / h > ILL_W / ILL_H:
        cw = round(h * ILL_W / ILL_H)
        cx = float(opt.get('--x', 0.5)) * w
        x0 = int(min(max(cx - cw / 2, 0), w - cw))
        im = im.crop((x0, 0, x0 + cw, h))
    else:
        ch = round(w * ILL_H / ILL_W)
        y0 = (h - ch) // 2
        im = im.crop((0, y0, w, y0 + ch))
    ill = np.dstack([np.asarray(im.resize((ILL_W, ILL_H), Image.LANCZOS)), np.full((ILL_H, ILL_W), 255, np.uint8)])
    open(MOD + f'gfx/interface/illustrations/activity_types/{variant}.dds', 'wb').write(dds([ill], ILL_W, ILL_H))
    out.append(Image.fromarray(ill, 'RGBA'))

if '--icon' in opt:
    g = np.asarray(Image.open(opt['--icon']).convert('L')).astype(np.float32)
    alpha = np.clip((235 - g) / 150, 0, 1)        # dark ink on white
    lab, n = ndimage.label(alpha > 0.5)
    if n > 1:                                      # drop specks under 1% of the largest piece
        sizes = ndimage.sum(alpha > 0.5, lab, range(1, n + 1))
        alpha *= ndimage.binary_dilation(np.isin(lab, 1 + np.where(sizes >= 0.01 * sizes.max())[0]), iterations=3)
    ys, xs = np.where(alpha > 0.03)
    alpha = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    glyph = np.dstack([np.zeros(alpha.shape + (3,), np.uint8), (alpha * 255).astype(np.uint8)])
    gh, gw = glyph.shape[:2]
    sc = min(GLYPH_H / gh, GLYPH_W / gw)
    small = premul_resize(glyph, (max(1, round(gw * sc)), max(1, round(gh * sc))))
    icon = np.zeros((ICON, ICON, 4), np.uint8)
    y0, x0 = (ICON - small.shape[0]) // 2, (ICON - small.shape[1]) // 2
    icon[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small
    icon[..., :3] = 0
    levels, size = [icon], ICON
    while size > 1:
        size = max(1, size // 2)
        levels.append(premul_resize(icon, (size, size)))
    open(MOD + f'gfx/interface/icons/activity_types/{variant}_icon.dds', 'wb').write(dds(levels, ICON, ICON))
    out.append(Image.fromarray(icon, 'RGBA'))

if '--preview' in opt:
    # Ours next to vanilla's Tsagaan Sar, on the planning window's dark brown
    van = [Image.open(VANILLA + 'illustrations/activity_types/feast_type_tsagaan_sar.dds').convert('RGBA'),
           Image.open(VANILLA + 'icons/activity_types/feast_type_tsagaan_sar_icon.dds').convert('RGBA')]
    tiles = [t.resize((t.width // 2, t.height // 2), Image.LANCZOS) if t.width > ICON else t for t in out + van]
    sheet = Image.new('RGBA', (sum(t.width + 10 for t in tiles) + 10, ILL_H // 2 + 20), (60, 50, 40, 255))
    x = 10
    for t in tiles:
        sheet.alpha_composite(t, (x, 10))
        x += t.width + 10
    sheet.save(opt['--preview'])
print(variant, 'written:', ', '.join(k[2:] for k in ('--painting', '--icon') if k in opt))
