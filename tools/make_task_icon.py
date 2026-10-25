# Painted Gemini object on a white background + a ring from make_task_rings.py -> 140x140 court position task icon
# (BGRA with 8 mips, like vanilla). The object sits over the ring, with the vanilla black outline and shadow.
# usage: python make_task_icon.py <src> <ring.png> <out.dds> [preview.png]
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/court_position_task_types/high_almoner_attend_poor.dds'
SIZE = 140
OBJ_BOX = 116  # vanilla objects fill the ring and spill over it a little
BG_TOLERANCE = 18

src, ring_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
preview = sys.argv[4] if len(sys.argv) > 4 else None


def cutout(path):
    im = Image.open(path).convert('RGB')
    # Background = near-white connected to the border, plus enclosed patches of almost pure white (gaps between chair
    # legs, chain links, bag strings). Small specks are left alone, since they may be highlights on the object.
    mark = (255, 0, 255)
    filled = im.copy()
    w, h = filled.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if all(c >= 255 - BG_TOLERANCE for c in filled.getpixel(seed)):
            ImageDraw.floodfill(filled, seed, mark, thresh=BG_TOLERANCE)
    bg = np.all(np.array(filled) == mark, axis=-1)
    px = np.array(im).astype(int)
    near_white = np.all(px >= 248, axis=-1) & ~bg
    labels, n = ndimage.label(near_white)
    if n:
        sizes = ndimage.sum(near_white, labels, range(1, n + 1))
        bg |= np.isin(labels, np.nonzero(sizes > w * h * 0.0002)[0] + 1)
    # The soft grey shading Gemini paints around the object and inside its gaps: grow the background through colourless
    # pixels brighter than the outline. The dark outline stops it, so grey parts of the object (coins, iron) are kept.
    halo = ((px.max(axis=-1) - px.min(axis=-1)) < 10) & (px.mean(axis=-1) > 80)
    labels, n = ndimage.label(halo | bg)
    if n:
        bg |= np.isin(labels, np.unique(labels[bg]))
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.convert('RGBA')
    rgba.putalpha(alpha)
    return rgba.crop(alpha.point(lambda v: 255 if v > 10 else 0).getbbox())


def premul_resize(img, size):
    a = np.array(img).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    r = Image.fromarray((a * 255).round().astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)
    b = np.array(r).astype(np.float32) / 255
    with np.errstate(divide='ignore', invalid='ignore'):
        b[..., :3] = np.where(b[..., 3:4] > 0, b[..., :3] / b[..., 3:4], 0)
    return Image.fromarray((np.clip(b, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


rgba = cutout(src)
cw, ch = rgba.size
scale = OBJ_BOX / max(cw, ch)
nw, nh = round(cw * scale), round(ch * scale)
obj = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
obj.alpha_composite(premul_resize(rgba, (nw, nh)), ((SIZE - nw) // 2, (SIZE - nh) // 2))

# Black outline and soft shadow around the object, at twice the court position icon's size
oa = obj.getchannel('A')
outline = oa.filter(ImageFilter.MaxFilter(3))
glow = outline.filter(ImageFilter.GaussianBlur(2.2))
glow_shifted = Image.new('L', glow.size, 0)
glow_shifted.paste(glow, (2, 2))
shadow_a = np.maximum(np.array(outline, np.float32), np.maximum(np.array(glow, np.float32), np.array(glow_shifted, np.float32)) * 1.4)
shadow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
shadow.putalpha(Image.fromarray(np.clip(shadow_a, 0, 255).astype(np.uint8)))

icon = Image.open(ring_path).convert('RGBA')
icon.alpha_composite(shadow)
icon.alpha_composite(obj)

header = open(VANILLA, 'rb').read(128)
data = b''
level, s = icon, SIZE
while True:
    data += np.array(level)[..., [2, 1, 0, 3]].tobytes()  # RGBA -> BGRA
    if s == 1:
        break
    s = max(1, s // 2)
    level = premul_resize(icon, (s, s))
open(out, 'wb').write(header + data)

if preview:
    icon.save(preview)
