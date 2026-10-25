# Gemini image of a CoA top decoration on a flat chroma-green background -> gfx/interface/coat_of_arms/<name>_{28,44,62,86,115}.dds:
# jip_mishpacha_topframe (the kippah, 80x48) or jip_exilarch_topframe (the Keter Shem Tov, 96x70)
# Keys out the background, crops to the crown, fits it the way vanilla's crown strip sits (centred, base on the bottom row,
# at most 96x70 of the 128x80 canvas), adds vanilla's soft dark edge and writes uncompressed BGRA like vanilla's topframes.
# usage: python make_mishpacha_crown.py <image> [preview.png] [max_w] [max_h] [name]
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
from make_mishpacha_coa import write_dds, downsample, over, CROWN, MOD, G

src = sys.argv[1]
preview = sys.argv[2] if len(sys.argv) > 2 else None
MAX_W = float(sys.argv[3]) if len(sys.argv) > 3 else 96
MAX_H = float(sys.argv[4]) if len(sys.argv) > 4 else 70
NAME = sys.argv[5] if len(sys.argv) > 5 else 'jip_mishpacha_topframe'

im = np.array(Image.open(src).convert('RGB')).astype(float)
h, w = im.shape[:2]
# background colour: the median of the border
border = np.concatenate([im[0], im[-1], im[:, 0], im[:, -1]])
bg = np.median(border, 0)
# alpha from how much of the background's dominant channel stands above the others (chroma key), so edge pixels
# blended with the background get partial alpha; colour is then unmixed from the background
dom = int(np.argmax(bg))
others = [c for c in range(3) if c != dom]
excess = im[..., dom] - im[..., others].max(-1)
bg_excess = bg[dom] - bg[others].max()
alpha = np.clip(1 - (excess - 0.08 * bg_excess) / (0.8 * bg_excess), 0, 1)
a3 = np.maximum(alpha, 1e-3)[..., None]
im = np.clip((im - (1 - alpha[..., None]) * bg) / a3, 0, 255)
# keep the largest blobs and their soft edges only: drops specks and the faint noise of an uneven background, which
# would otherwise widen the crop and pull the icon off centre
lab, n = ndimage.label(alpha > 0.5)
sizes = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
keep = np.isin(lab, 1 + np.nonzero(sizes >= sizes.max() * 0.002)[0])
keep = ndimage.binary_dilation(keep, iterations=3)
alpha *= keep
# despill: no pixel keeps more of the background's channel than the brightest other channel
im[..., dom] = np.minimum(im[..., dom], im[..., others].max(-1) + 4)

ys, xs = np.nonzero(alpha > 0.05)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
crop = np.dstack([im, alpha * 255])[y0:y1, x0:x1]

# Flatten the base: vanilla's crowns and hats stand on a straight line, but Gemini tends to paint the rim as a curve seen from
# below or above. Fit a parabola to the lowest solid pixel of the columns that reach the lower fifth (the base, not the
# points) and slide each column down so that edge becomes straight
solid = crop[..., 3] > 127
H = crop.shape[0]
bottom = np.where(solid.any(0), H - 1 - np.argmax(solid[::-1], 0), -1)
base_cols = np.nonzero(bottom >= H * 0.8)[0]
curve = np.polyval(np.polyfit(base_cols, bottom[base_cols], 2), np.clip(np.arange(crop.shape[1]), base_cols.min(), base_cols.max()))
shift = np.round(curve.max() - curve).astype(int)
pad = shift.max()
if pad > 0:
    src_rows = np.arange(H + pad)[:, None] - shift[None, :]
    valid = (src_rows >= 0) & (src_rows < H)
    crop = np.take_along_axis(crop, np.clip(src_rows, 0, H - 1)[..., None], 0) * valid[..., None]
    ys, xs = np.nonzero(crop[..., 3] > 0.05 * 255)
    crop = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
print('base flattened by', pad, 'px')

# fit into a 128x80 canvas at 8x
SS = 8
CW, CH = 128 * SS, 80 * SS
BASE = 16                                         # tenths of a 128-unit row between the base and the canvas bottom
scale = min(MAX_W * SS / crop.shape[1], MAX_H * SS / crop.shape[0])
nw, nh = round(crop.shape[1] * scale), round(crop.shape[0] * scale)
fit = downsample(crop, nw, nh) if scale < 1 else np.array(Image.fromarray(crop.astype(np.uint8), 'RGBA').resize((nw, nh), Image.LANCZOS)).astype(float)
canvas = np.zeros((CH, CW, 4))
bx, by = (CW - nw) // 2, CH - BASE * SS // 10 - nh   # the base on row 78 of 80 and the dark edge below it, like vanilla's crowns
canvas[by:by + nh, bx:bx + nw] = fit

# vanilla's crowns have a thin dark edge and a soft shadow below
solid = canvas[..., 3] > 128
edge = ndimage.binary_dilation(solid, iterations=int(0.7 * SS)) & ~solid
ol = np.zeros_like(canvas); ol[..., :3] = (30, 20, 10); ol[..., 3] = ndimage.gaussian_filter(edge.astype(float), 0.3 * SS) * 200
drop = ndimage.gaussian_filter(np.roll(solid.astype(float), int(0.8 * SS), 0), 1.2 * SS)
dr = np.zeros_like(canvas); dr[..., 3] = drop * 120
crown = over(over(dr, ol), canvas)

outs = []
for s, (w_, h_) in CROWN.items():
    hh = round(w_ * 80 / 128)
    img = downsample(crown, w_, hh)
    if hh < h_:
        img = np.concatenate([np.zeros((h_ - hh, w_, 4)), img], 0)
    write_dds(MOD + f'gfx/interface/coat_of_arms/{NAME}_{s}.dds', img, G + f'coat_of_arms/landless_adventurer_topframe_{s}.dds')
    outs.append(img)

if preview:
    sheet = Image.new('RGBA', (sum(o.shape[1] for o in outs) + 10 * len(outs) + 10 + 512, 340), (74, 66, 58, 255))
    x = 10
    for o in outs:
        sheet.alpha_composite(Image.fromarray(o.astype(np.uint8), 'RGBA'), (x, 330 - o.shape[0])); x += o.shape[1] + 10
    big = Image.fromarray(outs[-1].astype(np.uint8), 'RGBA').resize((512, 320), Image.LANCZOS)
    sheet.alpha_composite(big, (x, 10))
    sheet.save(preview)
print('ok', crop.shape[1], 'x', crop.shape[0], '->', nw // SS, 'x', nh // SS)
