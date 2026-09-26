import bpy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__name__': 'lib', '__file__': os.path.join(HERE, 'scene.py')}
exec(compile(open(os.path.join(HERE, 'scene.py')).read(), 'scene.py', 'exec'), g)
sys.path.insert(0, HERE)
from walk import add_walk
scn = bpy.context.scene
for o in scn.objects:
    if o.name.startswith(('bldg',)):
        o.hide_render = True
scn.camera = add_walk(scn)
scn.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scn.render.resolution_x, scn.render.resolution_y = 1280, 720
try:
    scn.eevee.use_raytracing = True
    scn.eevee.taa_render_samples = 32
except Exception:
    pass
if hasattr(scn.render.image_settings, 'media_type'):
    scn.render.image_settings.media_type = 'VIDEO'
scn.render.image_settings.file_format = 'FFMPEG'
scn.render.ffmpeg.format = 'MPEG4'
scn.render.ffmpeg.codec = 'H264'
scn.render.ffmpeg.constant_rate_factor = 'HIGH'
scn.render.filepath = sys.argv[sys.argv.index('--') + 1]
print('ENGINE', scn.render.engine, flush=True)
fr = os.environ.get('FRAMES')
if fr:
    scn.render.image_settings.file_format = 'JPEG'
    base = scn.render.filepath
    for f in fr.split(','):
        scn.frame_set(int(f))
        scn.render.filepath = f'{base}_{int(f):03d}.jpg'
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print('WALK_DONE', flush=True)
