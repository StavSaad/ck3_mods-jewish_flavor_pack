# Painted Gemini image on a white background -> 70x70 court position icon (BGRA with 7 mips, like vanilla)
# usage: python make_court_position_icon.py <src> <out.dds> [preview.png]
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/court_position_types/court_tutor_court_position.dds'
SIZE, PAD = 70, 4  # the padding leaves room for the shadow
BG_TOLERANCE = 18  # how far from pure white still counts as background

src, out = sys.argv[1], sys.argv[2]
preview = sys.argv[3] if len(sys.argv) > 3 else None

im = Image.open(src).convert('RGB')
# Background = near-white pixels connected to the border; the dark outline stops the fill, so white parts of the
# object itself (cloth, parchment) are kept
mark = (255, 0, 255)
filled = im.copy()
w, h = filled.size
for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
    if all(c >= 255 - BG_TOLERANCE for c in filled.getpixel(seed)):
        ImageDraw.floodfill(filled, seed, mark, thresh=BG_TOLERANCE)
bg = np.all(np.array(filled) == mark, axis=-1)
# Background enclosed by the object (e.g. inside a key ring): larger patches of almost pure white. Off-white object
# parts (cloth, parchment) are darker than this and are kept.
from scipy import ndimage
near_white = np.all(np.array(im) >= 250, axis=-1) & ~bg
labels, n = ndimage.label(near_white)
if n:
    sizes = ndimage.sum(near_white, labels, range(1, n + 1))
    for i, size in enumerate(sizes, 1):
        if size > im.size[0] * im.size[1] * 0.002:
            bg |= labels == i
alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
# Soften the cut edge a little so the downscale doesn't leave a white halo
alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
rgba = im.convert('RGBA')
rgba.putalpha(alpha)

bbox = alpha.point(lambda v: 255 if v > 10 else 0).getbbox()
rgba = rgba.crop(bbox)
cw, ch = rgba.size
inner = SIZE - 2 * PAD
scale = inner / max(cw, ch)
nw, nh = max(1, round(cw * scale)), max(1, round(ch * scale))


def premul_resize(img, size):
    a = np.array(img).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    r = Image.fromarray((a * 255).round().astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)
    b = np.array(r).astype(np.float32) / 255
    with np.errstate(divide='ignore', invalid='ignore'):
        b[..., :3] = np.where(b[..., 3:4] > 0, b[..., :3] / b[..., 3:4], 0)
    return Image.fromarray((np.clip(b, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


obj = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
obj.alpha_composite(premul_resize(rgba, (nw, nh)), ((SIZE - nw) // 2, (SIZE - nh) // 2))

# Vanilla-style black edge: a 1px solid outline around the object, then a soft glow fading over ~3px, slightly
# heavier towards the lower right
oa = obj.getchannel('A')
outline = oa.filter(ImageFilter.MaxFilter(3))
glow = outline.filter(ImageFilter.GaussianBlur(1.3))
glow_shifted = Image.new('L', glow.size, 0)
glow_shifted.paste(glow, (1, 1))
shadow_a = np.maximum(np.array(outline, np.float32), np.maximum(np.array(glow, np.float32), np.array(glow_shifted, np.float32)) * 1.4)
shadow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
shadow.putalpha(Image.fromarray(np.clip(shadow_a, 0, 255).astype(np.uint8)))
icon = shadow
icon.alpha_composite(obj)

header = open(VANILLA, 'rb').read(128)
data = b''
level, s = icon, SIZE
while True:
    arr = np.array(level)
    data += arr[..., [2, 1, 0, 3]].tobytes()  # RGBA -> BGRA
    if s == 1:
        break
    s = max(1, s // 2)
    level = premul_resize(icon, (s, s))
open(out, 'wb').write(header + data)

if preview:
    sheet = Image.new('RGBA', (SIZE * 2 + 30 + 140, 150), (60, 50, 40, 255))
    van = Image.open(VANILLA).convert('RGBA')
    sheet.alpha_composite(van, (10, 10))
    sheet.alpha_composite(icon, (SIZE + 20, 10))
    sheet.alpha_composite(icon.resize((140, 140), Image.LANCZOS), (SIZE * 2 + 30, 5))
    sheet.save(preview)
