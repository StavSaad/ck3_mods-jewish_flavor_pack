# Gemini full-bleed stained-glass panel -> 580x160 bookmark tab (icons/bookmark_buttons), cut to the shape of vanilla's
# tabs (bm_mask.dds alpha), written as uncompressed BGRA DDS with mips.
# usage: python make_bookmark_tab.py <src> <out.dds> <preview.png> [trim_px] [brightness] [saturation]
import struct
import sys
import numpy as np
from PIL import Image, ImageEnhance

V = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/'
W, H = 580, 160

src, out, preview = sys.argv[1], sys.argv[2], sys.argv[3]
trim = int(sys.argv[4]) if len(sys.argv) > 4 else 14
bright = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
sat = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0

im = Image.open(src).convert('RGB')
w, h = im.size
im = im.crop((trim, trim, w - trim, h - trim))  # Gemini's thin dark edge
# Fill the tab's aspect by cropping the excess, centred
w, h = im.size
if w / h > W / H:
    nw = round(h * W / H)
    im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = round(w * H / W)
    im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
im = im.resize((W, H), Image.LANCZOS)
im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(sat)).enhance(bright)

tab = im.convert('RGBA')
tab.putalpha(Image.open(V + 'bookmarks/bm_mask.dds').convert('RGBA').getchannel('A'))


def premul_resize(img, size):
    a = np.array(img).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    r = Image.fromarray((a * 255).round().astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)
    b = np.array(r).astype(np.float32) / 255
    with np.errstate(divide='ignore', invalid='ignore'):
        b[..., :3] = np.where(b[..., 3:4] > 0, b[..., :3] / b[..., 3:4], 0)
    return Image.fromarray((np.clip(b, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


levels, lw, lh, img = [], W, H, tab
while True:
    levels.append(np.array(img)[..., [2, 1, 0, 3]].tobytes())
    if lw == 1 and lh == 1:
        break
    lw, lh = max(1, lw // 2), max(1, lh // 2)
    img = premul_resize(tab, (lw, lh))
header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, 0x2100F, H, W, W * 4, 0, len(levels), b'\0' * 44,
                     32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, 0x401008, 0, 0, 0, 0)
open(out, 'wb').write(header + b''.join(levels))

sheet = Image.new('RGBA', (W, 3 * (H + 10)), (40, 40, 40, 255))
for i, t in enumerate([Image.open(V + 'icons/bookmark_buttons/bm_867_persia.dds').convert('RGBA'), tab,
                       Image.open(V + 'icons/bookmark_buttons/bm_1066_hastings.dds').convert('RGBA')]):
    sheet.alpha_composite(t, (0, i * (H + 10)))
sheet.save(preview)
print('mips', len(levels))
