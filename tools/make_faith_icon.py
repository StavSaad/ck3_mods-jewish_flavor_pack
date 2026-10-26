# Builds a vanilla-style faith or rite icon (100x100, uncompressed DDS like vanilla's germanic_reformed.dds) from a
# Gemini emblem painted on flat green (#00FF00), and optionally its reformed version: the same emblem over the soft
# cream glow with faint rays that vanilla's reformed icons have (measured on achamanism_reformed.dds).
# Usage: make_faith_icon.py <image> <icon_name> [--reformed] [--palette <shadow>,<mid>,<highlight>] [--preview <png>]
# Writes gfx/interface/icons/faith/<icon_name>.dds (and <icon_name>_reformed.dds); faiths and rites use it as
# icon = <icon_name>. --palette recolours a neutral (silver) emblem by its brightness, through three hex colours,
# so one painting gives every metal or enamel variant of an icon. --inlay <shadow>,<mid>,<highlight> recolours only
# the accent of a two-tone emblem; --palette then applies to the rest only. The accent is the blue inlay (like the
# Mesopotamian disc's lapis), or with --accent warm the gold parts of a silver emblem (like the Harranian disc).
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
VANILLA = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/faith/'
SIZE = 100
FIT = 94          # the emblem's longer side, leaving a small margin like vanilla's
GLOW_RGB = (170, 155, 132)

args = sys.argv[1:]
reformed = '--reformed' in args
preview = args[args.index('--preview') + 1] if '--preview' in args else None
palette = args[args.index('--palette') + 1] if '--palette' in args else None
inlay = args[args.index('--inlay') + 1] if '--inlay' in args else None
accent = args[args.index('--accent') + 1] if '--accent' in args else 'blue'
src, name = [a for i, a in enumerate(args)
             if not a.startswith('--') and (i == 0 or args[i - 1] not in ('--preview', '--palette', '--inlay', '--accent'))][:2]


def recolour(rgba, pal, region=None):
    """Gradient map: the emblem's brightness (stretched over its own range, or the region's) runs shadow -> mid ->
    highlight."""
    stops = [np.array([int(c.strip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32) for c in pal.split(',')]
    rgb = rgba[..., :3].astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    opaque = rgba[..., 3] > 128
    if region is not None:
        opaque &= region
    lo, hi = np.percentile(lum[opaque], [1, 99.5])
    t = np.clip((lum - lo) / max(hi - lo, 1), 0, 1)[..., None]
    out = np.where(t < 0.5, stops[0] + (stops[1] - stops[0]) * (t / 0.5),
                   stops[1] + (stops[2] - stops[1]) * ((t - 0.5) / 0.5))
    return np.dstack([out, rgba[..., 3:4].astype(np.float32)]).clip(0, 255).astype(np.uint8)


def key_green(im):
    """Alpha from how much green outweighs red and blue; green spill on the edges is pulled back."""
    rgb = im[..., :3].astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    spill = g - np.maximum(r, b)
    alpha = np.clip(1 - (spill - 20) / 90, 0, 1)
    # Drop specks: keep every opaque piece of at least 1% of the largest (an emblem can have separate parts,
    # like a disc inside a ring)
    solid = alpha > 0.5
    lab, n = ndimage.label(solid)
    if n > 1:
        sizes = ndimage.sum(solid, lab, range(1, n + 1))
        keep = np.isin(lab, 1 + np.where(sizes >= 0.01 * sizes.max())[0])
        alpha = alpha * ndimage.binary_dilation(keep, iterations=3)
    rgb[..., 1] = np.where(spill > 0, np.maximum(r, b) + np.minimum(spill, 0) , g)
    return np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)


def down(rgba, size):
    """Resize with premultiplied alpha so no dark or green fringe bleeds in."""
    arr = rgba.astype(np.float32) / 255
    pm = np.dstack([arr[..., :3] * arr[..., 3:4], arr[..., 3:4]])
    p = np.asarray(Image.fromarray((pm * 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)).astype(np.float32) / 255
    al = p[..., 3:4]
    rgb = np.where(al > 0, p[..., :3] / np.maximum(al, 1e-6), 0)
    return (np.dstack([rgb, al]).clip(0, 1) * 255).astype(np.uint8)


def write_dds(rgba, path):
    hdr = open(VANILLA + 'germanic_reformed.dds', 'rb').read(128)   # 100x100, 32-bit BGRA, no mips
    open(path, 'wb').write(hdr + rgba[..., [2, 1, 0, 3]].tobytes())


im = np.asarray(Image.open(src).convert('RGBA'))
cut = key_green(im)
ys, xs = np.where(cut[..., 3] > 8)
cut = cut[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
if inlay:
    # Two-tone: a soft mask of the accent (blue inlay, or warm gold on silver); the rest and the accent are recoloured
    # apart and blended back
    rgbf = cut[..., :3].astype(np.float32)
    if accent == 'warm':
        blue = np.clip((rgbf[..., 0] - rgbf[..., 2] - 30) / 40, 0, 1)
    else:
        blue = np.clip((rgbf[..., 2] - np.maximum(rgbf[..., 0], rgbf[..., 1]) - 10) / 40, 0, 1)
    metal = recolour(cut, palette, blue < 0.5).astype(np.float32) if palette else cut.astype(np.float32)
    stone = recolour(cut, inlay, blue >= 0.5).astype(np.float32)
    w = blue[..., None]
    cut = np.dstack([metal[..., :3] * (1 - w) + stone[..., :3] * w, cut[..., 3:4]]).clip(0, 255).astype(np.uint8)
elif palette:
    cut = recolour(cut, palette)
h, w = cut.shape[:2]
sc = FIT / max(w, h)
small = down(cut, (max(1, round(w * sc)), max(1, round(h * sc))))
icon = np.zeros((SIZE, SIZE, 4), np.uint8)
y0, x0 = (SIZE - small.shape[0]) // 2, (SIZE - small.shape[1]) // 2
icon[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small
write_dds(icon, MOD + f'gfx/interface/icons/faith/{name}.dds')
out = [icon]

if reformed:
    # Glow: falls off with distance from the emblem (about 210 * exp(-d / 5.3) in vanilla), broken into soft rays
    dist = ndimage.distance_transform_edt(icon[..., 3] < 128)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE] - (SIZE - 1) / 2
    theta = np.arctan2(yy, xx)
    rng = np.random.default_rng(3)
    rays = np.zeros(SIZE * 4)
    rays[rng.integers(0, len(rays), 22)] = 1
    rays = ndimage.gaussian_filter1d(rays, 3, mode='wrap')
    rays = rays / rays.max()
    ray = rays[((theta + np.pi) / (2 * np.pi) * (len(rays) - 1)).astype(int)]
    glow_a = 210 * np.exp(-dist / 5.3) * (0.65 + 0.35 * ray) * (1 + 0.6 * ray * np.exp(-dist / 14))
    glow = np.zeros((SIZE, SIZE, 4), np.float32)
    glow[..., :3] = GLOW_RGB
    glow[..., 3] = np.clip(glow_a, 0, 230)
    g = Image.fromarray(glow.astype(np.uint8), 'RGBA')
    g.alpha_composite(Image.fromarray(icon, 'RGBA'))
    ref = np.asarray(g)
    write_dds(ref, MOD + f'gfx/interface/icons/faith/{name}_reformed.dds')
    out.append(ref)

if preview:
    # Ours at 100 px and 3x, next to vanilla's Urartu and Achamanism (reformed) for scale
    van = [np.asarray(Image.open(VANILLA + f + '.dds').convert('RGBA')) for f in ('urartuism', 'achamanism_reformed')]
    tiles = out + van
    sheet = Image.new('RGBA', (110 * len(tiles) + 320 * len(out), 330), (52, 48, 46, 255))
    x = 5
    for t in tiles:
        sheet.alpha_composite(Image.fromarray(t, 'RGBA'), (x, 115))
        x += 110
    for t in out:
        sheet.alpha_composite(Image.fromarray(t, 'RGBA').resize((300, 300), Image.LANCZOS), (x, 15))
        x += 320
    sheet.save(preview)
print(name, 'written', '(+ reformed)' if reformed else '')
