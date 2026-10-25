# Black-on-white Gemini silhouette -> 124x124 vanilla-style domicile building icon (black RGB, alpha = darkness, no mips)
# usage: python make_domicile_icon.py <src> <out.dds> [preview.png] [line_grow_px]
import sys
import numpy as np
from PIL import Image, ImageFilter

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/domicile_building/domicile_building_library.dds'
SIZE, PAD = 124, 11

src, out = sys.argv[1], sys.argv[2]
preview = sys.argv[3] if len(sys.argv) > 3 else None
grow = int(sys.argv[4]) if len(sys.argv) > 4 else 9

lum = Image.open(src).convert('L')
# Widen the white detail lines so they survive the downscale (a min filter on darkness = max filter on white)
if grow > 0:
    lum = lum.filter(ImageFilter.MaxFilter(grow * 2 + 1))
dark = 255 - np.array(lum).astype(np.float32)
# Clean JPEG noise: near-white -> 0, near-black -> 255
dark = np.clip((dark - 40) * 255.0 / (215 - 40), 0, 255)
ys, xs = np.nonzero(dark > 20)
dark = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = dark.shape
inner = SIZE - 2 * PAD
scale = inner / max(h, w)
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
    sheet = Image.new('RGBA', (SIZE * 2 + 30 + 248, 260), (200, 190, 160, 255))
    icon = Image.fromarray(np.dstack([np.zeros((SIZE, SIZE, 3), np.uint8), al]), 'RGBA')
    van = Image.open(VANILLA).convert('RGBA')
    sheet.alpha_composite(van, (10, 10))
    sheet.alpha_composite(icon, (SIZE + 20, 10))
    sheet.alpha_composite(icon.resize((248, 248), Image.NEAREST), (SIZE * 2 + 30, 6))
    sheet.save(preview)
