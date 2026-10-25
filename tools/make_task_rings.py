# Rebuilds clean empty rings from vanilla court position task icons: the ring is unwrapped into polar coordinates,
# the angles the object covers are refilled from the neighbouring visible ring, and everything inside is cleared.
# usage: python make_task_rings.py <out_dir>
import sys
import numpy as np
from PIL import Image

V = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/court_position_task_types/'
SOURCES = {
    'gray': 'high_almoner_attend_poor',
    'green': 'seneschal_handling_estate',
    'blue': 'court_musician_court_position_task_bolster_legitimacy',
    'gold': 'chronicler_generate_seeds',
}
SIZE = 140
C = (SIZE - 1) / 2
NT, NR = 720, 140  # angle bins, radius bins (0.5 px each)


def bilinear(img, x, y):
    h, w = img.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def premul(a):
    a = a.astype(np.float32)
    a[..., :3] *= a[..., 3:4] / 255
    return a


def unpremul(a):
    out = a.copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        out[..., :3] = np.where(a[..., 3:4] > 0, a[..., :3] * 255 / a[..., 3:4], 0)
    return np.clip(out, 0, 255).astype(np.uint8)


def clean_ring(name, reddish_check=False):
    img = premul(np.array(Image.open(V + name + '.dds').convert('RGBA')))
    th = np.linspace(0, 2 * np.pi, NT, endpoint=False)
    rr = np.arange(NR) * 0.5
    T, R = np.meshgrid(th, rr, indexing='ij')
    polar = bilinear(img, C + R * np.cos(T), C + R * np.sin(T))  # [angle, radius, rgba]

    alpha = polar[..., 3]
    # The same in every vanilla task icon: the ring runs from 49 to 62 px with a soft shadow outside it, and a transparent
    # gap around 45 px separates it from the object
    r1, r2 = 98, 124
    # Per-angle ring colour, including its inner edge; angles where the object sits on the ring or reaches past its
    # outer shadow are covered
    def band_dist(a, b):
        band = polar[:, a:b, :3]
        profile = np.median(band, axis=0)  # the typical ring colour at each radius
        return np.linalg.norm(band - profile, axis=2).mean(axis=1)
    outer = alpha[:, 134]
    covered = (band_dist(r1 - 6, r2 + 1) > 22) | (outer > np.median(outer) + 40)
    if reddish_check:
        # Green stone never has red in it, so any reddish pixel on the ring is a sliver of the object (the castle roofs)
        band = polar[:, r1 - 6:r2 + 1, :3]
        covered |= ((band[..., 0] - band[..., 1] > 20) & (band[..., 0] - band[..., 2] > 20)).any(axis=1)
    # Widen the covered runs so object edges don't survive
    covered = np.convolve(covered.astype(int), np.ones(21, int), 'same') > 0

    fixed = polar.copy()
    # Refill each covered angle from the clear angles, cycling through them in order so the stone texture keeps varying
    # (only the template's few covered angles need this to look good)
    clear = np.nonzero(~covered)[0]
    if len(clear):
        for k, a in enumerate(np.nonzero(covered)[0]):
            fixed[a] = polar[clear[(a + k) % len(clear)]]
    # Clear the inside of the ring (keep the inner shadow just inside the band)
    fixed[:, :r1 - 6] = 0

    # Back to a square image
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    dx, dy = xs - C, ys - C
    rad = np.hypot(dx, dy) / 0.5
    ang = (np.arctan2(dy, dx) % (2 * np.pi)) / (2 * np.pi) * NT
    # Sample with wrap-around on the angle axis
    padded = np.concatenate([fixed, fixed[:1]], axis=0)
    out = bilinear(padded.transpose(1, 0, 2), ang, np.clip(rad, 0, NR - 1.001))
    out[rad > NR - 1] = 0
    # The ring's colour, from the angles the object leaves uncovered (ring pixels are opaque, so no unpremultiply)
    # The ring's colour, from the quarter of the angles that look most like plain ring (ring pixels are opaque, so no
    # unpremultiply). Large objects can mark every angle as covered, so this doesn't rely on the covered mask.
    d = band_dist(r1, r2 + 1)
    plain = d <= np.percentile(d, 25)
    ring_col = np.median(polar[plain, r1:r2 + 1, :3].reshape(-1, 3), axis=0)
    return Image.fromarray(unpremul(out), 'RGBA'), ring_col, covered.mean()


# The castle of seneschal_handling_estate covers the least of its ring, so the green ring is the template. The other
# colours are the template recoloured to the median ring colour of their own vanilla icon.
TEMPLATE = 'green'

if __name__ == '__main__':
    out_dir = sys.argv[1]
    template, t_col, cov = clean_ring(SOURCES[TEMPLATE], reddish_check=True)
    print('template covered', round(cov, 2))
    t = np.array(template).astype(np.float32)
    sheet = Image.new('RGBA', (SIZE * 4 + 50, SIZE * 2 + 30), (60, 50, 40, 255))
    for i, (color, name) in enumerate(SOURCES.items()):
        _, col, _ = clean_ring(name)
        ring = t.copy()
        ring[..., :3] *= (col / t_col)
        ring = Image.fromarray(np.clip(ring, 0, 255).astype(np.uint8), 'RGBA')
        ring.save(f'{out_dir}/task_ring_{color}.png')
        sheet.alpha_composite(Image.open(V + name + '.dds').convert('RGBA'), (10 + i * (SIZE + 10), 10))
        sheet.alpha_composite(ring, (10 + i * (SIZE + 10), SIZE + 20))
        print(color, 'ring colour', np.round(col))
    sheet.save(f'{out_dir}/task_rings_preview.png')
