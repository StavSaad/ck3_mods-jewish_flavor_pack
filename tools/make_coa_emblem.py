# Builds a vanilla-style colored CoA emblem (gfx/coat_of_arms/colored_emblems/<name>.dds, 256x256 with mips) from a
# Gemini drawing in flat code colours on a flat background (read from the corners):
#   white = color1, red = color2, green = color3, black lines = shading inside the nearest colour
# Vanilla's emblems encode the colour regions in the channels: blue alone is color1, red adds color2, green adds color3,
# and the blue level is the shading (vanilla uses about 96-128; lines darker). So each CoA can recolour the emblem's
# three parts (colored_emblem = { color1 color2 color3 }).
# Usage: make_coa_emblem.py <drawing> <name> [--preview <png> --colors <c1>,<c2>,<c3>]
# Register the emblem in gfx/coat_of_arms/colored_emblems/jip_coa_emblems.txt to show it in the CoA designer.
import struct
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
SIZE, FIT = 256, 240          # the emblem's longer side, leaving a small margin
FLAT, LINE = 120, 56          # blue (shading) levels: flat colour, fold lines

args = sys.argv[1:]
src, name = args[0], args[1]
opt = {k: args[args.index(k) + 1] for k in ('--preview', '--colors') if k in args}

im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
corners = np.concatenate([im[:20, :20].reshape(-1, 3), im[-20:, -20:].reshape(-1, 3)])
bg = np.median(corners, 0)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
lum = im @ np.array([0.299, 0.587, 0.114], np.float32)

# Shape: everything not the background colour
alpha = np.clip((np.abs(im - bg).max(2) - 40) / 60, 0, 1)
solid = alpha > 0.5
lab, n = ndimage.label(solid)
if n > 1:                                      # drop specks under 1% of the largest piece
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    alpha *= ndimage.binary_dilation(np.isin(lab, 1 + np.where(sizes >= 0.01 * sizes.max())[0]), iterations=2)

# Regions by code colour; black lines take the region they sit in
white = (lum > 170) & (np.abs(r - g) < 50) & (np.abs(g - b) < 50)
red = (r > 150) & (g < 110) & (b < 110)
green = (g > 120) & (r < 140) & (b < 140) & ~white
region = np.zeros(lum.shape, np.int8)       # 0 none, 1 color1, 2 color2, 3 color3
region[white], region[red], region[green] = 1, 2, 3
_, (iy, ix) = ndimage.distance_transform_edt(region == 0, return_indices=True)
region = region[iy, ix]
line = np.clip((110 - lum) / 80, 0, 1)      # dark ink -> shading

out = np.zeros(im.shape[:2] + (4,), np.float32)
out[..., 0] = np.where(region == 2, 224, 0)
out[..., 1] = np.where(region == 3, 224, 0)
out[..., 2] = FLAT + (LINE - FLAT) * line
out[..., 3] = alpha * 255

# Crop to the shape, fit into a square with a margin
ys, xs = np.where(alpha > 0.05)
out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = out.shape[:2]
sc = FIT / max(h, w)
small = np.asarray(Image.fromarray(out.astype(np.uint8), 'RGBA').resize((max(1, round(w * sc)), max(1, round(h * sc))),
                                                                       Image.LANCZOS))
emblem = np.zeros((SIZE, SIZE, 4), np.uint8)
y0, x0 = (SIZE - small.shape[0]) // 2, (SIZE - small.shape[1]) // 2
emblem[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small

# Uncompressed A8R8G8B8 DDS with mips
levels, img, s = [emblem], Image.fromarray(emblem, 'RGBA'), SIZE
while s > 1:
    s //= 2
    levels.append(np.asarray(img.resize((s, s), Image.LANCZOS)))
header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, 0x2100F, SIZE, SIZE, SIZE * 4, 0, len(levels), b'\0' * 44,
                     32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x401008, 0, 0, 0, 0)
open(MOD + f'gfx/coat_of_arms/colored_emblems/{name}.dds', 'wb').write(
    header + b''.join(lv[..., [2, 1, 0, 3]].tobytes() for lv in levels))

if '--preview' in opt:
    # An approximation of the game's tinting: each region's colour, darkened by the shading
    cols = [np.array([int(c.strip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
            for c in opt.get('--colors', 'ffffff,d4af37,3c9a3c').split(',')]
    e = emblem.astype(np.float32)
    c2, c3 = e[..., 0:1] / 224, e[..., 1:2] / 224
    base = cols[0] * (1 - c2 - c3) + cols[1] * c2 + cols[2] * c3
    shade = np.clip(e[..., 2:3] / FLAT, 0, 1.2)
    rgb = np.clip(base * shade, 0, 255)
    tile = Image.fromarray(np.dstack([rgb, e[..., 3:4]]).astype(np.uint8), 'RGBA')
    sheet = Image.new('RGBA', (SIZE * 2 + 30, SIZE + 20), (30, 60, 160, 255))
    sheet.alpha_composite(tile, (10, 10))
    sheet.alpha_composite(tile.resize((64, 64), Image.LANCZOS), (SIZE + 20, 10))
    sheet.save(opt['--preview'])
print(name, 'written')
