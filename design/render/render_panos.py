import bpy, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__name__': 'lib', '__file__': os.path.join(HERE, 'scene.py')}
exec(compile(open(os.path.join(HERE, 'scene.py')).read(), 'scene.py', 'exec'), g)
sys.path.insert(0, HERE)
from panos import NODES, EYE
args = sys.argv[sys.argv.index('--') + 1:]
out, want = args[0], args[1:]
os.makedirs(out, exist_ok=True)
scn = bpy.context.scene
scn.render.resolution_x = int(os.environ.get('PX', '4096'))
scn.render.resolution_y = scn.render.resolution_x // 2
scn.cycles.samples = int(os.environ.get('SAMPLES', '64'))
for (nid, z, x, y, title, links) in NODES:
    if want and nid not in want:
        continue
    cam = bpy.data.cameras.new(nid)
    cam.type = 'PANO'
    for holder in (cam, getattr(cam, 'cycles', None)):
        try:
            holder.panorama_type = 'EQUIRECTANGULAR'
        except Exception:
            pass
    cam.clip_start = 0.05
    co = bpy.data.objects.new('pano_' + nid, cam)
    scn.collection.objects.link(co)
    co.location = (x, y, z + EYE)
    co.rotation_euler = (math.radians(90), 0, 0)   # image centre looks toward +Y
    scn.camera = co
    scn.render.filepath = os.path.join(out, nid + '.jpg')
    bpy.ops.render.render(write_still=True)
    print('PANO', nid, flush=True)
