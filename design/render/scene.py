"""Build the duplex in Blender and render named camera views.

usage: python3 scene.py OUTDIR [view ...]   (no views = all)
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geometry import *  # noqa

IMG = os.path.join(HERE, '..', 'phase-1', 'img')

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
col = scn.collection


def hexc(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)


# ---------------------------------------------------------------- materials
MATS = {}


def mat(name, color='#ffffff', rough=0.5, metal=0.0, trans=0.0, emit=None, estr=0.0, sheen=0.0,
        coat=0.0, alpha=1.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(color)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Sheen Weight'].default_value = sheen
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Alpha'].default_value = alpha
    if trans > 0:
        b.inputs['IOR'].default_value = 1.45
    if emit:
        b.inputs['Emission Color'].default_value = hexc(emit)
        b.inputs['Emission Strength'].default_value = estr
    MATS[name] = m
    return m


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    MATS[name] = m
    return m, m.node_tree.nodes, m.node_tree.links


def tile_floor_mat():
    """Locked main floor: client's 120 x 60 marble-look ceramic (texture from the client's showroom photo,
    exposure normalised between the showroom and the sunlit site photo), 2 mm joints."""
    m, N, L = node_mat('floor_tile')
    b = N['Principled BSDF']
    tex = N.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(os.path.join(IMG, 'floor_marble.jpg'))
    tex.projection = 'BOX'
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / 0.6, 1 / 0.6, 1 / 0.6)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    L.new(mp.outputs['Vector'], tex.inputs['Vector'])
    br = N.new('ShaderNodeTexBrick')
    br.offset = 0.0
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.0018
    br.inputs['Brick Width'].default_value = 1.2
    br.inputs['Row Height'].default_value = 0.6
    br.inputs['Color1'].default_value = (1, 1, 1, 1)
    br.inputs['Color2'].default_value = (0.985, 0.985, 0.98, 1)
    br.inputs['Mortar'].default_value = (0.55, 0.53, 0.5, 1)
    L.new(tc.outputs['Object'], br.inputs['Vector'])
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    L.new(tex.outputs['Color'], mix.inputs[6])
    L.new(br.outputs['Color'], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.3
    return m


def travertine_mat():
    """Locked bathroom tile: the client's own travertine photo, veins horizontal, 1.20 x 0.60 modules."""
    m, N, L = node_mat('travertine')
    b = N['Principled BSDF']
    tex = N.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(os.path.join(IMG, 'travertine_clean.jpg'))
    tex.projection = 'BOX'
    tex.projection_blend = 0.15
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(90))
    mp.inputs['Scale'].default_value = (1 / 0.9, 1 / 0.9, 1 / 0.9)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    L.new(mp.outputs['Vector'], tex.inputs['Vector'])
    br = N.new('ShaderNodeTexBrick')
    br.offset = 0.0
    br.inputs['Mortar Size'].default_value = 0.0015
    br.inputs['Brick Width'].default_value = 1.2
    br.inputs['Row Height'].default_value = 0.6
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Color1'].default_value = (1, 1, 1, 1)
    br.inputs['Color2'].default_value = (1, 1, 1, 1)
    br.inputs['Mortar'].default_value = (0.62, 0.6, 0.57, 1)
    L.new(tc.outputs['Object'], br.inputs['Vector'])
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    L.new(tex.outputs['Color'], mix.inputs[6])
    L.new(br.outputs['Color'], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.35
    return m


def wood_mat(name, color, scale=1.0):
    """straight-grain veneer: noise stretched along the board length (x)."""
    m, N, L = node_mat(name)
    b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.6 * scale, 60 * scale, 60 * scale)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 2.0
    nz.inputs['Detail'].default_value = 8.0
    nz.inputs['Roughness'].default_value = 0.6
    L.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    c = hexc(color)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (c[0] * 0.82, c[1] * 0.82, c[2] * 0.82, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (c[0] * 1.08, c[1] * 1.08, c[2] * 1.08, 1)
    L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.5
    return m


def wallpaper_mat():
    """Kids room: soft pastel yellow wallpaper with a fine tone-on-tone motif (stand-in for 5144-1)."""
    m, N, L = node_mat('wallpaper_yellow')
    b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (14, 14, 14)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi')
    vo.inputs['Scale'].default_value = 1.0
    L.new(mp.outputs['Vector'], vo.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.08
    ramp.color_ramp.elements[0].color = hexc('#EFE2B6')
    ramp.color_ramp.elements[1].position = 0.12
    ramp.color_ramp.elements[1].color = hexc('#F4E9C8')
    L.new(vo.outputs['Distance'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.8
    return m


M = dict(
    wall=mat('wall', '#D9D3C8', 0.85),
    ceiling=mat('ceiling', '#EFEBE4', 0.9),
    floor=tile_floor_mat(),
    trav=travertine_mat(),
    oak=wood_mat('smoked_oak', '#8B6B4D'),
    oak_light=wood_mat('natural_oak', '#C9A57A'),
    walnut=wood_mat('walnut', '#5A4131'),
    bronze=mat('bronze', '#6E5A45', 0.32, 1.0),
    champ=mat('champagne', '#B8A078', 0.3, 1.0),
    boucle=mat('boucle', '#E7E0D2', 0.95, sheen=0.6),
    linen=mat('linen_taupe', '#BEB3A3', 0.9, sheen=0.3),
    linen_ivory=mat('linen_ivory', '#EDE7DC', 0.9, sheen=0.3),
    wool_rug=mat('wool_rug', '#D8CFC1', 1.0, sheen=0.4),
    rug_taupe=mat('rug_taupe', '#B5A796', 1.0, sheen=0.4),
    stone_top=mat('stone_top', '#E9E4DB', 0.25, coat=0.3),
    glass=mat('glass', '#FFFFFF', 0.02, trans=1.0),
    sheer=mat('sheer', '#F4F0E8', 0.9, trans=0.65),
    dark=mat('dark_screen', '#111111', 0.15, coat=0.6),
    white_ceramic=mat('ceramic', '#F5F3EF', 0.12, coat=0.5),
    mirror=mat('mirror', '#FFFFFF', 0.0, 1.0),
    alu=mat('alu_frame', '#8C877F', 0.4, 1.0),
    plant=mat('plant', '#4E6B3F', 0.7),
    pot=mat('pot', '#CBBFAE', 0.8),
    led=mat('led', '#FFFFFF', 0.5, emit='#FFD9A8', estr=6.0),
    lamp=mat('lampshade', '#F6EFE2', 0.8, trans=0.3, emit='#FFD9A8', estr=1.2),
    ivory_panel=mat('ivory_panel', '#F3EEE3', 0.6),
    yellow=mat('yellow_soft', '#F1DE9E', 0.9, sheen=0.4),
    yellow_wall=wallpaper_mat(),
    art=mat('art', '#C9BBA4', 0.9),
    sky_ground=mat('ground', '#CDBFA8', 1.0),
    building=mat('building', '#D8CBB6', 0.9),
)


# ---------------------------------------------------------------- primitives
def box(name, x0, y0, z0, x1, y1, z1, m, bevel=0.0):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    me = bpy.data.meshes.new(name)
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(v, [], f)
    me.update()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.data.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new('bv', 'BEVEL')
        md.width = bevel
        md.segments = 3
        md.limit_method = 'ANGLE'
    return o


def cyl(name, x, y, z0, z1, r, m, verts=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new('bv', 'BEVEL')
        md.width = bevel
        md.segments = 3
        md.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth()
    return o


def sphere(name, x, y, z, r, m, sx=1, sy=1, sz=1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=32, ring_count=16)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def rot_group(objs, cx, cy, ang):
    for o in objs:
        o.rotation_euler.rotate_axis('Z', 0)
    for o in objs:
        loc = o.matrix_world.translation.copy() if False else None
    # rotate around (cx, cy)
    empty = bpy.data.objects.new('pivot', None)
    col.objects.link(empty)
    empty.location = (cx, cy, 0)
    for o in objs:
        o.parent = empty
        o.location = (o.location[0] - cx, o.location[1] - cy, o.location[2])
        if o.data and hasattr(o.data, 'vertices'):
            for v in o.data.vertices:
                v.co.x -= cx
                v.co.y -= cy
            o.location = (o.location[0] + cx, o.location[1] + cy, o.location[2]) if o.type != 'MESH' else o.location
    empty.rotation_euler = (0, 0, math.radians(ang))
    return empty


# ---------------------------------------------------------------- architecture
OPEN_DOORS = {(4.15, 5.05), (3.3, 4.2), (11.3, 12.2), (4.55, 5.4), (3.45, 4.25), (9.75, 10.65)}
def build_wall(x0, y0, x1, y1, openings, z0, h, m, level):
    horiz = (x1 - x0) >= (y1 - y0)
    a0, a1 = (x0, x1) if horiz else (y0, y1)

    def piece(p0, p1, zz0, zz1, tag):
        if p1 - p0 < 1e-3 or zz1 - zz0 < 1e-3:
            return
        if horiz:
            box(f'wall_{level}_{tag}', p0, y0, z0 + zz0, p1, y1, z0 + zz1, m)
        else:
            box(f'wall_{level}_{tag}', x0, p0, z0 + zz0, x1, p1, z0 + zz1, m)

    ops = sorted(openings, key=lambda o: o[0])
    cur = a0
    for i, (a, b, oz0, oz1, kind) in enumerate(ops):
        piece(cur, a, 0, h, f'{i}s')
        piece(a, b, 0, oz0, f'{i}b')
        piece(a, b, oz1, h, f'{i}t')
        th = (y1 - y0) if horiz else (x1 - x0)
        mid = ((y0 + y1) / 2) if horiz else ((x0 + x1) / 2)
        if kind in ('window', 'glass'):
            f = 0.05
            if horiz:
                box('frame', a, mid - 0.03, z0 + oz0, b, mid + 0.03, z0 + oz0 + f, M['alu'])
                box('frame', a, mid - 0.03, z0 + oz1 - f, b, mid + 0.03, z0 + oz1, M['alu'])
                box('frame', a, mid - 0.03, z0 + oz0, a + f, mid + 0.03, z0 + oz1, M['alu'])
                box('frame', b - f, mid - 0.03, z0 + oz0, b, mid + 0.03, z0 + oz1, M['alu'])
                nm = max(1, round((b - a) / 1.3))
                for k in range(1, nm):
                    xm = a + k * (b - a) / nm
                    box('mullion', xm - 0.025, mid - 0.03, z0 + oz0, xm + 0.025, mid + 0.03, z0 + oz1, M['alu'])
                box('glass', a, mid - 0.004, z0 + oz0, b, mid + 0.004, z0 + oz1, M['glass'])
            else:
                box('frame', mid - 0.03, a, z0 + oz0, mid + 0.03, b, z0 + oz0 + f, M['alu'])
                box('frame', mid - 0.03, a, z0 + oz1 - f, mid + 0.03, b, z0 + oz1, M['alu'])
                box('frame', mid - 0.03, a, z0 + oz0, mid + 0.03, a + f, z0 + oz1, M['alu'])
                box('frame', mid - 0.03, b - f, z0 + oz0, mid + 0.03, b, z0 + oz1, M['alu'])
                nm = max(1, round((b - a) / 1.3))
                for k in range(1, nm):
                    ym = a + k * (b - a) / nm
                    box('mullion', mid - 0.03, ym - 0.025, z0 + oz0, mid + 0.03, ym + 0.025, z0 + oz1, M['alu'])
                box('glass', mid - 0.004, a, z0 + oz0, mid + 0.004, b, z0 + oz1, M['glass'])
        elif kind == 'door' and (a, b) not in OPEN_DOORS:
            # flush full-height smoked-oak door, shown closed except where a view needs it open
            t = 0.045
            if horiz:
                box('doorleaf', a + 0.01, mid - t / 2, z0 + 0.01, b - 0.01, mid + t / 2, z0 + oz1 - 0.005, M['oak'])
                box('handle', b - 0.12, mid - 0.06, z0 + 1.0, b - 0.10, mid + 0.06, z0 + 1.35, M['bronze'])
            else:
                box('doorleaf', mid - t / 2, a + 0.01, z0 + 0.01, mid + t / 2, b - 0.01, z0 + oz1 - 0.005, M['oak'])
                box('handle', mid - 0.06, b - 0.12, z0 + 1.0, mid + 0.06, b - 0.10, z0 + 1.35, M['bronze'])
        cur = b
    piece(cur, a1, 0, h, 'e')


def build_level(walls, z0, level):
    for i, (x0, y0, x1, y1, ops) in enumerate(walls):
        build_wall(x0, y0, x1, y1, ops, z0, CEIL, M['wall'], f'{level}_{i}')


def slab(x0, y0, x1, y1, z, m, name, holes=()):
    """floor/ceiling rectangle split around rectangular holes (simple grid split)."""
    xs = sorted({x0, x1, *[h[0] for h in holes], *[h[2] for h in holes]})
    ys = sorted({y0, y1, *[h[1] for h in holes], *[h[3] for h in holes]})
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if any(h[0] <= cx <= h[2] and h[1] <= cy <= h[3] for h in holes):
                continue
            box(name, xs[i], ys[j], z - 0.01, xs[i + 1], ys[j + 1], z, m)


# level 01
build_level(L01_WALLS, 0.0, 'L01')
for c in L01_COLUMNS:
    box('column', c[0], c[1], 0, c[2], c[3], CEIL, M['wall'])
slab(0.2, 0.2, 12.5, 7.9, 0.0, M['floor'], 'floor_L01')
# L01 ceiling (void above stair)
slab(0.2, 0.2, 12.5, 7.9, CEIL + 0.01, M['ceiling'], 'ceil_L01', holes=[L02_VOID])
# fill outside the L01 footprint top-right (11.2-12.7 x 4.35-8.08) is exterior: nothing
# level 02
build_level(L02_WALLS, L2Z, 'L02')
slab(0.2, 0.2, 19.8, 7.9, L2Z, M['floor'], 'floor_L02', holes=[L02_VOID])
slab(5.35, 0.2, 19.8, 7.9, L2Z + CEIL + 0.01, M['ceiling'], 'ceil_L02')
slab(0.2, 3.2, 5.35, 7.9, L2Z + CEIL + 0.01, M['ceiling'], 'ceil_L02b')
# terrace glass roof (x 0.2-5.2, y 0.2-3.0)
for k in range(5):
    box('roof_beam', 0.2 + k * 1.2, 0.2, L2Z + CEIL - 0.08, 0.26 + k * 1.2, 3.0, L2Z + CEIL, M['alu'])
box('roof_glass', 0.2, 0.2, L2Z + CEIL - 0.01, 5.2, 3.0, L2Z + CEIL, M['glass'])
# slab between L01 ceiling and L02 floor (visual thickness from outside only)
# bathrooms: travertine walls (cladding) and floor
BATHS = {
    'wc_L01': (5.35, 4.45, 6.9, 7.9, 0.0),
    'bath_nanny': (0.2, 3.2, 1.6, 5.5, L2Z),
    'bath_master': (11.1, 5.6, 12.7, 7.9, L2Z),
    'bath_office': (11.1, 0.2, 12.7, 3.2, L2Z),
}
def clad(x0, y0, x1, y1, z, h0, h1, m, ops, name, t=0.012):
    """line the inside faces of a room; ops = {'N'|'S'|'E'|'W': [(a, b, z0, z1), ...]}"""
    sides = {'N': (x0, y1 - t, x1, y1), 'S': (x0, y0, x1, y0 + t), 'W': (x0, y0, x0 + t, y1), 'E': (x1 - t, y0, x1, y1)}
    for k, (a0, b0, a1, b1) in sides.items():
        horiz = k in 'NS'
        lo, hi = (a0, a1) if horiz else (b0, b1)
        cur = lo
        for (a, b, oz0, oz1) in sorted(ops.get(k, [])):
            for (p0, p1, q0, q1) in [(cur, a, h0, h1), (a, b, h0, max(h0, oz0)), (a, b, min(h1, oz1), h1)]:
                if p1 - p0 > 1e-3 and q1 - q0 > 1e-3:
                    if horiz:
                        box(name, p0, b0, z + q0, p1, b1, z + q1, m)
                    else:
                        box(name, a0, p0, z + q0, a1, p1, z + q1, m)
            cur = b
        if hi - cur > 1e-3:
            if horiz:
                box(name, cur, b0, z + h0, hi, b1, z + h1, m)
            else:
                box(name, a0, cur, z + h0, a1, hi, z + h1, m)


BATH_OPS = {
    'wc_L01': {'S': [(5.6, 6.4, 0, 2.3)]},
    'bath_nanny': {'E': [(3.45, 4.2, 0, 2.3)]},
    'bath_master': {'S': [(11.45, 12.2, 0, 2.3)], 'N': [(11.3, 12.1, 1.7, 2.3)]},
    'bath_office': {'N': [(11.8, 12.6, 0, 2.3)]},
}
for n, (x0, y0, x1, y1, z) in BATHS.items():
    box(n + '_floor', x0, y0, z, x1, y1, z + 0.004, M['trav'])
    clad(x0, y0, x1, y1, z, 0.0, CEIL, M['trav'], BATH_OPS[n], n + '_clad')

# ---------------------------------------------------------------- stair
def stair():
    r = 3.5 / 22
    tread = (4.1 - 1.05) / 10
    y0, y1 = STAIR['y_run1']
    # run 1: from x=4.1 (step 1) toward x=1.05, rising
    for i in range(10):
        xa = 4.1 - (i + 1) * tread
        xb = 4.1 - i * tread
        z = (i + 1) * r
        box(f'st1_{i}', xa, y0, z - 0.04, xb + 0.02, y1 - 0.02, z, M['floor'])
        box(f'st1r_{i}', xb - 0.01, y0, z - r, xb + 0.02, y1 - 0.02, z - 0.04, M['floor'])
        box(f'st1s_{i}', xa, y0, 0, xb, y1 - 0.02, z - 0.04, M['wall'])
    zl = 11 * r
    box('landing', 0.2, y0, zl - 0.25, 1.05, 7.9, zl, M['floor'])
    y0b, y1b = STAIR['y_run2']
    for i in range(10):
        xa = 1.05 + i * tread
        xb = 1.05 + (i + 1) * tread
        z = zl + (i + 1) * r
        box(f'st2_{i}', xa - 0.02, y0b + 0.02, z - 0.04, xb, y1b, z, M['floor'])
        box(f'st2r_{i}', xa - 0.02, y0b + 0.02, z - r, xa + 0.01, y1b, z - 0.04, M['floor'])
        box(f'st2s_{i}', xa, y0b + 0.02, 0.0, xb, y1b, z - 0.04, M['wall'])
    # LED strip under each tread nosing (warm)
    # central balustrade: frameless glass + smoked oak handrail, along y=6.8 (between runs)
    box('bal_glass', 1.05, 6.79, 0.0, 4.1, 6.81, 3.5 + 0.92, M['glass'])
    for i in range(21):
        pass
    for (yy, p0, p1) in [(6.74, (4.1, r + 0.95), (1.05, zl + 0.95)), (6.86, (1.05, zl + 0.95), (4.1, 3.5 + 0.95))]:
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dz)
        bpy.ops.mesh.primitive_cube_add(size=1, location=((p0[0] + p1[0]) / 2, yy, (p0[1] + p1[1]) / 2))
        o = bpy.context.active_object
        o.scale = (ln, 0.05, 0.045)
        o.rotation_euler = (0, -math.atan2(dz, dx), 0)
        o.data.materials.append(M['oak'])
    # L02 guard around the void (glass) along y=5.7 edge is wall; along x=4.1 edge (arrival) glass guard
    box('void_guard', 4.08, 5.7, L2Z, 4.11, 6.8, L2Z + 1.05, M['glass'])
    box('void_rail', 4.06, 5.7, L2Z + 1.05, 4.13, 6.8, L2Z + 1.1, M['oak'])


stair()

# ---------------------------------------------------------------- furniture helpers
def sofa(x0, y0, w, d, facing='N', m=None, arm=0.18, h=0.72, seat=0.42, name='sofa'):
    """facing = direction the sitter looks. returns objects."""
    m = m or M['boucle']
    objs = []
    if facing in ('N', 'S'):
        x1, y1 = x0 + w, y0 + d
        back = (y0, y0 + 0.22) if facing == 'N' else (y1 - 0.22, y1)
        objs.append(box(name + '_base', x0, y0, 0.06, x1, y1, seat - 0.1, m, 0.03))
        objs.append(box(name + '_back', x0, back[0], seat - 0.12, x1, back[1], h, m, 0.06))
        objs.append(box(name + '_armL', x0, y0, seat - 0.12, x0 + arm, y1, h - 0.1, m, 0.06))
        objs.append(box(name + '_armR', x1 - arm, y0, seat - 0.12, x1, y1, h - 0.1, m, 0.06))
        n = max(1, round((w - 2 * arm) / 0.9))
        cw = (w - 2 * arm) / n
        cy0, cy1 = ((y0 + 0.22, y1) if facing == 'N' else (y0, y1 - 0.22))
        for i in range(n):
            objs.append(box(name + f'_cush{i}', x0 + arm + i * cw + 0.01, cy0, seat - 0.1,
                            x0 + arm + (i + 1) * cw - 0.01, cy1, seat + 0.04, m, 0.05))
        objs.append(box(name + '_plinth', x0 + 0.05, y0 + 0.05, 0.0, x1 - 0.05, y1 - 0.05, 0.06, M['bronze']))
    else:
        x1, y1 = x0 + d, y0 + w
        back = (x0, x0 + 0.22) if facing == 'E' else (x1 - 0.22, x1)
        objs.append(box(name + '_base', x0, y0, 0.06, x1, y1, seat - 0.1, m, 0.03))
        objs.append(box(name + '_back', back[0], y0, seat - 0.12, back[1], y1, h, m, 0.06))
        objs.append(box(name + '_armL', x0, y0, seat - 0.12, x1, y0 + arm, h - 0.1, m, 0.06))
        objs.append(box(name + '_armR', x0, y1 - arm, seat - 0.12, x1, y1, h - 0.1, m, 0.06))
        n = max(1, round((w - 2 * arm) / 0.9))
        cw = (w - 2 * arm) / n
        cx0, cx1 = ((x0 + 0.22, x1) if facing == 'E' else (x0, x1 - 0.22))
        for i in range(n):
            objs.append(box(name + f'_cush{i}', cx0, y0 + arm + i * cw + 0.01, seat - 0.1, cx1,
                            y0 + arm + (i + 1) * cw - 0.01, seat + 0.04, m, 0.05))
        objs.append(box(name + '_plinth', x0 + 0.05, y0 + 0.05, 0.0, x1 - 0.05, y1 - 0.05, 0.06, M['bronze']))
    return objs


def lounge_chair(cx, cy, facing, m=None, name='chair'):
    m = m or M['linen']
    ang = {'N': 0, 'E': -90, 'S': 180, 'W': 90}[facing] if isinstance(facing, str) else facing
    o = []
    o.append(cyl(name + '_seat', cx, cy, 0.18, 0.42, 0.40, m, bevel=0.06))
    back = sphere(name + '_back', 0, 0, 0.55, 0.42, m, 1.0, 0.35, 0.55)
    a = math.radians(ang)
    back.location = (cx - 0.28 * math.sin(-a) * -1 * 0 + (-math.sin(a)) * -0.3, cy - math.cos(a) * 0.3, 0.58)
    back.location = (cx + math.sin(a) * 0.30, cy - math.cos(a) * 0.30, 0.58)
    back.rotation_euler = (0, 0, a)
    o.append(back)
    o.append(cyl(name + '_foot', cx, cy, 0.0, 0.18, 0.18, M['bronze']))
    return o


def rug(x0, y0, x1, y1, z=0.0, m=None, name='rug'):
    return box(name, x0, y0, z + 0.001, x1, y1, z + 0.014, m or M['wool_rug'], 0.005)


def coffee_round(cx, cy, r, z=0.0, m=None, h=0.36, name='ctable'):
    return [cyl(name, cx, cy, z + h - 0.05, z + h, r, m or M['trav'], bevel=0.01),
            cyl(name + '_base', cx, cy, z, z + h - 0.05, r * 0.6, M['oak'])]


def pendant_ring(cx, cy, ztop, r=0.45, drop=0.9, name='pend'):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.018, location=(cx, cy, ztop - drop))
    o = bpy.context.active_object
    o.data.materials.append(M['led'])
    bpy.ops.object.shade_smooth()
    for k in range(3):
        a = k * 2 * math.pi / 3
        box(name + f'_w{k}', cx + r * math.cos(a) - 0.002, cy + r * math.sin(a) - 0.002, ztop - drop,
            cx + r * math.cos(a) + 0.002, cy + r * math.sin(a) + 0.002, ztop, M['bronze'])
    return o


def linear_pendant(x0, x1, y, ztop, drop=0.85, name='lin'):
    box(name, x0, y - 0.025, ztop - drop - 0.03, x1, y + 0.025, ztop - drop, M['bronze'])
    box(name + '_led', x0 + 0.02, y - 0.018, ztop - drop - 0.032, x1 - 0.02, y + 0.018, ztop - drop - 0.028, M['led'])
    for x in (x0 + 0.2, x1 - 0.2):
        box(name + '_w', x - 0.002, y - 0.002, ztop - drop, x + 0.002, y + 0.002, ztop, M['bronze'])


def downlight(x, y, zc):
    cyl('dl', x, y, zc - 0.004, zc, 0.04, M['led'], verts=16)
    ld = bpy.data.lights.new('dl', 'SPOT')
    ld.energy = 25
    ld.spot_size = math.radians(70)
    ld.spot_blend = 0.6
    ld.color = (1.0, 0.82, 0.62)
    lo = bpy.data.objects.new('dl', ld)
    lo.location = (x, y, zc - 0.02)
    col.objects.link(lo)


def cove(x0, y0, x1, y1, zc, strength=40):
    ld = bpy.data.lights.new('cove', 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = max(0.05, x1 - x0)
    ld.size_y = max(0.05, y1 - y0)
    ld.energy = strength * (x1 - x0) * (y1 - y0) + 20
    ld.color = (1.0, 0.84, 0.66)
    lo = bpy.data.objects.new('cove', ld)
    lo.location = ((x0 + x1) / 2, (y0 + y1) / 2, zc - 0.05)
    col.objects.link(lo)


def curtain(x0, y0, x1, y1, z0, z1, m=None, name='curt'):
    """sheer ripple-fold curtain as a row of thin slightly offset panels."""
    m = m or M['sheer']
    horiz = abs(x1 - x0) > abs(y1 - y0)
    L_ = abs(x1 - x0) if horiz else abs(y1 - y0)
    n = max(4, int(L_ / 0.12))
    for i in range(n):
        off = 0.03 * math.sin(i * math.pi / 2)
        if horiz:
            xa = x0 + i * (x1 - x0) / n
            box(name, xa, y0 + off, z0, xa + (x1 - x0) / n * 1.05, y0 + off + 0.01, z1, m)
        else:
            ya = y0 + i * (y1 - y0) / n
            box(name, x0 + off, ya, z0, x0 + off + 0.01, ya + (y1 - y0) / n * 1.05, z1, m)
    # recessed track shadow gap
    if horiz:
        box(name + '_track', x0, y0 - 0.05, z1, x1, y0 + 0.08, z1 + 0.02, M['bronze'])
    else:
        box(name + '_track', x0 - 0.05, y0, z1, x0 + 0.08, y1, z1 + 0.02, M['bronze'])


def plant(x, y, z=0.0, h=1.6, name='plant'):
    """potted olive tree proxy: stone pot, slim trunk, loose canopy of small leaves."""
    import random
    rnd = random.Random(int(x * 100 + y * 10))
    cyl(name + '_pot', x, y, z, z + 0.42, 0.22, M['pot'], bevel=0.02)
    cyl(name + '_soil', x, y, z + 0.40, z + 0.41, 0.2, M['walnut'])
    cyl(name + '_trunk', x, y, z + 0.4, z + h * 0.62, 0.025, M['walnut'], verts=12)
    for k in range(3):
        a = k * 2.1
        box(name + '_br', x, y, z + h * 0.55, x + 0.25 * math.cos(a), y + 0.25 * math.sin(a), z + h * 0.56 + 0.2, M['walnut'])
    for k in range(140):
        r = 0.42 * rnd.random() ** 0.5
        a = rnd.random() * 6.283
        zz = z + h * 0.58 + rnd.random() * h * 0.42
        o = sphere(name + '_lf', x + r * math.cos(a), y + r * math.sin(a), zz, 0.045, M['plant'], 1.0, 0.35, 0.18)
        o.rotation_euler = (rnd.random() * 3, rnd.random() * 3, rnd.random() * 3)


def joinery_wall(x0, y0, x1, y1, z0, z1, m, name='join', panel=0.6, gap=0.006):
    """full-height flush joinery with thin shadow gaps."""
    horiz = abs(x1 - x0) >= abs(y1 - y0)
    L_ = abs(x1 - x0) if horiz else abs(y1 - y0)
    n = max(1, round(L_ / panel))
    for i in range(n):
        if horiz:
            a = x0 + i * (x1 - x0) / n
            b = x0 + (i + 1) * (x1 - x0) / n
            box(name, a + gap, y0, z0, b - gap, y1, z1, m)
        else:
            a = y0 + i * (y1 - y0) / n
            b = y0 + (i + 1) * (y1 - y0) / n
            box(name, x0, a + gap, z0, x1, b - gap, z1, m)


def bed(x0, y0, w, L_, head='N', z=0.0, m=None, head_m=None, name='bed', hb_h=1.2):
    m = m or M['linen_ivory']
    head_m = head_m or M['linen']
    if head == 'N':
        x1, y1 = x0 + w, y0 + L_
        box(name + '_frame', x0, y0, z + 0.1, x1, y1 - 0.08, z + 0.32, head_m, 0.03)
        box(name + '_matt', x0 + 0.03, y0 + 0.03, z + 0.32, x1 - 0.03, y1 - 0.1, z + 0.55, m, 0.05)
        box(name + '_duvet', x0 - 0.02, y0 - 0.02, z + 0.5, x1 + 0.02, y1 - 0.6, z + 0.6, M['linen_ivory'], 0.05)
        box(name + '_throw', x0 - 0.03, y0 + 0.1, z + 0.55, x1 + 0.03, y0 + 0.55, z + 0.62, M['linen'], 0.03)
        box(name + '_hb', x0 - 0.15, y1 - 0.1, z + 0.1, x1 + 0.15, y1, z + hb_h, head_m, 0.05)
        for k in range(2 if w > 1.3 else 1):
            px = x0 + (k + 0.5) * w / (2 if w > 1.3 else 1)
            box(name + '_pillow', px - 0.33, y1 - 0.45, z + 0.55, px + 0.33, y1 - 0.12, z + 0.78, M['linen_ivory'], 0.07)
    elif head == 'W':
        x1, y1 = x0 + L_, y0 + w
        box(name + '_frame', x0 + 0.08, y0, z + 0.1, x1, y1, z + 0.32, head_m, 0.03)
        box(name + '_matt', x0 + 0.1, y0 + 0.03, z + 0.32, x1 - 0.03, y1 - 0.03, z + 0.55, m, 0.05)
        box(name + '_duvet', x0 + 0.6, y0 - 0.02, z + 0.5, x1 + 0.02, y1 + 0.02, z + 0.6, M['linen_ivory'], 0.05)
        box(name + '_hb', x0, y0 - 0.15, z + 0.1, x0 + 0.1, y1 + 0.15, z + hb_h, head_m, 0.05)
        box(name + '_pillow', x0 + 0.12, y0 + 0.1, z + 0.55, x0 + 0.45, y1 - 0.1, z + 0.76, M['linen_ivory'], 0.07)


def vanity(x0, y0, x1, y1, z, top_m=None, body_m=None, name='van', mirror_face=None):
    body_m = body_m or M['oak']
    top_m = top_m or M['stone_top']
    box(name + '_body', x0, y0, z + 0.32, x1, y1, z + 0.82, body_m, 0.01)
    box(name + '_top', x0 - 0.01, y0 - 0.01, z + 0.82, x1 + 0.01, y1 + 0.01, z + 0.86, top_m, 0.005)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cyl(name + '_basin', cx, cy, z + 0.86, z + 0.99, 0.2, M['white_ceramic'], bevel=0.02)
    box(name + '_led', x0 + 0.03, y0 + 0.03, z + 0.315, x1 - 0.03, y1 - 0.03, z + 0.32, M['led'])


def wc(x, y, z, facing, name='wc'):
    a = {'N': 0, 'E': -90, 'S': 180, 'W': 90}[facing]
    dx, dy = -math.sin(math.radians(a)), math.cos(math.radians(a))
    sphere(name + '_bowl', x + dx * 0.3, y + dy * 0.3, z + 0.36, 0.22, M['white_ceramic'], 1.0, 1.0, 0.45)
    ox, oy = x + dx * 0.1, y + dy * 0.1
    box(name + '_back', ox - 0.18 if dy else ox - 0.05, oy - 0.05 if dy else oy - 0.18, z + 0.25,
        ox + 0.18 if dy else ox + 0.05, oy + 0.05 if dy else oy + 0.18, z + 0.45, M['white_ceramic'], 0.03)
    box(name + '_plate', x - 0.12 if dy else x - 0.01, y - 0.01 if dy else y - 0.12, z + 1.0,
        x + 0.12 if dy else x + 0.01, y + 0.01 if dy else y + 0.12, z + 1.16, M['bronze'])


def shower_glass(x0, y0, x1, y1, z):
    box('shower_glass', x0, y0, z, x1, y1, z + 2.1, M['glass'])
    box('shower_prof', x0, y0, z + 2.08, x1, y1, z + 2.1, M['bronze'])


def mirror_panel(x0, y0, x1, y1, z0, z1, name='mir', frame=True):
    horiz = abs(x1 - x0) > abs(y1 - y0)
    box(name, x0, y0, z0, x1, y1, z1, M['mirror'])
    if frame:
        e = 0.015
        if horiz:
            box(name + 'f', x0 - e, y0 - 0.003, z0 - e, x1 + e, y1 - 0.004, z1 + e, M['bronze'])
        else:
            box(name + 'f', x0 - 0.003, y0 - e, z0 - e, x1 - 0.004, y1 + e, z1 + e, M['bronze'])


def art(x0, y0, x1, y1, z0, z1, m=None):
    box('art', x0, y0, z0, x1, y1, z1, m or M['art'], 0.004)


# ================================================================== LEVEL 01 FURNITURE
z = 0.0
# --- living (x 0.2-5.15, y 0.2-5.5); feature wall = stair wall at y 5.5
joinery_wall(0.35, 5.08, 4.1, 5.5, 0, 2.6, M['oak'], 'tvwall', panel=0.62)
box('tv_niche', 1.2, 5.05, 1.05, 3.25, 5.1, 2.2, M['wall'])
box('tv', 1.35, 5.03, 1.2, 3.1, 5.06, 2.18, M['dark'])
box('tv_console', 0.35, 4.62, 0.0, 4.1, 5.08, 0.42, M['oak'], 0.01)
box('tv_console_top', 0.35, 4.62, 0.42, 4.1, 5.08, 0.45, M['trav'])
box('tvwall_led', 0.35, 5.05, 2.6, 4.1, 5.08, 2.61, M['led'])
rug(0.7, 1.2, 4.1, 4.1, m=M['wool_rug'])
sofa(0.8, 0.75, 3.0, 1.05, 'N', name='sofa_liv')
coffee_round(2.0, 2.75, 0.5)
coffee_round(2.9, 2.55, 0.35, h=0.30, name='ctable2')
lounge_chair(0.95, 3.7, -120, name='lc1')
lounge_chair(3.75, 3.55, 120, M['boucle'], name='lc2')
box('side_tbl', 4.05, 1.05, 0.0, 4.45, 1.45, 0.52, M['oak'], 0.02)
cyl('lamp_base', 4.25, 1.25, 0.52, 0.9, 0.06, M['trav'])
cyl('lamp_shade', 4.25, 1.25, 0.9, 1.15, 0.2, M['lamp'])
curtain(0.28, 2.1, 0.28, 5.05, 0.02, 2.95, name='curt_liv')
curtain(0.24, 0.3, 4.9, 0.3, 0.02, 2.95, M['linen_ivory'], name='curt_liv_b') if False else None
pendant_ring(2.35, 2.75, CEIL, 0.55, 0.95)
plant(0.55, 0.55, h=1.8)
art(4.95, 1.9, 5.15, 3.4, 1.1, 2.3) if False else None
# --- column wrapped in fluted oak
joinery_wall(5.13, 1.28, 5.37, 1.87, 0, CEIL, M['oak'], 'col', panel=0.06)
# --- console + art on bottom wall between living & dining
box('console', 5.8, 0.2, 0.0, 7.2, 0.62, 0.78, M['oak'], 0.01)
box('console_top', 5.78, 0.2, 0.78, 7.22, 0.64, 0.81, M['trav'])
art(5.9, 0.2, 7.1, 0.22, 1.25, 2.25, M['linen'])
cyl('vase', 6.0, 0.42, 0.81, 1.15, 0.09, M['pot'])
# --- dining (table centred on window)
din_cx, din_cy = 9.05, 2.25
box('din_top', din_cx - 1.3, din_cy - 0.55, 0.72, din_cx + 1.3, din_cy + 0.55, 0.76, M['oak'], 0.02)
box('din_leg1', din_cx - 0.85, din_cy - 0.2, 0.0, din_cx - 0.55, din_cy + 0.2, 0.72, M['oak'], 0.02)
box('din_leg2', din_cx + 0.55, din_cy - 0.2, 0.0, din_cx + 0.85, din_cy + 0.2, 0.72, M['oak'], 0.02)
rug(din_cx - 2.1, din_cy - 1.6, din_cx + 2.1, din_cy + 1.6, m=M['rug_taupe'], name='din_rug')
def dining_chair(cx, cy, face, name='dch'):
    """face = unit vector the sitter looks toward (table)."""
    fx, fy = face
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(name + '_leg', cx + sx * 0.19 - 0.015, cy + sy * 0.19 - 0.015, 0.0, cx + sx * 0.19 + 0.015,
                cy + sy * 0.19 + 0.015, 0.44, M['oak'])
    box(name + '_seat', cx - 0.23, cy - 0.23, 0.44, cx + 0.23, cy + 0.23, 0.5, M['linen'], 0.03)
    bx, by = cx - fx * 0.21, cy - fy * 0.21
    if fx == 0:
        box(name + '_back', bx - 0.23, by - 0.03, 0.52, bx + 0.23, by + 0.03, 0.86, M['linen'], 0.03)
    else:
        box(name + '_back', bx - 0.03, by - 0.23, 0.52, bx + 0.03, by + 0.23, 0.86, M['linen'], 0.03)


for i in range(3):
    for side in (-1, 1):
        dining_chair(din_cx - 0.85 + i * 0.85, din_cy + side * 0.8, (0, -side))
for side in (-1, 1):
    dining_chair(din_cx + side * 1.55, din_cy, (-side, 0))
linear_pendant(din_cx - 0.95, din_cx + 0.95, din_cy, CEIL, 1.3)
curtain(7.75, 0.28, 10.35, 0.28, 0.02, 2.95, name='curt_din')
# sideboard on bump wall
box('sideboard', 12.05, 0.9, 0.0, 12.5, 3.5, 0.8, M['oak'], 0.01)
box('sideboard_top', 12.03, 0.88, 0.8, 12.5, 3.52, 0.83, M['trav'])
art(12.47, 1.3, 12.5, 3.1, 1.25, 2.35, M['art'])
plant(11.7, 3.75, h=1.7)
# --- kitchen (x 8.2-11.0, y 4.25-7.9)
box('k_base_top', 8.2, 7.3, 0.0, 10.4, 7.9, 0.88, M['oak'], 0.005)
box('k_counter', 8.2, 7.28, 0.88, 10.4, 7.9, 0.92, M['stone_top'])
box('k_splash', 8.2, 7.86, 0.92, 10.4, 7.9, 1.55, M['stone_top'])
box('k_wall_units', 8.2, 7.55, 1.55, 10.4, 7.9, 2.35, M['oak'], 0.005)
box('k_wall_led', 8.2, 7.55, 1.545, 10.4, 7.88, 1.55, M['led'])
box('k_upper_fill', 8.2, 7.55, 2.35, 11.0, 7.9, CEIL, M['wall'])
joinery_wall(10.4, 5.1, 11.0, 7.9, 0, 2.35, M['oak'], 'k_tall', panel=0.6)
box('k_tall_top', 10.4, 5.1, 2.35, 11.0, 7.9, CEIL, M['wall'])
box('cooktop', 9.4, 7.4, 0.92, 10.1, 7.8, 0.925, M['dark'])
box('sink', 8.55, 7.4, 0.86, 9.25, 7.8, 0.925, M['alu'])
box('tap', 8.88, 7.8, 0.92, 8.92, 7.84, 1.2, M['bronze'])
box('isl_body', 8.45, 4.75, 0.0, 10.75, 5.7, 0.88, M['oak'], 0.005)
box('isl_top', 8.4, 4.55, 0.88, 10.8, 5.72, 0.93, M['stone_top'], 0.005)
for k in range(3):
    sx = 8.9 + k * 0.7
    cyl('stool_seat', sx, 4.2, 0.62, 0.68, 0.2, M['linen'], bevel=0.02)
    cyl('stool_leg', sx, 4.2, 0.0, 0.62, 0.025, M['bronze'])
for k in range(3):
    px = 8.95 + k * 0.7
    sphere('isl_pend', px, 5.15, CEIL - 0.95, 0.12, M['lamp'])
    box('isl_pend_w', px - 0.002, 5.148, CEIL - 0.85, px + 0.002, 5.152, CEIL, M['bronze'])
# --- stair hall
art(5.13, 6.2, 5.15, 7.5, 1.1, 2.2, M['linen'])
box('hall_bench', 4.75, 6.1, 0.0, 5.13, 7.6, 0.45, M['oak'], 0.02)
# --- guest WC (x 5.35-6.9, y 4.45-7.9)
vanity(5.65, 7.42, 6.65, 7.88, 0.0, top_m=M['trav'], name='wc1_van')
mirror_panel(5.75, 7.87, 6.55, 7.875, 1.05, 2.25, 'wc1_mir')
box('wc1_mir_led', 5.72, 7.874, 1.02, 6.58, 7.876, 2.28, M['led'])
wc(6.88, 6.1, 0.0, 'W', 'wc1')
box('wc1_sconce', 5.37, 6.9, 1.7, 5.4, 7.0, 2.0, M['lamp'])

# ================================================================== LEVEL 02 FURNITURE
z = L2Z
# --- entrance corridor (x 5.35-6.85, y 4.5-7.9); door at top x 5.45-6.45
joinery_wall(6.45, 4.6, 6.85, 6.85, z, z + 2.4, M['oak'], 'shoe', panel=0.55)
box('shoe_top', 6.45, 4.6, z + 2.4, 6.85, 6.85, z + CEIL, M['wall'])
box('shoe_niche', 6.4, 5.4, z + 0.95, 6.46, 6.1, z + 1.35, M['led'])
box('entry_bench', 6.45, 6.95, z, 6.85, 7.75, z + 0.45, M['boucle'], 0.04)
rug(5.55, 6.3, 6.35, 7.7, z, M['rug_taupe'], 'entry_rug')
for yy in (5.2, 6.2, 7.2):
    downlight(6.1, yy, z + CEIL)
# --- family lounge (x 5.35-10.9, y 0.2-4.3)
rug(7.2, 0.8, 10.2, 3.4, z, M['wool_rug'], 'lounge_rug')
for o in sofa(6.4, 0.7, 3.0, 1.05, 'E', name='sofa_fam'):
    o.location.z += z
for o in coffee_round(8.3, 2.05, 0.55, z):
    pass
for o in lounge_chair(9.35, 3.45, 150, M['boucle'], 'lc3'):
    o.location.z += z
box('media', 10.45, 0.7, z, 10.9, 3.1, z + 0.45, M['oak'], 0.01)
box('media_top', 10.43, 0.68, z + 0.45, 10.9, 3.12, z + 0.48, M['trav'])
joinery_wall(10.8, 0.5, 10.9, 3.2, z + 0.48, z + CEIL, M['oak'], 'tv2wall', panel=0.1)
box('tv2', 10.76, 0.95, z + 1.05, 10.8, 2.6, z + 1.98, M['dark'])
curtain(8.15, 0.28, 10.65, 0.28, z + 0.02, z + 2.95, name='curt_fam')
pendant_ring(8.3, 2.05, z + CEIL, 0.6, 0.9, 'pend2')
plant(5.75, 3.7, z, 1.7)
# --- terrace / sunroom (x 0.2-5.2, y 0.2-3.0), glass roof
box('planter_L', 0.2, 0.2, z, 0.75, 3.0, z + 0.55, M['trav'])
box('planter_B', 0.75, 0.2, z, 5.2, 0.7, z + 0.55, M['trav'])
import random as _r
_g = _r.Random(3)
for k in range(260):
    if k % 2:
        px, py = 0.25 + _g.random() * 0.45, 0.3 + _g.random() * 2.6
    else:
        px, py = 0.8 + _g.random() * 4.3, 0.25 + _g.random() * 0.4
    o = sphere('shrub', px, py, z + 0.58 + _g.random() * 0.45, 0.06, M['plant'], 1.0, 0.4, 0.2)
    o.rotation_euler = (_g.random() * 3, _g.random() * 3, _g.random() * 3)
plant(4.8, 2.6, z, 2.0)
for o in lounge_chair(1.9, 1.9, 200, M['linen'], 'tlc1'):
    o.location.z += z
for o in lounge_chair(3.4, 1.9, 160, M['linen'], 'tlc2'):
    o.location.z += z
for o in coffee_round(2.65, 1.45, 0.3, z, h=0.42, name='tct'):
    pass
rug(1.2, 0.9, 4.2, 2.8, z, M['rug_taupe'], 'ter_rug')
# --- nanny room (x 1.8-5.2, y 3.2-5.5)
bed(2.45, 3.45, 1.2, 2.0, 'N', z, name='bed_nanny', hb_h=1.1)
box('ns_n', 1.85, 5.05, z, 2.3, 5.45, z + 0.5, M['oak'], 0.01)
joinery_wall(4.6, 4.25, 5.2, 5.5, z, z + 2.6, M['oak'], 'nanny_ward', panel=0.6)
curtain(3.05, 3.28, 4.45, 3.28, z + 0.85, z + 2.5, name='curt_nanny')
# --- nanny bath (x 0.2-1.6, y 3.2-5.5)
vanity(0.22, 4.6, 0.68, 5.3, z, top_m=M['trav'], name='nb_van')
mirror_panel(0.215, 4.7, 0.22, 5.2, z + 1.05, z + 1.95, 'nb_mir')
wc(1.0, 5.48, z, 'S', 'nbwc')
shower_glass(0.2, 4.15, 1.0, 4.16, z)
# --- kids room (x 8.1-10.9, y 4.5-7.9): pastel yellow + ivory wainscoting + natural oak
kz = z
KOPS = {'N': [(8.5, 10.2, 0.9, 2.4)], 'S': [(9.75, 10.65, 0.0, 2.3)]}
clad(8.1, 4.5, 10.9, 7.9, kz, 0.9, CEIL, M['yellow_wall'], KOPS, 'kid_wp')
clad(8.1, 4.5, 10.9, 7.9, kz, 0.0, 0.9, M['ivory_panel'], KOPS, 'kid_wains', t=0.03)
clad(8.08, 4.48, 10.92, 7.92, kz, 0.88, 0.93, M['ivory_panel'], KOPS, 'kid_rail', t=0.05)
# rounded single bed with arched upholstered headboard against west wall
box('kbed_frame', 8.15, 5.6, kz + 0.1, 10.15, 6.55, kz + 0.32, M['oak_light'], 0.06)
box('kbed_matt', 8.2, 5.63, kz + 0.32, 10.1, 6.52, kz + 0.52, M['linen_ivory'], 0.06)
box('kbed_duvet', 8.8, 5.58, kz + 0.48, 10.14, 6.57, kz + 0.58, M['yellow'], 0.06)
cyl('kbed_hb', 8.16, 6.075, kz + 0.1, kz + 1.25, 0.55, M['yellow'], bevel=0.05).scale = (0.12, 1, 1)
box('kbed_pillow', 8.25, 5.75, kz + 0.52, 8.6, 6.4, kz + 0.72, M['linen_ivory'], 0.07)
cyl('knight', 8.4, 5.2, kz, kz + 0.5, 0.22, M['oak_light'], bevel=0.04)
sphere('klamp', 8.4, 5.2, kz + 0.68, 0.14, M['lamp'])
joinery_wall(8.12, 7.3, 9.9, 7.86, kz, kz + 2.3, M['ivory_panel'], 'kward', panel=0.6)
cyl('krug', 9.7, 5.4, kz, kz + 0.012, 0.85, M['wool_rug'])
cyl('kpouf', 10.35, 7.05, kz, kz + 0.38, 0.28, M['yellow'], bevel=0.1)
for o in lounge_chair(10.2, 6.6, 120, M['boucle'], 'kchair'):
    o.location.z += kz
curtain(8.4, 7.8, 10.3, 7.8, kz + 0.02, kz + 2.95, M['yellow'], 'kcurt')
sphere('kpend', 9.5, 6.2, kz + CEIL - 0.6, 0.28, M['lamp'], 1, 1, 0.7)
# --- master vestibule (x 11.1-12.7, y 4.5-5.45): dressing niche
joinery_wall(11.12, 4.5, 11.55, 5.45, z, z + 2.4, M['oak'], 'vest_ward', panel=0.48)
# --- master bath (x 11.1-12.7, y 5.6-7.9)
vanity(12.2, 5.75, 12.68, 6.75, z, top_m=M['trav'], name='mb_van')
mirror_panel(12.68, 5.85, 12.685, 6.65, z + 1.05, z + 2.1, 'mb_mir')
wc(11.12, 6.35, z, 'E', 'mbwc')
shower_glass(11.1, 6.9, 12.2, 6.91, z)
box('mb_niche', 11.12, 7.1, z + 1.1, 11.14, 7.7, z + 1.45, M['led'])
box('mb_rain', 11.6, 7.35, z + 2.2, 11.9, 7.65, z + 2.21, M['bronze'])
# --- master bedroom (x 12.9-19.8, y 4.5-7.9)
bed(16.65, 5.8, 1.9, 2.1, 'N', z, name='mbed', hb_h=1.35)
box('mbed_panel', 15.9, 7.78, z, 19.3, 7.9, z + 2.4, M['linen'], 0.02)
box('mbed_panel_led', 15.9, 7.77, z + 2.4, 19.3, 7.9, z + 2.41, M['led'])
for nx in (16.05, 18.95):
    box('ns', nx - 0.3, 7.3, z + 0.25, nx + 0.3, 7.77, z + 0.62, M['oak'], 0.01)
    box('sconce', nx - 0.06, 7.76, z + 1.1, nx + 0.06, 7.78, z + 1.45, M['lamp'])
box('bench_foot', 16.85, 5.2, z, 18.35, 5.6, z + 0.45, M['boucle'], 0.05)
rug(15.9, 4.9, 19.3, 7.0, z, M['wool_rug'], 'mrug')
joinery_wall(12.92, 7.3, 15.4, 7.9, z, z + 2.6, M['oak'], 'm_ward_N', panel=0.62)
joinery_wall(12.92, 5.5, 13.5, 7.3, z, z + 2.6, M['oak'], 'm_ward_W', panel=0.6)
box('m_ward_top', 12.92, 5.5, z + 2.6, 15.4, 7.9, z + CEIL, M['wall'])
box('dress_tbl', 14.2, 4.52, z + 0.72, 15.4, 5.0, z + 0.76, M['oak'], 0.01)
mirror_panel(14.4, 4.515, 15.2, 4.52, z + 1.0, z + 2.0, 'dress_mir')
for o in lounge_chair(19.0, 4.95, 210, M['boucle'], 'mchair'):
    o.location.z += z
curtain(19.72, 4.55, 19.72, 7.85, z + 0.02, z + 2.95, name='curt_m')
cove(15.9, 5.0, 19.3, 7.4, z + CEIL, 25)
# --- office (x 12.9-19.8, y 0.2-4.3): library + desk facing door
joinery_wall(13.1, 0.2, 16.4, 0.6, z, z + CEIL - 0.05, M['walnut'], 'library', panel=0.8)
for sh in range(5):
    zz = z + 0.45 + sh * 0.48
    box('shelf_led', 13.2, 0.55, zz, 16.3, 0.6, zz + 0.005, M['led'])
    for k in range(10):
        bx = 13.3 + k * 0.3
        box('books', bx, 0.25, zz + 0.01, bx + 0.18, 0.5, zz + 0.3, M['linen'] if k % 2 else M['boucle'])
box('desk', 17.3, 1.3, z + 0.74, 18.3, 3.3, z + 0.78, M['walnut'], 0.01)
box('desk_ped', 17.4, 1.4, z, 18.2, 1.9, z + 0.74, M['walnut'], 0.01)
box('desk_leg', 17.75, 2.9, z, 17.85, 3.2, z + 0.74, M['bronze'])
box('desk_chair', 18.45, 2.05, z + 0.0, 18.95, 2.55, z + 0.5, M['boucle'], 0.08)
box('desk_chair_b', 18.85, 2.05, z + 0.5, 18.95, 2.55, z + 1.15, M['boucle'], 0.04)
box('guest_ch1', 16.55, 1.6, z, 17.0, 2.05, z + 0.45, M['linen'], 0.06)
box('guest_ch2', 16.55, 2.55, z, 17.0, 3.0, z + 0.45, M['linen'], 0.06)
for o in sofa(13.2, 2.4, 2.4, 0.95, 'S', name='sofa_off'):
    o.location.z += z
coffee_round(14.4, 1.6, 0.45, z)
rug(13.1, 0.9, 15.7, 3.3, z, M['rug_taupe'], 'orug')
curtain(19.72, 1.85, 19.72, 3.55, z + 0.02, z + 2.95, name='curt_off')
linear_pendant(17.4, 18.2, 2.3, z + CEIL, 0.9, 'off_lin')
art(12.905, 1.3, 12.92, 3.0, z + 1.1, z + 2.2) if False else None
# --- office bath (x 11.1-12.7, y 0.2-3.2)
vanity(11.12, 1.9, 11.58, 2.9, z, top_m=M['trav'], name='ob_van')
mirror_panel(11.115, 2.0, 11.12, 2.8, z + 1.05, z + 2.05, 'ob_mir')
wc(11.9, 0.22, z, 'N', 'obwc')
shower_glass(11.1, 1.45, 12.0, 1.46, z) if False else None

# general downlights / coves per space
for (x, y) in [(1.2, 1.2), (3.6, 1.2), (1.2, 4.2), (3.6, 4.2), (6.2, 2.2), (7.0, 3.6), (11.3, 1.2), (11.3, 3.3),
               (4.6, 6.4), (4.6, 7.4), (6.1, 5.2), (6.1, 7.2), (9.3, 6.4), (10.1, 6.4)]:
    downlight(x, y, CEIL)
for (x, y) in [(6.1, 1.0), (10.3, 3.7), (11.9, 3.85), (8.6, 7.1), (13.5, 3.7), (18.5, 0.9), (1.4, 4.5), (3.3, 4.5),
               (11.9, 7.2), (11.9, 6.1), (11.9, 2.4), (0.9, 4.6), (5.9, 7.4), (11.9, 4.95)]:
    downlight(x, y, L2Z + CEIL)
cove(0.5, 0.5, 4.8, 5.2, CEIL, 18)
cove(5.6, 0.5, 12.3, 4.0, CEIL, 14)
cove(5.6, 0.5, 10.7, 4.1, L2Z + CEIL, 16)
cove(13.1, 0.4, 19.6, 4.1, L2Z + CEIL, 14)
cove(8.3, 4.7, 10.7, 7.7, L2Z + CEIL, 14)

# ---------------------------------------------------------------- world, context outside
world = bpy.data.worlds.new('w')
scn.world = world
world.use_nodes = True
wn = world.node_tree.nodes
sky = wn.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(38)
sky.sun_rotation = math.radians(200)
sky.sun_intensity = 0.45
sky.air_density = 1.2
sky.dust_density = 2.5
world.node_tree.links.new(sky.outputs['Color'], wn['Background'].inputs['Color'])
wn['Background'].inputs['Strength'].default_value = 0.35
sun = bpy.data.lights.new('sun', 'SUN')
sun.energy = 3.2
sun.angle = math.radians(1.5)
sun.color = (1.0, 0.93, 0.84)
so = bpy.data.objects.new('sun', sun)
so.rotation_euler = Euler((math.radians(52), 0, math.radians(200)), 'XYZ')
col.objects.link(so)
box('ground', -60, -60, -3.6, 80, 70, -3.5, M['sky_ground'])
for (x0, y0, x1, y1, h) in [(-40, -38, -10, -22, 16), (-6, -34, 14, -24, 12), (18, -40, 40, -20, 20),
                            (-38, 0, -18, 10, 9), (30, -5, 45, 15, 14), (-10, 16, 10, 26, 11), (22, 14, 40, 30, 18)]:
    box('bldg', x0, y0, -3.5, x1, y1, h, M['building'])

# ---------------------------------------------------------------- render settings
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = int(os.environ.get('SAMPLES', '24'))
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 8
scn.cycles.diffuse_bounces = 4
scn.cycles.glossy_bounces = 4
scn.cycles.transmission_bounces = 8
scn.cycles.caustics_reflective = False
scn.cycles.caustics_refractive = False
scn.render.resolution_x = int(os.environ.get('RX', '1024'))
scn.render.resolution_y = int(os.environ.get('RY', '683'))
scn.view_settings.view_transform = 'AgX'
scn.view_settings.look = 'AgX - Base Contrast'
scn.view_settings.exposure = float(os.environ.get('EXPO', '-0.15'))
scn.render.image_settings.file_format = 'JPEG'
scn.render.image_settings.quality = 92

# ---------------------------------------------------------------- cameras
# (name, level_z, eye(x,y,h), target(x,y,h), lens_mm)
from views import VIEWS  # noqa


def render_view(name, zlev, eye, tgt, lens, out):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = 36
    cam.clip_start = 0.05
    co = bpy.data.objects.new(name, cam)
    col.objects.link(co)
    e = Vector((eye[0], eye[1], zlev + eye[2]))
    t = Vector((tgt[0], tgt[1], zlev + eye[2]))  # level target -> 2-point perspective
    d = t - e
    co.location = e
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    # vertical shift to frame target height without tilting verticals
    cam.shift_y = (tgt[2] - eye[2]) / max(1.0, d.length) * (lens / 36) * 0.9
    scn.camera = co
    scn.render.filepath = os.path.join(out, name + '.jpg')
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    out = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else sys.argv[1]
    want = sys.argv[sys.argv.index('--') + 2:] if '--' in sys.argv else sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    for v in VIEWS:
        if want and v[0] not in want:
            continue
        render_view(*v, out)
        print('RENDERED', v[0], flush=True)
