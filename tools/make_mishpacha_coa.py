# Generates the Mishpacha government's realm CoA textures:
#   gfx/interface/icons/realm_frames/mishpacha_government_{28,44,62,86,115}_{frame,shadow}.dds and _mask.dds:
#     a banner with a Torah-mantle hem, from a Gemini silhouette (mishpacha_banner_silhouette.png, black on white)
# The kippah and Keter above it come from make_mishpacha_crown.py; --crown draws an old procedural placeholder instead.
# Everything is drawn at 8x in 128-unit coordinates and downsampled. Vanilla's are uncompressed BGRA without mips.
# usage: python make_mishpacha_coa.py [silhouette.png] [--crown]
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
G = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
SS = 8                      # supersampling: 128 units -> 1024 px
SIZES = {28: 32, 44: 52, 62: 64, 86: 96, 115: 128}
CROWN = {28: (32, 22), 44: (52, 32), 62: (64, 40), 86: (96, 60), 115: (128, 80)}


def write_dds(path, rgba, header_from):
    rgba = np.clip(rgba, 0, 255).astype(np.uint8)
    hdr = open(header_from, 'rb').read(128)
    h, w = rgba.shape[:2]
    assert int.from_bytes(hdr[12:16], 'little') == h and int.from_bytes(hdr[16:20], 'little') == w, path
    bgra = rgba[..., [2, 1, 0, 3]]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(hdr + bgra.tobytes())


def downsample(rgba, w, h):
    """Premultiplied-alpha resize of a float RGBA array"""
    a = rgba[..., 3:4] / 255.0
    pm = np.concatenate([rgba[..., :3] * a, rgba[..., 3:4]], -1)
    chans = [np.array(Image.fromarray(pm[..., c].astype(np.float32), 'F').resize((w, h), Image.BOX)) for c in range(4)]
    out = np.stack(chans, -1)
    al = np.clip(out[..., 3:4], 0, 255)
    rgb = np.where(al > 0.5, out[..., :3] / np.maximum(al / 255.0, 1e-6), 0)
    return np.concatenate([np.clip(rgb, 0, 255), al], -1)


def over(dst, src):
    """Alpha-composite float RGBA src over dst"""
    sa = src[..., 3:4] / 255.0
    da = dst[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    return np.concatenate([rgb, oa * 255], -1)


def make_shield(silhouette):
    """The banner from a Gemini silhouette (black on white): stretched to vanilla's banner box (x 12..116, y 0..123 of 128),
    with vanilla's top-to-bottom shading, cloth texture and shadow"""
    N = 128 * SS
    L, R, TOP, BOT = 12.0, 116.0, 0.0, 123.0
    dark = 255.0 - np.array(Image.open(silhouette).convert('L')).astype(float)
    ys, xs = np.nonzero(dark > 128)
    dark = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    w, h = round((R - L) * SS), round((BOT - TOP) * SS)
    big = np.array(Image.fromarray(dark.astype(np.float32), 'F').resize((w, h), Image.BICUBIC))
    big = ndimage.gaussian_filter(big, 0.6 * SS)
    shape = np.zeros((N, N), bool)
    shape[round(TOP * SS):round(TOP * SS) + h, round(L * SS):round(L * SS) + w] = big > 127
    d_out = ndimage.distance_transform_edt(~shape) / SS

    dflt = {}
    for gv in ('frame', 'shadow'):
        for s, px in SIZES.items():
            dflt[(gv, s)] = np.array(Image.open(G + f'icons/realm_frames/_default_{s}_{gv}.dds').convert('RGBA')).astype(float)

    for s, px in SIZES.items():
        cov = downsample(np.dstack([np.zeros((N, N, 3)), shape * 255.0]), px, px)[..., 3]
        # overlay: vanilla's top-to-bottom gradient at alpha 38 inside the shape
        grad = dflt[('frame', s)][:, px // 2, :3]
        frame = np.zeros((px, px, 4))
        frame[..., :3] = grad[:, None, :]
        frame[..., 3] = cov / 255.0 * 38
        write_dds(MOD + f'gfx/interface/icons/realm_frames/mishpacha_government_{s}_frame.dds', frame, G + f'icons/realm_frames/_default_{s}_frame.dds')
        # shadow: the shape grown a little and softened, as vanilla's
        grow = {32: 1.2, 52: 1.5, 64: 1.7, 96: 2.0, 128: 2.3}[px] * 128 / px
        sh = ndimage.gaussian_filter((d_out < grow).astype(float), 0.6 * SS * 128 / px)
        shadow = downsample(np.dstack([np.zeros((N, N, 3)), sh * 255]), px, px)
        write_dds(MOD + f'gfx/interface/icons/realm_frames/mishpacha_government_{s}_shadow.dds', shadow, G + f'icons/realm_frames/_default_{s}_shadow.dds')

    # mask: vanilla's cloth texture under our shape (filled outward where vanilla's own shape ends)
    dm = np.array(Image.open(G + 'icons/realm_frames/_default_mask.dds').convert('RGBA')).astype(float)
    solid = dm[..., 3] > 200
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    cloth = dm[idx[0], idx[1], :3]
    mask = np.zeros((128, 128, 4))
    mask[..., :3] = cloth
    mask[..., 3] = downsample(np.dstack([np.zeros((N, N, 3)), shape * 255.0]), 128, 128)[..., 3]
    write_dds(MOD + 'gfx/interface/icons/realm_frames/mishpacha_government_mask.dds', mask, G + 'icons/realm_frames/_default_mask.dds')


# Placeholder crown, drawn here; make_mishpacha_crown.py replaces it with the Gemini-painted one
def make_placeholder_crown():
    # ---------------------------------------------------------------- crown
    CW, CH = 128 * SS, 80 * SS
    cy, cx = (np.mgrid[0:CH, 0:CW] + 0.5) / SS
    LIGHT = np.array([-0.45, -0.75, 0.55]); LIGHT /= np.linalg.norm(LIGHT)
    HALFV = LIGHT + np.array([0, 0, 1.0]); HALFV /= np.linalg.norm(HALFV)

    GOLD = [(70, 42, 12), (150, 104, 38), (214, 168, 78), (246, 218, 140), (255, 248, 214)]
    SILVER = [(52, 58, 68), (120, 128, 140), (182, 188, 198), (226, 230, 236), (255, 255, 255)]
    RUBY = [(50, 4, 8), (120, 14, 22), (190, 36, 44), (236, 96, 96), (255, 210, 210)]
    SAPPHIRE = [(6, 14, 50), (20, 44, 120), (52, 96, 190), (120, 170, 236), (230, 240, 255)]


    def ramp(t, stops):
        t = np.clip(t, 0, 1) * (len(stops) - 1)
        i = np.minimum(np.floor(t).astype(int), len(stops) - 2)
        f = (t - i)[..., None]
        st = np.array(stops, float)
        return st[i] * (1 - f) + st[i + 1] * f


    def shade(mask, stops, bevel=1.6, cyl=None, shine=40, gem=False):
        """Bevelled metal/gem part: a height field from the distance to the part's edge, lit from the upper left"""
        d = ndimage.distance_transform_edt(mask) / SS
        h = np.clip(d / bevel, 0, 1)
        h = np.sin(h * np.pi / 2) if not gem else np.sqrt(np.clip(1 - (1 - np.clip(d / bevel, 0, 1)) ** 2, 0, 1))
        gy, gx = np.gradient(h * bevel * SS * 0.6)
        nx, ny = -gx / SS * 4, -gy / SS * 4
        if cyl is not None:
            nx = nx + cyl
        n = np.dstack([nx, ny, np.ones_like(nx)])
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        diff = np.clip(n @ LIGHT, 0, 1)
        spec = np.clip(n @ HALFV, 0, 1) ** shine
        t = 0.18 + 0.62 * diff + 0.35 * spec
        rgb = ramp(t, stops)
        a = mask.astype(float) * 255
        return np.dstack([rgb, a])


    def band_edges(x):
        u = np.clip((x - 64) / 34.0, -1, 1)
        return 54.0 + 1.5 * u ** 2, 74.5 - 2.5 * u ** 2 + 0.0, u


    def leaf(x0, base, height, width, tilt=0.0):
        """A pointed palmette rising from the band; returns its mask and the tip position"""
        t = (base - cy) / height                       # 0 at the base, 1 at the tip
        xs = x0 + tilt * (base - cy)
        w = width * (0.42 * (1 - t) + 0.75 * np.sin(np.pi * np.clip(t, 0, 1) ** 0.8)) * (1 - np.clip(t, 0, 1) ** 3)
        m = (t >= -0.05) & (t <= 1) & (np.abs(cx - xs) <= w)
        return m, (x0 + tilt * height, base - height)


    def disc(x0, y0, r):
        return (cx - x0) ** 2 + (cy - y0) ** 2 <= r * r


    def ellipse(x0, y0, rx, ry):
        return ((cx - x0) / rx) ** 2 + ((cy - y0) / ry) ** 2 <= 1


    def star(x0, y0, r, width):
        """Magen David: two triangles as thick outlines"""
        m = np.zeros_like(cx, bool)
        for rot in (0, np.pi):
            pts = [(x0 + r * np.sin(rot + k * 2 * np.pi / 3), y0 - r * np.cos(rot + k * 2 * np.pi / 3)) for k in range(3)]
            for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
                vx, vy = bx - ax, by - ay
                tt = np.clip(((cx - ax) * vx + (cy - ay) * vy) / (vx * vx + vy * vy), 0, 1)
                m |= (cx - ax - tt * vx) ** 2 + (cy - ay - tt * vy) ** 2 <= (width / 2) ** 2
        return m


    top_e, bot_e, u = band_edges(cx)
    band = (np.abs(cx - 64) <= 34) & (cy >= top_e) & (cy <= bot_e)

    layers = []
    # palmettes: silver, topped with gold pomegranates, the middle one with a Magen David
    specs = [(-33, 15, 7.0, -0.16), (33, 15, 7.0, 0.16), (-17.5, 21, 8.0, -0.05), (17.5, 21, 8.0, 0.05), (0, 25, 8.5, 0.0)]
    tips = []
    for dx, hgt, wid, tilt in specs:
        base = band_edges(np.array(64.0 + dx))[0] + 1.0
        m, tip = leaf(64 + dx, base, hgt, wid, tilt)
        layers.append(shade(m, SILVER, bevel=1.8))
        tips.append((dx, tip))
    for dx, (tx, ty) in tips:
        if dx == 0:
            layers.append(shade(star(tx, ty - 5.2, 6.2, 2.0), GOLD, bevel=0.9))
        else:
            layers.append(shade(disc(tx, ty - 2.2, 3.0), GOLD, bevel=3.0, gem=True, shine=30))
    # the band: gold, rounded like a cylinder
    layers.append(shade(band, GOLD, bevel=1.4, cyl=u * 0.9))
    # beading along its edges
    for edge, off in ((top_e, 1.8), (bot_e, -1.8)):
        for x in np.arange(32.5, 96.1, 4.0):
            e = band_edges(np.array(x))
            y = (e[0] if edge is top_e else e[1]) + off
            layers.append(shade(disc(x, y, 1.25), SILVER, bevel=1.25, gem=True, shine=25))
    # gems: a ruby in the middle, sapphires and rubies outward, narrower toward the sides
    for x, stones, rx in ((64, RUBY, 4.2), (47, SAPPHIRE, 2.8), (81, SAPPHIRE, 2.8), (34.5, RUBY, 1.4), (93.5, RUBY, 1.4)):
        e = band_edges(np.array(float(x)))
        ymid = (e[0] + e[1]) / 2
        setting = ellipse(x, ymid, rx + 1.1, 4.1)
        layers.append(shade(setting, SILVER, bevel=0.8))
        layers.append(shade(ellipse(x, ymid, rx, 3.0), stones, bevel=2.6, gem=True, shine=60))

    crown = np.zeros((CH, CW, 4))
    for ly in layers:
        crown = over(crown, ly)
    # dark outline and a soft drop shadow, as vanilla's crowns have
    solid = crown[..., 3] > 128
    outline = ndimage.binary_dilation(solid, iterations=int(0.9 * SS)) & ~solid
    ol = np.zeros_like(crown); ol[..., :3] = (38, 24, 10); ol[..., 3] = outline * 230
    drop = ndimage.gaussian_filter(np.roll(np.roll(solid.astype(float), int(1.0 * SS), 0), int(0.6 * SS), 1), 1.4 * SS)
    dr = np.zeros_like(crown); dr[..., 3] = drop * 150
    crown = over(over(dr, ol), crown)

    for s, (w, h) in CROWN.items():
        # vanilla's 28 strip is 22 high for 32 wide, not 20: draw at the 128x80 ratio and pad the top
        hh = round(w * 80 / 128)
        img = downsample(crown, w, hh)
        if hh < h:
            img = np.concatenate([np.zeros((h - hh, w, 4)), img], 0)
        write_dds(MOD + f'gfx/interface/coat_of_arms/jip_mishpacha_topframe_{s}.dds', img, G + f'coat_of_arms/landless_adventurer_topframe_{s}.dds')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    make_shield(args[0] if args else OUT + 'mishpacha_banner_silhouette.png')
    if '--crown' in sys.argv:
        make_placeholder_crown()
    print('ok')
