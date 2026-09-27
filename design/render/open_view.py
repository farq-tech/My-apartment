import bpy
def setup():
    scn = bpy.context.scene
    scn.camera = bpy.data.objects['F1-02_Living_V2']
    scn.frame_set(1)
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'RENDERED'
                s.overlay.show_overlays = False
                s.clip_start = 0.05
                s.region_3d.view_perspective = 'CAMERA'
                s.region_3d.view_camera_zoom = 29
                s.region_3d.view_camera_offset = (0, 0)
    return None
bpy.app.timers.register(setup, first_interval=2.0)
