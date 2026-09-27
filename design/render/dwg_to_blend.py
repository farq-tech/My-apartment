"""Build a .blend from the geometry extracted out of 4.dwg (one mesh of edges per DWG layer + text objects).
usage: blender -b --python dwg_to_blend.py -- plan.json out.blend"""
import bpy, json, sys, math
from mathutils import Quaternion

src, out = sys.argv[sys.argv.index('--') + 1:][:2]
D = json.load(open(src))
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'
OX, OY = -280.0, -345.0          # shift so the drawing sheets start near the origin (units: metres)
LIM = 700.0                      # anything farther than this after the shift is a stray object


def inside(p):
    return -LIM < p[0] - OX < LIM and -LIM < p[1] - OY < LIM


root = bpy.data.collections.new('4.dwg')
scn.collection.children.link(root)
lay_col = bpy.data.collections.new('Layers')
root.children.link(lay_col)
stray_col = bpy.data.collections.new('Far away objects (hidden)')
root.children.link(stray_col)
for name, polys in sorted(D['layers'].items()):
    for tag, keep, col in (('', True, lay_col), (' (far)', False, stray_col)):
        verts, edges = [], []
        for pl in polys:
            if all(inside(p) for p in pl) != keep:
                continue
            base = len(verts)
            verts += [(p[0] - OX, p[1] - OY, 0.0) for p in pl]
            edges += [(base + i, base + i + 1) for i in range(len(pl) - 1)]
        if not verts:
            continue
        me = bpy.data.meshes.new(name + tag)
        me.from_pydata(verts, edges, [])
        me.update()
        o = bpy.data.objects.new(name + tag, me)
        c = D['colors'].get(name, [255, 255, 255])
        o.color = (max(0.35, c[0] / 255), max(0.35, c[1] / 255), max(0.35, c[2] / 255), 1)
        col.objects.link(o)
stray_col.hide_viewport = True
stray_col.hide_render = True
txt_col = bpy.data.collections.new('Text')
root.children.link(txt_col)
for t in D['texts']:
    if not inside((t['x'], t['y'])) or not t['s'].strip():
        continue
    cu = bpy.data.curves.new('txt', 'FONT')
    cu.body = t['s'][:200]
    cu.size = max(0.02, t['h'])
    o = bpy.data.objects.new('txt ' + t['s'][:30], cu)
    o.location = (t['x'] - OX, t['y'] - OY, 0.0)
    o.rotation_euler = (0, 0, math.radians(t['r']))
    o.color = (1, 1, 1, 1)
    txt_col.objects.link(o)
# open in top orthographic view, lines coloured by layer, dark background
for scr in bpy.data.screens:
    for a in scr.areas:
        if a.type == 'VIEW_3D':
            sp = a.spaces.active
            sp.shading.type = 'WIREFRAME'
            sp.shading.wireframe_color_type = 'OBJECT'
            sp.shading.background_type = 'VIEWPORT'
            sp.shading.background_color = (0.08, 0.08, 0.09)
            sp.overlay.wireframe_opacity = 1.0
            sp.overlay.show_floor = False
            sp.overlay.show_axis_x = False
            sp.overlay.show_axis_y = False
            sp.clip_end = 5000
            sp.region_3d.view_perspective = 'CAMERA'
            sp.region_3d.view_camera_zoom = 0
cam = bpy.data.cameras.new('Top view')
cam.type = 'ORTHO'
cam.ortho_scale = 480
cam.clip_end = 5000
co = bpy.data.objects.new('Top view', cam)
co.location = (85.0, 231.0, 500.0)
root.objects.link(co)
scn.camera = co
scn.render.resolution_x, scn.render.resolution_y = 1200, 1600
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('SAVED', out, flush=True)
