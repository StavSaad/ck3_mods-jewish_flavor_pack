# Gemini stained-glass panel on white -> 548x140 bookmark start button (uncompressed BGRA DDS with mips), fitted to the
# area vanilla's buttons fill (x 17-530, y 21-118).
# usage: python make_bookmark_button.py <src> <out.dds> <preview.png>
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

VANILLA = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/bookmarks/start_buttons/bm_1066_hastings.dds'
W, H = 548, 140
X0, X1, Y0, Y1 = 17, 531, 21, 119  # vanilla's filled area (exclusive ends)

src, out, preview = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert('RGB')
w, h = im.size
# Background: near-white connected to the border
mark = (255, 0, 255)
filled = im.copy()
for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
    if all(c >= 230 for c in filled.getpixel(seed)):
        ImageDraw.floodfill(filled, seed, mark, thresh=25)
bg = np.all(np.array(filled) == mark, axis=-1)
alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
rgba = im.convert('RGBA')
rgba.putalpha(alpha)
bbox = alpha.point(lambda v: 255 if v > 10 else 0).getbbox()
print('panel bbox', bbox, 'aspect', round((bbox[2] - bbox[0]) / (bbox[3] - bbox[1]), 2), 'target aspect', round((X1 - X0) / (Y1 - Y0), 2))
rgba = rgba.crop(bbox)


def premul_resize(img, size):
    a = np.array(img).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    r = Image.fromarray((a * 255).round().astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)
    b = np.array(r).astype(np.float32) / 255
    with np.errstate(divide='ignore', invalid='ignore'):
        b[..., :3] = np.where(b[..., 3:4] > 0, b[..., :3] / b[..., 3:4], 0)
    return Image.fromarray((np.clip(b, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


button = Image.new('RGBA', (W, H), (0, 0, 0, 0))
button.alpha_composite(premul_resize(rgba, (X1 - X0, Y1 - Y0)), (X0, Y0))

# Uncompressed A8R8G8B8 DDS with a full mip chain
levels, lw, lh = [], W, H
img = button
while True:
    levels.append(np.array(img)[..., [2, 1, 0, 3]].tobytes())
    if lw == 1 and lh == 1:
        break
    lw, lh = max(1, lw // 2), max(1, lh // 2)
    img = premul_resize(button, (lw, lh))
header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, 0x2100F, H, W, W * 4, 0, len(levels), b'\0' * 44,
                     32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x401008, 0, 0, 0, 0)
open(out, 'wb').write(header + b''.join(levels))
print('mips', len(levels), 'bytes', len(header) + sum(map(len, levels)))

# Preview: vanilla, ours, and ours over vanilla's outline
van = Image.open(VANILLA).convert('RGBA')
sheet = Image.new('RGBA', (W, H * 3 + 20), (40, 40, 40, 255))
sheet.alpha_composite(van, (0, 0))
sheet.alpha_composite(button, (0, H + 10))
outline = van.getchannel('A').point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.FIND_EDGES)
ov = button.copy()
ov.alpha_composite(Image.merge('RGBA', (outline, Image.new('L', (W, H), 0), Image.new('L', (W, H), 0), outline)))
sheet.alpha_composite(ov, (0, 2 * H + 20))
sheet.save(preview)
