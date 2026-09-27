"""Save the full duplex (both levels, furniture, materials, 40 cameras) as a .blend to browse."""
import bpy, math, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__name__': 'scene_lib', '__file__': os.path.join(HERE, 'scene.py')}
exec(compile(open(os.path.join(HERE, 'scene.py')).read(), 'scene.py', 'exec'), g)
scn = bpy.context.scene
cams = bpy.data.collections.new('Cameras (40 views)')
scn.collection.children.link(cams)
for (name, z, e, t, lens) in g['VIEWS']:
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = 36
    cam.clip_start = 0.05
    co = bpy.data.objects.new(name, cam)
    cams.objects.link(co)
    ev = Vector((e[0], e[1], z + e[2]))
    co.location = ev
    co.rotation_euler = (Vector((t[0], t[1], z + e[2])) - ev).to_track_quat('-Z', 'Y').to_euler()
    cam.shift_y = (t[2] - e[2]) / max(1.0, (Vector(t[:2]) - Vector(e[:2])).length) * (lens / 36) * 0.9
sys.path.insert(0, HERE)
from walk import add_walk
scn.camera = add_walk(scn)
for o in scn.objects:
    if o.name.startswith(('bldg', 'ground')):
        o.hide_viewport = True
for scr in bpy.data.screens:
    for a in scr.areas:
        if a.type == 'VIEW_3D':
            sp = a.spaces.active
            sp.shading.type = 'RENDERED'
            sp.overlay.show_floor = False
            sp.overlay.show_axis_x = False
            sp.overlay.show_axis_y = False
            sp.clip_start = 0.05
            sp.region_3d.view_perspective = 'CAMERA'
            sp.overlay.show_extras = False
            sp.overlay.show_relationship_lines = False
            sp.region_3d.view_camera_zoom = 29
            sp.region_3d.view_camera_offset = (0, 0)
eng = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
scn.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in eng else 'BLENDER_EEVEE'
try:
    scn.eevee.use_raytracing = True
    scn.eevee.use_shadows = True
except Exception:
    pass
bpy.ops.file.pack_all()
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('SAVED', out, flush=True)
