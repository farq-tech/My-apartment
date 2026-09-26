"""Animated walkthrough camera: L01 living -> stair door -> both stair runs -> L02 corridor -> family lounge.
Coordinates follow geometry.py; eye height 1.6 m above the floor or tread under the camera."""
import bpy, math

R = 3.5 / 22            # riser
T = (4.1 - 1.05) / 10   # tread


def run1_floor(x):      # run 1 rises from x=4.1 (floor) toward x=1.05
    return min(11 * R, max(0.0, (4.1 - x) / T * R))


def run2_floor(x):      # run 2 rises from x=1.05 (landing) toward x=4.1 (L02 floor)
    return 11 * R + min(11 * R, max(0.0, (x - 1.05) / T * R))


EYE = 1.6
# (frame, x, y, floor_z, yaw_deg, pitch_deg)   yaw 0 = +Y, 90 = -X, 180 = -Y, 270 = +X
KEYS = [
    (1, 4.6, 2.6, 0.0, 0, 90),
    (45, 4.6, 5.0, 0.0, 0, 90),
    (80, 4.6, 6.25, 0.0, 60, 92),
    (100, 4.1, 6.25, 0.0, 90, 98),
    (180, 1.2, 6.25, run1_floor(1.2), 90, 98),
    (205, 0.62, 6.5, 11 * R, 160, 92),
    (230, 0.62, 7.3, 11 * R, 270, 96),
    (245, 1.05, 7.35, 11 * R, 270, 98),
    (330, 3.95, 7.35, run2_floor(3.95), 270, 96),
    (355, 4.7, 7.42, 3.5, 270, 90),
    (385, 6.1, 7.45, 3.5, 225, 90),
    (405, 6.1, 7.0, 3.5, 180, 90),
    (470, 6.1, 4.2, 3.5, 180, 90),
    (510, 6.5, 3.1, 3.5, 215, 88),
    (560, 6.9, 2.5, 3.5, 235, 88),
]


def add_walk(scene, name='Walkthrough'):
    cam = bpy.data.cameras.new(name)
    cam.lens = 16
    cam.sensor_width = 36
    cam.clip_start = 0.05
    co = bpy.data.objects.new(name, cam)
    scene.collection.objects.link(co)
    co.rotation_mode = 'XYZ'
    for (f, x, y, fz, yaw, pitch) in KEYS:
        co.location = (x, y, fz + EYE)
        co.rotation_euler = (math.radians(pitch), 0.0, math.radians(yaw))
        co.keyframe_insert('location', frame=f)
        co.keyframe_insert('rotation_euler', frame=f)
    scene.frame_start = 1
    scene.frame_end = KEYS[-1][0]
    scene.render.fps = 30
    return co
