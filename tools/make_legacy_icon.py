# Black-on-white Gemini silhouette -> 140x140 vanilla-style dynasty legacy track icon
# (gfx/interface/icons/dynasty/<track>.dds: black RGB, alpha = darkness, no mips), the glyph fitted in the middle like vanilla's
# usage: python make_legacy_icon.py <src> <track_name> [preview.png] [box_px]
# box_px: the glyph's longest side (default 84, like vanilla's; a tall, thin glyph reads better larger, e.g. 104)
import sys
import numpy as np
from PIL import Image

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/dynasty/blood_legacy_track.dds'
SIZE = 140

src, name = sys.argv[1], sys.argv[2]
preview = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
BOX = int(sys.argv[4]) if len(sys.argv) > 4 else 84 # vanilla's glyphs fill about 80 pixels of the 140
out = MOD + f'gfx/interface/icons/dynasty/{name}.dds'

dark = 255 - np.array(Image.open(src).convert('L')).astype(np.float32)
# Clean JPEG noise: near-white -> 0, near-black -> 255
dark = np.clip((dark - 40) * 255.0 / (215 - 40), 0, 255)
ys, xs = np.nonzero(dark > 20)
dark = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = dark.shape
scale = BOX / max(h, w)
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
print('wrote', out)

if preview:
    sheet = Image.new('RGBA', (SIZE * 2 + 30 + 280, 300), (200, 190, 160, 255))
    icon = Image.fromarray(np.dstack([np.zeros((SIZE, SIZE, 3), np.uint8), al]), 'RGBA')
    van = Image.open(VANILLA).convert('RGBA')
    sheet.alpha_composite(van, (10, 10))
    sheet.alpha_composite(icon, (SIZE + 20, 10))
    sheet.alpha_composite(icon.resize((280, 280), Image.NEAREST), (SIZE * 2 + 30, 10))
    small = icon.resize((40, 40), Image.LANCZOS)
    sheet.alpha_composite(small, (10, SIZE + 30))
    sheet.alpha_composite(van.resize((40, 40), Image.LANCZOS), (60, SIZE + 30))
    sheet.save(preview)
