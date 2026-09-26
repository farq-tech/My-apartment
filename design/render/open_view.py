import bpy
def setup():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'MATERIAL'
                s.overlay.show_floor = False
                s.region_3d.view_perspective = 'CAMERA'
    return None
bpy.app.timers.register(setup, first_interval=1.0)
