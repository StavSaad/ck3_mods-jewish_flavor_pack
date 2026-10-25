# Builds the mod's event "content source" banner (526x128, shown at 263x64 in the event window's top right like a DLC's):
# a Gemini painting in place of the art of vanilla's dlc_009 decoration, keeping vanilla's alpha (the fade to the left),
# its stone ledge (rows 103-112), dark right edge (cols 505-510) and drop shadow.
# Usage: python make_dlc_banner.py <painting> <y0> [preview.png]
#   y0: top row (in the painting's pixels) of the strip used; the strip spans the painting's full width
import os
import sys
import numpy as np
from PIL import Image

DEC = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/illustrations/dlc_event_decorations/'
HEADER_FROM = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gfx/interface/icons/dlc/dlc_003.dds'
OUT = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/gfx/interface/illustrations/jip_event_source_banner.dds'
W, H = 526, 128
ART_W, ART_H = 505, 103


def dds_header(w, h):
    """vanilla's uncompressed BGRA header (from a DLC icon) with the size patched"""
    hdr = bytearray(open(HEADER_FROM, 'rb').read(128))
    hdr[12:16] = h.to_bytes(4, 'little')
    hdr[16:20] = w.to_bytes(4, 'little')
    hdr[20:24] = (w * 4).to_bytes(4, 'little')
    return bytes(hdr)


def main():
    src, y0 = sys.argv[1], int(sys.argv[2])
    preview = sys.argv[3] if len(sys.argv) > 3 else None
    vanilla = np.asarray(Image.open(DEC + 'dlc_009.dds').convert('RGBA')).astype(np.float64)
    im = Image.open(src).convert('RGB')
    strip_h = round(im.width * ART_H / ART_W)
    art = np.asarray(im.crop((0, y0, im.width, y0 + strip_h)).resize((ART_W, ART_H), Image.LANCZOS)).astype(np.float64)
    out = vanilla.copy()
    out[:ART_H, :ART_W, :3] = art
    # blend the last row and column into vanilla's ledge and edge
    out[ART_H - 1, :ART_W, :3] = (art[-1] + vanilla[ART_H, :ART_W, :3]) / 2
    out[:ART_H, ART_W - 1, :3] = (art[:, -1] + vanilla[:ART_H, ART_W, :3]) / 2
    out = out.clip(0, 255).astype(np.uint8)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'wb').write(dds_header(W, H) + out[..., [2, 1, 0, 3]].tobytes())
    print('wrote', OUT)
    if preview:
        # ours above vanilla's, on event-window parchment, at full size and at the in-game 263x64
        bg = (200, 190, 170, 255)
        sheet = Image.new('RGBA', (W + 20, 2 * H + 64 + 40), bg)
        sheet.alpha_composite(Image.fromarray(out, 'RGBA'), (10, 10))
        sheet.alpha_composite(Image.fromarray(vanilla.astype(np.uint8), 'RGBA'), (10, H + 20))
        sheet.alpha_composite(Image.fromarray(out, 'RGBA').resize((263, 64), Image.LANCZOS), (10, 2 * H + 30))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS).save(preview)
        print('preview', preview)


main()
