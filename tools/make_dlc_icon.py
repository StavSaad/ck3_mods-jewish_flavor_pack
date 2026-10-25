# Builds the mod's "DLC" icon: a Gemini painting set in vanilla's flavour-pack frame (Northern Lords, Fate of Iberia and
# Legacy of Persia share it). The frame is the pixels those three icons have in common; the opening is everything else.
# Usage: python make_dlc_icon.py <painting> <x0> <y0> <size> [preview.png]
#   x0 y0 size: the square of the painting (in its own pixels) that fills the 120x120 icon; the frame covers ~12 px a side
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

DLC = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/dlc/'
OUT = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/gfx/interface/icons/dlc/jip_rising_lion.dds'
FLAVOUR_PACKS = (3, 5, 10)
S = 120


def load(n):
    return np.asarray(Image.open(DLC + f'dlc_{n:03d}.dds').convert('RGBA')).astype(np.float64)


def frame_and_opening():
    icons = [load(n) for n in FLAVOUR_PACKS]
    same = np.ones((S, S), bool)
    for other in icons[1:]:
        same &= np.abs(icons[0] - other).max(2) < 10
    inside = icons[0][..., 3] > 0
    diff = ndimage.binary_closing(~same & inside, iterations=2)
    lab, n = ndimage.label(diff)
    biggest = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
    opening = ndimage.binary_fill_holes(biggest)
    return icons[0], opening


def main():
    src, x0, y0, size = sys.argv[1], *map(int, sys.argv[2:5])
    preview = sys.argv[5] if len(sys.argv) > 5 else None
    frame, opening = frame_and_opening()
    art = Image.open(src).convert('RGB').crop((x0, y0, x0 + size, y0 + size))
    art = np.asarray(art.resize((S, S), Image.LANCZOS)).astype(np.float64)
    # vanilla's art darkens toward the frame: an inner shadow of a few pixels
    dist = ndimage.distance_transform_edt(opening)
    art *= (1 - 0.55 * np.exp(-(dist - 1) / 1.8).clip(0, 1))[..., None]
    m = ndimage.gaussian_filter(opening.astype(np.float64), 0.5)[..., None]
    rgb = frame[..., :3] * (1 - m) + art * m
    alpha = np.maximum(frame[..., 3], opening * 255.0)
    out = np.dstack([rgb, alpha]).clip(0, 255).astype(np.uint8)
    hdr = open(DLC + 'dlc_003.dds', 'rb').read(128)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'wb').write(hdr + out[..., [2, 1, 0, 3]].tobytes())
    print('wrote', OUT)
    if preview:
        # ours beside the three flavour packs, at 2x and at the in-game sizes (DLC_ICON_DISPLAY_SIZE 37 42 47)
        icons = [out] + [load(n).astype(np.uint8) for n in FLAVOUR_PACKS]
        sheet = Image.new('RGBA', (4 * 250 + 10, 250 + 70), (45, 40, 35, 255))
        for k, ic in enumerate(icons):
            im = Image.fromarray(ic, 'RGBA')
            sheet.alpha_composite(im.resize((240, 240), Image.LANCZOS), (10 + k * 250, 5))
            x = 10 + k * 250
            for d in (37, 42, 47):
                sheet.alpha_composite(im.resize((d, d), Image.LANCZOS), (x, 255))
                x += d + 12
        sheet.save(preview)
        print('preview', preview)


main()
