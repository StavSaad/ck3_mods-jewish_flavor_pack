# Builds the map model of the Ehulhul, the Temple of Sin at Harran, as a Neo-Babylonian moon-god ziggurat, in Blender.
# Run: blender --background --python tools/make_ziggurat_model.py -- [--preview <png>] [--no-bake]
# Needs the io_pdx_mesh add-on (github.com/ross-g/io_pdx_mesh; patched for Blender 5's removed material settings).
#
# The design (0.15 plan, section 2): no ziggurat at Harran is attested (Nabonidus's texts call the Ehulhul a temple),
# so the model follows the moon god's ziggurat he restored at Ur: a broad first stage (Ur's 64 x 45 m proportions) with
# a niche-and-buttress face of baked brick, three stairs meeting at a gatehouse on the first terrace, a single stair on to
# two smaller stages, and the god's shrine on top in blue glazed brick (as found at Ur), with stepped merlons and the
# crescent of Sin on a pole.
#
# Texturing follows vanilla's special buildings (e.g. the Great Mosque of Samarra): every face maps onto a tile of the
# shared Persian atlas (building_persia_atlas_*), about 1.5 map units to a 128 px tile, with the standard_atlas shader;
# a second UV set (map2) carries the building's own baked ambient occlusion, the "unique" map (texture index 5).
# Outputs gfx/models/buildings/jip/jip_temple_of_sin.mesh, .asset and jip_temple_of_sin_unique.dds.
import importlib
import math
import os
import struct
import sys
from types import SimpleNamespace

import addon_utils
import bmesh
import bpy
import numpy as np
from mathutils import Vector

MOD = 'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
VAN = 'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/'
ATLAS_DIR = VAN + 'gfx/models/buildings/holdings/atlas/persian'
OUT_DIR = MOD + 'gfx/models/buildings/jip/'
NAME = 'jip_temple_of_sin'

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PREVIEW = argv[argv.index('--preview') + 1] if '--preview' in argv else None
BAKE = '--no-bake' not in argv

DENS = 12.0  # map units per atlas UV unit (vanilla's median): a 128 px tile spans 1.5 units
SCALE = 0.9  # the model is built in round numbers, then shrunk to the Tomb of Cyrus's footprint (about 6.3 x 7.5)
TILE_LEN = DENS / 8


def px(x0, y0, x1, y1):
    """A pixel rectangle of the 1024 px atlas as UV (u0, v0, u1, v1); Blender's v runs up."""
    return (x0 / 1024, 1 - y1 / 1024, x1 / 1024, 1 - y0 / 1024)


def tile(c, r, inset=2):
    return px(c * 128 + inset, r * 128 + inset, (c + 1) * 128 - inset, (r + 1) * 128 - inset)


# Atlas regions (building_persia_atlas_diffuse.dds)
T_BRICK = tile(3, 0)          # weathered baked brick
T_BRICK_PALE = tile(2, 0)     # paler baked brick
T_BRICK_DARK = tile(7, 7)     # dark baked brick, the platform
T_PAVING = tile(0, 0)         # plain mud plaster, the courtyard
T_TERRACE = tile(2, 6)        # worn brick paving, the terraces
T_STAIRS = tile(2, 3)         # steps
T_GLAZED = tile(5, 2)         # blue glazed brick with gold rosettes
T_NICHES = px(0, 692, 1024, 766)   # strip: brick panels between dark recesses (niche and buttress)
T_FRIEZE = px(0, 642, 1024, 690)   # strip: turquoise and gold frieze
T_DOOR = px(905, 388, 941, 444)    # an arched opening
T_GOLD = px(702, 317, 708, 323)    # a rosette's gold

STRIPS = (T_NICHES, T_FRIEZE)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv0 = self.bm.loops.layers.uv.new('map1')
        self.uv1 = self.bm.loops.layers.uv.new('map2')

    def face(self, pts, uvs):
        verts = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(verts)
        for loop, uv in zip(f.loops, uvs):
            loop[self.uv0].uv = uv
        f.smooth = False
        return f

    def quad(self, bl, br, tr, tl, region, mode='tile'):
        """A quad seen from outside as bl, br, tr, tl. 'tile' repeats the region every TILE_LEN (split into cells),
        'strip' runs a full-width atlas strip along the face (u by density, v over the whole height), 'fit' maps the
        region over the whole face."""
        bl, br, tr, tl = map(Vector, (bl, br, tr, tl))
        u0, v0, u1, v1 = region
        width = max((br - bl).length, (tr - tl).length)
        height = max((tl - bl).length, (tr - br).length)

        def at(s, t):
            return bl.lerp(br, s).lerp(tl.lerp(tr, s), t)

        if mode == 'fit':
            self.face([bl, br, tr, tl], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
            return
        if mode == 'strip':
            span = (u1 - u0) * DENS          # map units the strip covers before it must wrap
            nu = max(1, math.ceil(width / span - 1e-6))
            for i in range(nu):
                s0, s1 = i / nu, (i + 1) / nu
                du = (s1 - s0) * width / DENS
                self.face([at(s0, 0), at(s1, 0), at(s1, 1), at(s0, 1)],
                          [(u0, v0), (u0 + du, v0), (u0 + du, v1), (u0, v1)])
            return
        nu = max(1, math.ceil(width / TILE_LEN - 1e-6))
        nv = max(1, math.ceil(height / TILE_LEN - 1e-6))
        for i in range(nu):
            for j in range(nv):
                s0, s1, t0, t1 = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv
                fu = (s1 - s0) * width / TILE_LEN
                fv = (t1 - t0) * height / TILE_LEN
                uu, vv = u0 + (u1 - u0) * fu, v0 + (v1 - v0) * fv
                self.face([at(s0, t0), at(s1, t0), at(s1, t1), at(s0, t1)],
                          [(u0, v0), (uu, v0), (uu, vv), (u0, vv)])

    def tri(self, a, b, c, region):
        """A triangle seen from outside as a, b, c, mapped flat onto the region (shrunk to fit one tile)."""
        a, b, c = map(Vector, (a, b, c))
        n = (b - a).cross(c - a).normalized()
        ax = (b - a).normalized()
        ay = n.cross(ax)
        pts2 = [((p - a).dot(ax), (p - a).dot(ay)) for p in (a, b, c)]
        xs, ys = [p[0] for p in pts2], [p[1] for p in pts2]
        ext = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
        k = min(1.0, TILE_LEN / ext) / TILE_LEN
        u0, v0, u1, v1 = region
        uvs = [(u0 + (x - min(xs)) * k * (u1 - u0), v0 + (y - min(ys)) * k * (v1 - v0)) for x, y in pts2]
        self.face([a, b, c], uvs)

    def box(self, x0, x1, y0, y1, z0, z1, side, top, batter=0.0, side_mode='tile', sides='fbrl', top_mode='tile'):
        i = batter
        if 'f' in sides:
            self.quad((x0, y0, z0), (x1, y0, z0), (x1 - i, y0 + i, z1), (x0 + i, y0 + i, z1), side, side_mode)
        if 'r' in sides:
            self.quad((x1, y0, z0), (x1, y1, z0), (x1 - i, y1 - i, z1), (x1 - i, y0 + i, z1), side, side_mode)
        if 'b' in sides:
            self.quad((x1, y1, z0), (x0, y1, z0), (x0 + i, y1 - i, z1), (x1 - i, y1 - i, z1), side, side_mode)
        if 'l' in sides:
            self.quad((x0, y1, z0), (x0, y0, z0), (x0 + i, y0 + i, z1), (x0 + i, y1 - i, z1), side, side_mode)
        if top:
            self.quad((x0 + i, y0 + i, z1), (x1 - i, y0 + i, z1), (x1 - i, y1 - i, z1), (x0 + i, y1 - i, z1), top,
                      top_mode)

    def stair(self, x0, x1, y_foot, y_top, z_foot, z_top):
        """A straight stair rising towards +y, with its two side walls."""
        self.quad((x0, y_foot, z_foot), (x1, y_foot, z_foot), (x1, y_top, z_top), (x0, y_top, z_top), T_STAIRS)
        self.tri((x0, y_foot, z_foot), (x0, y_top, z_top), (x0, y_top, z_foot), T_BRICK)
        self.tri((x1, y_foot, z_foot), (x1, y_top, z_foot), (x1, y_top, z_top), T_BRICK)

    def merlons(self, x0, x1, y0, y1, z, size=0.12, height=0.14, step=0.24):
        """Stepped merlons along a roof's edge."""
        def row(a, b, fixed, along_x):
            n = max(2, int((b - a) / step))
            for k in range(n + 1):
                c = a + (b - a) * k / n
                if along_x:
                    self.box(c - size / 2, c + size / 2, fixed - size / 2, fixed + size / 2, z, z + height,
                             T_BRICK_PALE, T_BRICK_PALE)
                else:
                    self.box(fixed - size / 2, fixed + size / 2, c - size / 2, c + size / 2, z, z + height,
                             T_BRICK_PALE, T_BRICK_PALE)
        h = size / 2
        row(x0 + h, x1 - h, y0 + h, True)
        row(x0 + h, x1 - h, y1 - h, True)
        row(y0 + h + step, y1 - h - step, x0 + h, False)
        row(y0 + h + step, y1 - h - step, x1 - h, False)


def build():
    b = Builder()
    # The temple court: a low platform of dark brick, paved
    b.box(-4.0, 4.0, -4.6, 2.6, 0.0, 0.12, T_BRICK_DARK, T_PAVING)
    z1 = 0.12
    # Stage 1: 6.0 x 4.3 (Ur's proportions), battered, the niche-and-buttress face
    s1 = dict(x0=-3.0, x1=3.0, y0=-2.15, y1=2.15)
    b.box(s1['x0'], s1['x1'], s1['y0'], s1['y1'], z1, z1 + 1.3, T_NICHES, T_TERRACE, batter=0.12, side_mode='strip')
    z2 = z1 + 1.3
    # The three stairs of the first stage: a central flight out from the face, two along it, meeting at the gatehouse
    b.stair(-0.35, 0.35, -4.0, s1['y0'] + 0.12, z1, z2)
    yf, yb = s1['y0'] - 0.62, s1['y0'] - 0.02
    # Left flight rises towards +x, along the face
    b.quad((-3.0, yb, z1), (-3.0, yf, z1), (-0.45, yf, z2), (-0.45, yb, z2), T_STAIRS)
    b.tri((-3.0, yf, z1), (-0.45, yf, z1), (-0.45, yf, z2), T_BRICK)
    # Right flight rises towards -x
    b.quad((3.0, yf, z1), (3.0, yb, z1), (0.45, yb, z2), (0.45, yf, z2), T_STAIRS)
    b.tri((0.45, yf, z1), (3.0, yf, z1), (0.45, yf, z2), T_BRICK)
    # Their landings' fronts, under the gatehouse
    b.quad((-0.45, yf, z1), (0.45, yf, z1), (0.45, yf, z2), (-0.45, yf, z2), T_BRICK)
    b.quad((-0.45, yf, z2), (0.45, yf, z2), (0.45, yb, z2), (-0.45, yb, z2), T_TERRACE)
    # The gatehouse on the first terrace, with its arch and merlons
    g = dict(x0=-0.55, x1=0.55, y0=-2.0, y1=-1.5)
    b.box(g['x0'], g['x1'], g['y0'], g['y1'], z2, z2 + 0.55, T_BRICK_PALE, T_TERRACE)
    b.quad((-0.17, g['y0'] - 0.01, z2), (0.17, g['y0'] - 0.01, z2), (0.17, g['y0'] - 0.01, z2 + 0.42),
           (-0.17, g['y0'] - 0.01, z2 + 0.42), T_DOOR, 'fit')
    b.merlons(g['x0'], g['x1'], g['y0'], g['y1'], z2 + 0.55, size=0.1, height=0.11, step=0.2)
    # Stage 2
    s2 = dict(x0=-2.1, x1=2.1, y0=-0.65, y1=2.05)
    b.box(s2['x0'], s2['x1'], s2['y0'], s2['y1'], z2, z2 + 0.95, T_NICHES, T_TERRACE, batter=0.08, side_mode='strip')
    z3 = z2 + 0.95
    b.stair(-0.3, 0.3, g['y1'], s2['y0'] + 0.08, z2, z3)
    # Stage 3
    s3 = dict(x0=-1.3, x1=1.3, y0=0.1, y1=1.9)
    b.box(s3['x0'], s3['x1'], s3['y0'], s3['y1'], z3, z3 + 0.75, T_BRICK, T_TERRACE, batter=0.06)
    z4 = z3 + 0.75
    b.stair(-0.25, 0.25, s2['y0'] + 0.08 + 0.05, s3['y0'] + 0.06, z3, z4)
    # The shrine of Sin: blue glazed brick, a turquoise and gold frieze, the door, stepped merlons
    sh = dict(x0=-0.7, x1=0.7, y0=0.65, y1=1.65)
    b.box(sh['x0'], sh['x1'], sh['y0'], sh['y1'], z4, z4 + 0.62, T_GLAZED, None)
    b.box(sh['x0'], sh['x1'], sh['y0'], sh['y1'], z4 + 0.62, z4 + 0.8, T_FRIEZE, T_TERRACE, side_mode='strip')
    zr = z4 + 0.8
    b.quad((-0.16, sh['y0'] - 0.01, z4), (0.16, sh['y0'] - 0.01, z4), (0.16, sh['y0'] - 0.01, z4 + 0.46),
           (-0.16, sh['y0'] - 0.01, z4 + 0.46), T_DOOR, 'fit')
    b.merlons(sh['x0'], sh['x1'], sh['y0'], sh['y1'], zr, size=0.11, height=0.13, step=0.22)
    # The crescent of Sin on its pole, horns up, over the shrine's front
    b.box(-0.025, 0.025, 1.0, 1.05, zr, zr + 0.5, T_GOLD, T_GOLD)
    crescent(b, cx=0.0, cy=1.025, cz=zr + 0.68, R=0.24, r=0.2, d=0.09, depth=0.05)
    return b


def crescent(b, cx, cy, cz, R, r, d, depth, n=16):
    """A crescent, horns up, facing -y: a disc of radius R less a disc of radius r raised by d."""
    yi = (R * R - r * r + d * d) / (2 * d)          # where the two circles meet
    xi = math.sqrt(max(R * R - yi * yi, 0))
    ao0, ao1 = math.atan2(yi, -xi), math.atan2(yi, xi) + 2 * math.pi       # outer arc, through the bottom
    ai0, ai1 = math.atan2(yi - d, -xi), math.atan2(yi - d, xi) + 2 * math.pi
    outer = [(cx + R * math.cos(a), cz + R * math.sin(a)) for a in np.linspace(ao0, ao1, n + 1)]
    inner = [(cx + r * math.cos(a), cz + d + r * math.sin(a)) for a in np.linspace(ai0, ai1, n + 1)]
    gold = [(T_GOLD[0], T_GOLD[1]), (T_GOLD[2], T_GOLD[1]), (T_GOLD[2], T_GOLD[3]), (T_GOLD[0], T_GOLD[3])]
    yf, yb = cy - depth / 2, cy + depth / 2
    for k in range(n):
        o0, o1, i0, i1 = outer[k], outer[k + 1], inner[k], inner[k + 1]
        # front (-y) and back faces
        b.face([(o0[0], yf, o0[1]), (o1[0], yf, o1[1]), (i1[0], yf, i1[1]), (i0[0], yf, i0[1])], gold)
        b.face([(o1[0], yb, o1[1]), (o0[0], yb, o0[1]), (i0[0], yb, i0[1]), (i1[0], yb, i1[1])], gold)
        # the outer and inner rims
        b.face([(o1[0], yf, o1[1]), (o0[0], yf, o0[1]), (o0[0], yb, o0[1]), (o1[0], yb, o1[1])], gold)
        b.face([(i0[0], yf, i0[1]), (i1[0], yf, i1[1]), (i1[0], yb, i1[1]), (i0[0], yb, i0[1])], gold)


def main():
    mods = [m.__name__ for m in addon_utils.modules() if 'pdx' in m.__name__.lower()]
    if not mods:
        raise SystemExit('io_pdx_mesh is not installed')
    for m in mods:
        addon_utils.enable(m, default_set=True)
    pdx = importlib.import_module(mods[0] + '.pdx_blender.blender_import_export')
    bpy.ops.wm.read_factory_settings(use_empty=True)

    b = build()
    bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(NAME + '_LOD0Shape')
    b.bm.to_mesh(me)
    b.bm.free()
    from mathutils import Matrix
    me.transform(Matrix.Scale(SCALE, 4))
    obj = bpy.data.objects.new(NAME + '_LOD0', me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    print('FACES', len(me.polygons), 'VERTS', len(me.vertices), 'DIMS', [round(d, 2) for d in obj.dimensions])

    # The material: vanilla's atlas through the add-on's own shader setup (the export reads its shader and textures)
    stub = SimpleNamespace(shader=['standard_atlas'], diff=['building_persia_atlas_diffuse.dds'],
                           spec=['building_persia_atlas_properties.dds'], n=['building_persia_atlas_normal.dds'])
    mat = pdx.create_shader(stub, 'PDXmat_' + NAME, ATLAS_DIR)
    me.materials.append(mat)

    # The unique map's UVs: every face once, in its own island
    me.uv_layers.active = me.uv_layers['map2']
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')

    os.makedirs(OUT_DIR, exist_ok=True)
    if BAKE:
        bake_unique(obj, me, mat)
    me.uv_layers.active = me.uv_layers['map1']
    me.uv_layers['map1'].active_render = True

    pdx.export_meshfile(OUT_DIR + NAME + '.mesh', exp_mesh=True, exp_skel=False, exp_locs=False)
    write_asset()
    if PREVIEW:
        render_preview(obj)


def bake_unique(obj, me, mat):
    """Ambient occlusion on map2, brightened like vanilla's (mean ~0.82), as an uncompressed 512 px DDS."""
    size = 512
    img = bpy.data.images.new(NAME + '_unique', size, size, alpha=False)
    nodes = mat.node_tree.nodes
    node = nodes.new('ShaderNodeTexImage')
    node.image = img
    nodes.active = node
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 64
    # A ground plane under the court, so the platform's foot darkens like vanilla's
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.001))
    ground = bpy.context.active_object
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.scene.objects:
        o.select_set(o == obj)
    bpy.ops.object.bake(type='AO', margin=8, use_clear=True)
    bpy.data.objects.remove(ground)
    nodes.remove(node)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)[::-1]   # Blender's rows run bottom-up
    ao = a[..., 0]
    ao = np.clip(0.45 + 0.55 * ao, 0, 1) ** 0.75
    print('UNIQUE mean', round(float(ao.mean()), 3))
    rgba = np.dstack([ao, ao, ao, np.ones_like(ao)])
    levels = [(rgba * 255).astype(np.uint8)]
    while levels[-1].shape[0] > 1:
        lv = levels[-1].astype(np.float32)
        h = lv.shape[0] // 2
        levels.append(lv.reshape(h, 2, h, 2, 4).mean((1, 3)).astype(np.uint8))
    open(OUT_DIR + NAME + '_unique.dds', 'wb').write(dds(levels, size, size))


def dds(levels, w, h):
    """Uncompressed A8R8G8B8 DDS; levels are RGBA arrays, largest first."""
    flags = 0x100F | (0x20000 if len(levels) > 1 else 0)
    caps = 0x1000 | (0x400008 if len(levels) > 1 else 0)
    header = struct.pack('<4sIIIIIII44sIIIIIIIIIIIII', b'DDS ', 124, flags, h, w, w * 4, 0, len(levels), b'\0' * 44,
                         32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000, caps, 0, 0, 0, 0)
    return header + b''.join(lv[..., [2, 1, 0, 3]].tobytes() for lv in levels)


def write_asset():
    text = f'''# The Ehulhul, the Temple of Sin at Harran: a Neo-Babylonian moon-god ziggurat (tools/make_ziggurat_model.py)
pdxmesh = {{
	name = "{NAME}_mesh"
	file = "{NAME}.mesh"

	scale = 1

	meshsettings = {{
		name = "{NAME}_LOD0Shape"
		index = 0
		texture_diffuse = "building_persia_atlas_diffuse.dds"
		texture_normal = "building_persia_atlas_normal.dds"
		texture_specular = "building_persia_atlas_properties.dds"
		texture = {{ file = "{NAME}_unique.dds" index = 5 }}
		shader = "standard_atlas"
		shader_file = "gfx/FX/pdxmesh.shader"
	}}
}}

entity = {{
	name = "{NAME}_entity"
	pdxmesh = "{NAME}_mesh"
}}
'''
    open(OUT_DIR + NAME + '.asset', 'w', encoding='utf-8-sig', newline='\r\n').write(text)


def render_preview(obj):
    sc = bpy.context.scene
    from mathutils import Vector as V
    pts = [obj.matrix_world @ V(c) for c in obj.bound_box]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre, size = (lo + hi) / 2, max(hi - lo)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    cam.location = centre + V((0.9, -1.5, 1.0)) * size
    cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
    sun.data.energy = 4
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    sc.world = w
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 32
    sc.render.resolution_x, sc.render.resolution_y = 900, 640
    sc.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', PREVIEW)


main()
