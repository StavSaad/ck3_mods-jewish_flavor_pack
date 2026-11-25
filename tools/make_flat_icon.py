# Black-on-white Gemini silhouette -> 60x60 vanilla-style flat icon (black RGB, alpha = darkness, no mips),
# like vanilla's gfx/interface/icons/flat_icons (the lobby's ruler designer buttons use them)
# usage: python make_flat_icon.py <src> <out.dds> [preview.png] [line_grow_px: >0 widens white lines, <0 thickens black]
import sys
import numpy as np
from PIL import Image, ImageFilter

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/flat_icons/merchant_government.dds'
SIZE, PAD = 60, 5

src, out = sys.argv[1], sys.argv[2]
preview = sys.argv[3] if len(sys.argv) > 3 else None
grow = int(sys.argv[4]) if len(sys.argv) > 4 else 0

lum = Image.open(src).convert('L')
# Widen the white detail lines (grow > 0) or thicken the black strokes (grow < 0) so they survive the downscale
if grow > 0:
    lum = lum.filter(ImageFilter.MaxFilter(grow * 2 + 1))
elif grow < 0:
    lum = lum.filter(ImageFilter.MinFilter(-grow * 2 + 1))
dark = 255 - np.array(lum).astype(np.float32)
dark = np.clip((dark - 40) * 255.0 / (215 - 40), 0, 255)
ys, xs = np.nonzero(dark > 20)
dark = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = dark.shape
scale = (SIZE - 2 * PAD) / max(h, w)
nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
a = Image.fromarray(dark.astype(np.uint8)).resize((nw, nh), Image.LANCZOS)
alpha = Image.new('L', (SIZE, SIZE), 0)
alpha.paste(a, ((SIZE - nw) // 2, (SIZE - nh) // 2))
al = np.array(alpha)

bgra = np.zeros((SIZE, SIZE, 4), np.uint8)
bgra[..., 3] = al
header = open(VANILLA, 'rb').read(128)
with open(out, 'wb') as f:
    f.write(header)
    f.write(bgra.tobytes())

if preview:
    sheet = Image.new('RGBA', (SIZE * 2 + 30 + 240, 260), (200, 190, 160, 255))
    icon = Image.fromarray(np.dstack([np.zeros((SIZE, SIZE, 3), np.uint8), al]), 'RGBA')
    van = Image.open(VANILLA).convert('RGBA')
    van = Image.fromarray(np.dstack([np.zeros((SIZE, SIZE, 3), np.uint8), np.array(van)[..., 3]]), 'RGBA')
    sheet.alpha_composite(van, (10, 10))
    sheet.alpha_composite(icon, (SIZE + 20, 10))
    sheet.alpha_composite(icon.resize((240, 240), Image.NEAREST), (SIZE * 2 + 30, 10))
    sheet.save(preview)
