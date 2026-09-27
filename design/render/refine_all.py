"""Refine every base render into a photoreal image, keeping geometry. Skips views already done.
usage: python3 refine_all.py BASE_DIR OUT_DIR
"""
import os, sys, time, subprocess

BASE = ('Turn this 3D render into an ultra photorealistic architectural interior photograph of a finished Riyadh apartment. '
        'Keep the exact room geometry, camera angle, walls, doors, windows, ceiling and every furniture piece exactly as in the render: '
        'do not add, remove, replace or move anything; only make materials, light and textures photographic. '
        'Windows stay flush windows with a solid wall below the sill: no balconies, no railings, no sliding doors, no city towers outside. '
        'Keep the floor exactly as it is: light warm grey marble-look 120x60 ceramic tiles with soft subtle veining and thin joints, satin finish. '
        'Matte painted walls in warm mushroom taupe exactly as in the render, smoked oak joinery, satin bronze details, bright soft natural daylight, '
        'realistic shadows and reflections, calm quiet-luxury styling, high-end interior photography. ')

ROOM = {
    'StairHall': 'Stair hall with smoked oak bench and linen artwork, view into the living room.',
    'Living': 'Living room: ivory boucle sofa and lounge chairs, travertine-top round coffee tables on oak bases, '
              'smoked oak TV wall joinery, wool rug, sheer linen curtains, ring pendant, potted olive tree.',
    'Dining': 'Dining area: smoked oak dining table with upholstered taupe linen chairs, linear bronze pendant, '
              'oak sideboard with travertine top, sheer curtains, potted olive tree.',
    'Kitchen': 'Kitchen: smoked oak flat-panel cabinets, warm white stone countertop and backsplash, oak island with '
               'stone top, linen bar stools, glass globe pendants, integrated appliances.',
    'Staircase': 'Staircase clad in the same light warm grey marble-look floor tiles, frameless glass balustrade with smoked oak '
                 'handrail, warm LED light.',
    'GuestWC': 'Guest bathroom with floors and walls fully clad in the exact same travertine vein-cut tiles '
               '(keep the travertine pattern), floating smoked oak vanity with travertine top, backlit mirror, '
               'wall-hung toilet, brushed bronze fittings.',
    'Entrance': 'Entrance corridor with smoked oak built-in shoe cabinet, boucle bench, rug, downlights.',
    'FamilyLounge': 'Family lounge: ivory boucle sofa, round travertine coffee table, oak media wall with TV, '
                    'wool rug, sheer curtains, glass door to a planted sunroom, potted olive tree.',
    'Terrace': 'Glass greenhouse sitting room: pitched clear glass roof on slim black steel frames, lush vertical green wall, '
               'hanging trailing plants in ceramic pots, travertine planters with shrubs, olive trees, ivory linen sofa, two '
               'lounge chairs, round oak coffee table, warm string lights along the ridge, bright natural daylight from above.',
    'MasterBedroom': 'Master bedroom: bed with tall upholstered taupe linen headboard wall with hidden warm light, '
                     'ivory linen bedding, oak nightstands, wall sconces, boucle bench, smoked oak wardrobes, '
                     'dressing table with mirror, sheer curtains, wool rug.',
    'MasterBath': 'Master bathroom with floors and walls fully clad in the exact same travertine vein-cut tiles '
                  '(keep the travertine pattern), floating vanity with travertine top and white basin, bronze '
                  'framed mirror, wall-hung toilet, frameless glass shower, lit shower niche, brushed bronze fittings.',
    'ChildBedroom': 'Baby girl bedroom in soft pastel yellow and warm ivory: soft yellow vertical-panel wainscoting with a hidden '
                    'warm LED strip on top, ivory wallpaper with small yellow rainbow and cloud motifs, cream daybed with a '
                    'cloud-shaped upholstered headboard, yellow throw and cushions, light oak nightstand with a mushroom lamp, '
                    'low light oak cubby shelf with yellow and cream baskets, floating oak shelf with frames, yellow curtains with '
                    'white sheer, cream rug with pastel yellow dots, tray ceiling with cove light, calm premium feeling.',
    'Office': 'Home office: walnut library wall with lit shelves and books, walnut desk under the window, boucle desk '
              'chair, linen lounge chair, wool rug, sheer curtains.',
    'MasterDressing': 'Master dressing and sitting area: full-height smoked oak wardrobes, oak dressing island with '
                      'travertine top, full-length mirror, boucle lounge chair by the window, sheer curtains, wool rug.',
    'ChildBath': 'Bathroom with floors and walls fully clad in the exact same travertine vein-cut tiles (keep the '
                 'travertine pattern), floating vanity with travertine top, mirror, wall-hung toilet, bronze fittings.',
    'OfficeBath': 'Bathroom with floors and walls fully clad in the exact same travertine vein-cut tiles (keep the '
                  'travertine pattern), floating vanity with travertine top, mirror, wall-hung toilet, bronze fittings.',
    'GuestRoom': 'Compact guest bedroom: single bed with taupe linen headboard, oak nightstand, oak wardrobe, '
                 'sheer curtain on the window to the sunroom.',
    'GuestBath': 'Small bathroom with floors and walls fully clad in the exact same travertine vein-cut tiles '
                 '(keep the travertine pattern), compact vanity, mirror, wall-hung toilet, glass shower screen.',
}


def prompt_for(name):
    room = name.split('_')[1]
    return BASE + ROOM.get(room, '')


if __name__ == '__main__':
    base, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    for f in (sorted(os.listdir(base)) if os.path.isdir(base) else []):
        if not f.endswith('.jpg'):
            continue
        dst = os.path.join(out, f)
        if os.path.exists(dst):
            continue
        for attempt in range(2):
            r = subprocess.run([sys.executable, os.path.join(here, 'refine.py'), os.path.join(base, f), dst,
                                prompt_for(f[:-4]), '11'], capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                print('done', f, flush=True)
                break
            print('fail', f, r.stderr[-400:], flush=True)
            time.sleep(5)
