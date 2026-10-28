# Builds a great project's art from Gemini images, in vanilla's formats:
# - icon: gfx/interface/icons/great_projects/<name>.dds, 120x120 with mips, like mandala_capital.dds: a painted
#   miniature of the building on a flat background (read from the corners, usually #00FF00), keyed out by its distance
#   to that colour so green parts of the model (palms) stay, with the green fringe pulled back
# - illustration: gfx/interface/illustrations/great_projects/<name>.dds, 1100x440 like pam_grand_project_cathedral.dds,
#   cropped from a wide painting around a vertical centre (0-1, default 0.5)
# Usage: make_great_project_art.py <name> [--icon <image>] [--illustration <image> [--y <0-1>]] [--preview <png>]
# The project points at them in its icon and illustration blocks (common/great_projects/types/jip_great_projects.txt).
import struct
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
VANILLA = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/'
ICON, FIT = 120, 116
ILL_W, ILL_H = 1100, 440

args = sys.argv[1:]
name = args[0]
opt = {k: args[args.index(k) + 1] for k in ('--icon', '--illustration', '--y', '--preview') if k in args}


def dds(levels, w, h):
    """Uncompressed A8R8G8B8 DDS; levels are RGBA arrays, largest first."""
    flags = 0x100F | (0x20000 if len(levels) > 1 else 0)
    caps = 0x1000 | (0x400008 if len(levels) > 1 else 0)
    header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, flags, h, w, w * 4, 0, len(levels), b'\0' * 44,
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, caps, 0, 0, 0, 0)
    return header + b''.join(lv[..., [2, 1, 0, 3]].tobytes() for lv in levels)


def premul_resize(rgba, size):
    arr = rgba.astype(np.float32) / 255
    pm = np.dstack([arr[..., :3] * arr[..., 3:4], arr[..., 3:4]])
    p = np.asarray(Image.fromarray((pm * 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)).astype(np.float32) / 255
    al = p[..., 3:4]
    rgb = np.where(al > 0, p[..., :3] / np.maximum(al, 1e-6), 0)
    return (np.dstack([rgb, al]).clip(0, 1) * 255).astype(np.uint8)


out = []
if '--icon' in opt:
    im = np.asarray(Image.open(opt['--icon']).convert('RGB')).astype(np.float32)
    corners = np.concatenate([im[:24, :24].reshape(-1, 3), im[-24:, -24:].reshape(-1, 3)])
    bg = np.median(corners, 0)
    alpha = np.clip((np.abs(im - bg).max(2) - 30) / 50, 0, 1)
    solid = alpha > 0.5
    lab, n = ndimage.label(solid)
    if n > 1:                                  # keep the model, drop specks
        sizes = ndimage.sum(solid, lab, range(1, n + 1))
        alpha *= ndimage.binary_dilation(np.isin(lab, 1 + np.where(sizes >= 0.01 * sizes.max())[0]), iterations=2)
    # Pull the background's green out of the edge, a few pixels deep (it bleeds into the model's rim), and thin the
    # alpha a pixel so the last tinted ring goes
    edge = ndimage.binary_dilation(alpha < 0.9, iterations=4)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    im[..., 1] = np.where(edge, np.minimum(g, np.maximum(r, b)), g)
    alpha = np.minimum(alpha, ndimage.grey_erosion(alpha, size=3))
    rgba = np.dstack([im, alpha * 255]).clip(0, 255).astype(np.uint8)
    ys, xs = np.where(alpha > 0.05)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = rgba.shape[:2]
    sc = FIT / max(h, w)
    small = premul_resize(rgba, (max(1, round(w * sc)), max(1, round(h * sc))))
    icon = np.zeros((ICON, ICON, 4), np.uint8)
    y0, x0 = (ICON - small.shape[0]) // 2, (ICON - small.shape[1]) // 2
    icon[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small
    levels, s = [icon], ICON
    while s > 1:
        s = max(1, s // 2)
        levels.append(premul_resize(icon, (s, s)))
    open(MOD + f'gfx/interface/icons/great_projects/{name}.dds', 'wb').write(dds(levels, ICON, ICON))
    out.append(Image.fromarray(icon, 'RGBA'))

if '--illustration' in opt:
    im = Image.open(opt['--illustration']).convert('RGB')
    w, h = im.size
    if w / h < ILL_W / ILL_H:                  # too tall: crop a band around the chosen centre
        ch = round(w * ILL_H / ILL_W)
        cy = float(opt.get('--y', 0.5)) * h
        y0 = int(min(max(cy - ch / 2, 0), h - ch))
        im = im.crop((0, y0, w, y0 + ch))
    else:
        cw = round(h * ILL_W / ILL_H)
        x0 = (w - cw) // 2
        im = im.crop((x0, 0, x0 + cw, h))
    ill = np.dstack([np.asarray(im.resize((ILL_W, ILL_H), Image.LANCZOS)), np.full((ILL_H, ILL_W), 255, np.uint8)])
    open(MOD + f'gfx/interface/illustrations/great_projects/{name}.dds', 'wb').write(dds([ill], ILL_W, ILL_H))
    out.append(Image.fromarray(ill, 'RGBA'))

if '--preview' in opt:
    # Ours next to vanilla's cathedral, on the window's dark brown
    van = Image.open(VANILLA + 'icons/great_projects/grand_cathedral_gp.dds').convert('RGBA').resize((ICON, ICON))
    tiles = [t.resize((t.width // 2, t.height // 2), Image.LANCZOS) if t.width > ICON else t for t in out] + [van]
    sheet = Image.new('RGBA', (sum(t.width + 10 for t in tiles) + 10, max(t.height for t in tiles) + 20), (60, 50, 40, 255))
    x = 10
    for t in tiles:
        sheet.alpha_composite(t, (x, 10))
        x += t.width + 10
    sheet.save(opt['--preview'])
print(name, 'written:', ', '.join(k[2:] for k in ('--icon', '--illustration') if k in opt))
