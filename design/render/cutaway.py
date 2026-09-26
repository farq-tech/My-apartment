"""Axonometric cutaway of each level (ceilings removed) from the same scene."""
import bpy, math, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'scene.py')).read()
g = {'__name__': 'scene_lib', '__file__': os.path.join(HERE, 'scene.py')}
exec(compile(src, 'scene.py', 'exec'), g)
out = sys.argv[sys.argv.index('--') + 1]
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y = 1600, 1000
base = {o.name: o for o in scn.objects}


def lowest_z(o):
    if o.type != 'MESH':
        return o.matrix_world.translation.z
    return min((o.matrix_world @ Vector(c)).z for c in o.bound_box)


for tag, cut, cx, cy, span in [('L01', 2.6, 6.35, 4.0, 14.5), ('L02', 3.5 + 2.6, 10.0, 4.0, 21.5)]:
    for o in scn.objects:
        if o.type in ('MESH', 'LIGHT') and not o.name.startswith(('ground', 'bldg')):
            o.hide_render = lowest_z(o) > cut or (tag == 'L01' and lowest_z(o) > 3.4)
    cam = bpy.data.cameras.new('ax' + tag)
    cam.type = 'ORTHO'
    cam.ortho_scale = span
    co = bpy.data.objects.new('ax' + tag, cam)
    scn.collection.objects.link(co)
    zc = 0 if tag == 'L01' else 3.5
    tgt = Vector((cx, cy, zc))
    co.location = tgt + Vector((-14, -18, 22))
    co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
    scn.camera = co
    scn.render.filepath = os.path.join(out, f'model_{tag}.jpg')
    bpy.ops.render.render(write_still=True)
    print('RENDERED', tag, flush=True)
