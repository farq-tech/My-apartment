"""Unit geometry (metres), digitised from 4.dwg sheets FIRST FLOOR PLAN / ROOF FLOOR PLAN.

Origin = outer bottom-left corner of each sheet. Both levels share the same origin
(verified: identical stair 3.07 x 2.20 m at identical offsets). Level 02 floor = 3.50 m.
Assumptions (not in drawings): clear ceiling height 3.00 m, window sill 0.90 / head 2.40,
floor-to-floor 3.50 m (22 risers x 159 mm).
"""

CEIL = 3.00
L2Z = 3.50

# walls: (x0, y0, x1, y1, openings) ; opening = (a, b, z0, z1, kind) along the wall's long axis
# kind: 'door', 'window', 'open', 'glass'
L01_WALLS = [
    # exterior
    (0.0, 0.0, 12.7, 0.2, [(7.8, 10.3, 0.45, 2.55, 'window')]),
    (0.0, 0.2, 0.2, 8.08, [(2.2, 4.95, 0.45, 2.55, 'window')]),
    (0.0, 7.9, 11.2, 8.08, []),
    (11.0, 4.35, 11.2, 7.9, [(5.0, 6.2, 0.9, 2.4, 'window')]),
    (11.2, 4.12, 12.7, 4.35, []),
    (12.5, 0.2, 12.7, 4.12, []),
    # stair enclosure / hall
    (0.2, 5.5, 5.15, 5.7, [(4.15, 5.05, 0.0, 2.3, 'door')]),
    # guest WC
    (5.15, 3.9, 5.35, 7.9, []),
    (5.35, 4.2, 6.9, 4.45, [(5.6, 6.4, 0.0, 2.3, 'door')]),
    # service shaft (solid) between WC and kitchen
    (6.9, 4.2, 8.2, 7.9, []),
]
L01_COLUMNS = [(5.15, 1.3, 5.35, 1.85)]

L02_WALLS = [
    # exterior
    (0.0, 0.0, 20.0, 0.2, [(8.2, 10.6, 0.45, 2.55, 'window')]),
    (0.0, 0.2, 0.2, 8.08, []),
    (0.0, 7.9, 20.0, 8.08, [(5.45, 6.45, 0.0, 2.3, 'door'), (8.5, 10.2, 0.9, 2.4, 'window'),
                            (11.3, 12.1, 1.7, 2.3, 'window')]),
    (19.8, 0.2, 20.0, 7.9, [(1.95, 3.45, 0.6, 2.5, 'window'), (4.6, 6.0, 0.6, 2.5, 'window')]),
    # stair enclosure
    (0.2, 5.5, 5.2, 5.7, []),
    (5.2, 3.0, 5.35, 7.0, [(3.3, 4.2, 0.0, 2.3, 'door')]),
    # nanny room / bath / terrace
    (0.2, 3.0, 5.35, 3.2, [(3.1, 4.4, 0.9, 2.4, 'window')]),
    (1.6, 3.2, 1.8, 5.5, [(3.45, 4.2, 0.0, 2.3, 'door')]),
    (5.2, 0.2, 5.35, 3.0, [(0.8, 2.2, 0.0, 2.6, 'glass')]),
    # corridor right wall + shaft (solid) + kids left wall
    (6.85, 4.3, 8.1, 7.9, []),
    # kids room bottom wall (living top wall)
    (8.1, 4.3, 10.9, 4.5, [(9.75, 10.65, 0.0, 2.3, 'door')]),
    (10.9, 4.3, 11.1, 7.9, []),
    # master vestibule + bath
    (10.9, 4.3, 12.9, 4.5, [(11.3, 12.2, 0.0, 2.3, 'door')]),
    (11.1, 5.45, 12.7, 5.6, [(11.45, 12.2, 0.0, 2.3, 'door')]),
    (12.7, 4.5, 12.9, 7.9, [(4.55, 5.4, 0.0, 2.3, 'door')]),
    (12.9, 4.3, 19.8, 4.5, [(17.2, 18.4, 0.0, 2.4, 'open')]),
    # new partition on the column line: child room (west) / master dressing-sitting (east)
    (16.55, 0.2, 16.75, 4.3, []),
    # office bath + office
    (10.9, 0.2, 11.1, 3.2, []),
    (10.9, 3.2, 12.9, 3.4, [(11.8, 12.6, 0.0, 2.3, 'door')]),
    (12.7, 0.2, 12.9, 3.2, []),
    (12.7, 3.4, 12.9, 4.3, [(3.45, 4.25, 0.0, 2.3, 'door')]),
]

# stair (both levels): bottom run y 5.7-6.8 rising from x 4.1 to 1.05, landing x 0.2-1.05,
# top run y 6.8-7.9 rising from x 1.05 to 4.1, arrival on L02 at x 4.1-5.2.
STAIR = dict(x_low=1.05, x_high=4.1, y_run1=(5.7, 6.8), y_run2=(6.8, 7.9), landing_x=(0.2, 1.05),
             treads=10, risers=22)
# void in L02 slab above the stair
L02_VOID = (0.2, 5.7, 4.1, 7.9)
