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
L2 = 3.5
# unit front door is on the upper level (top wall, x 5.45-6.45): enter, look into the lounge,
# then take the internal stair down to the first floor living and dining.
KEYS = [
    (1, 5.95, 8.9, L2, 180, 90),
    (40, 5.95, 7.4, L2, 180, 90),
    (90, 6.1, 4.9, L2, 180, 90),
    (120, 6.6, 3.6, L2, 215, 88),
    (150, 6.4, 3.4, L2, 140, 88),
    (185, 6.1, 4.8, L2, 0, 90),
    (230, 6.1, 7.2, L2, 20, 90),
    (255, 5.3, 7.45, L2, 90, 88),
    (275, 4.4, 7.35, L2, 90, 84),
    (355, 1.2, 7.35, run2_floor(1.2), 90, 84),
    (380, 0.62, 7.2, 11 * R, 180, 88),
    (400, 0.62, 6.35, 11 * R, 270, 86),
    (415, 1.05, 6.25, 11 * R, 270, 84),
    (495, 3.95, 6.25, run1_floor(3.95), 270, 86),
    (520, 4.6, 6.3, 0.0, 200, 90),
    (545, 4.6, 5.3, 0.0, 180, 90),
    (590, 4.6, 3.2, 0.0, 180, 90),
    (625, 4.9, 2.8, 0.0, 250, 90),
    (680, 7.4, 2.9, 0.0, 270, 90),
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
