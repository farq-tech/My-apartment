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
scn.camera = bpy.data.objects['F1-02_Living_V2']
bpy.ops.file.pack_all()
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('SAVED', out, flush=True)
