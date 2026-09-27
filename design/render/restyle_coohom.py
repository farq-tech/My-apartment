"""Restyle the interior designer's Coohom views to the owner's approved palette (one Kontext pass each)."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'coohom', 'views'); OUT = os.path.join(HERE, '..', 'coohom', 'restyled')
KEEP = ('Keep the exact architecture, camera, ceiling design with its gypsum bulkheads and linear lights, walls, doors, windows, '
        'built-in joinery positions and furniture layout. ')
MAT = ('Floor: light grey 60x120 porcelain tiles, near-plain with very soft veining and thin grey joints. Walls: warm greige paint. '
       'All wood: medium natural oak. Replace any black or dark marble with warm greige stone. Textiles in camel, taupe and mushroom '
       'with olive and terracotta accents; rugs beige and taupe with a subtle Sadu geometric pattern. Very little white. ')
END = 'Bright natural daylight, warm, practical, refined contemporary Saudi home, ultra photorealistic interior photograph.'
BATH = ('Keep the exact bathroom layout, camera and fixtures. Clad the floor and all walls in light warm grey-beige travertine '
        'vein-cut tiles with long vertical linear veins, 60x120, matte. Vanity in medium natural oak, brushed brass taps and fittings, '
        'warm backlit mirror. Photorealistic high-end bathroom photograph.')
ROOM = {
 'Living': 'Main sofa in camel performance velvet, the two round lounge chairs in terracotta boucle, rug beige with subtle Sadu pattern.',
 'Dining': 'Dining chairs in taupe and olive velvet, oak dining table, warm brass pendant.',
 'Kitchen': 'Kitchen cabinets in medium oak and warm greige, light stone counters.',
 'Lounge': 'Modular sofa in mushroom taupe performance fabric instead of green, terracotta pouf, rug beige with subtle Sadu pattern.',
 'Greenhouse': 'Keep the greenhouse glass and plants.',
 'Entrance': 'Warm greige textured plaster walls and medium oak panels.',
 'Corridor': 'Warm greige walls, oak doors, a framed earthy artwork.',
 'Master': 'Replace the navy walls with warm greige, bedding in sand and oatmeal with a camel throw instead of orange, dusty rose and olive cushions.',
 'Dressing': 'Wardrobes in medium oak with bronze glass, warm greige walls.',
 'GuestBed': 'Headboard in camel linen, bedding sand and olive.',
 'KidsRoom': 'Child room: replace the pink with warm greige walls and soft mustard yellow accents, keep the cloud headboard in oatmeal, oak furniture.',
 'Office': 'Lighter office: medium oak shelving and desk, warm greige walls instead of black, sofa in olive, rug beige.',
}

def job(f):
    name = f[:-4]; key = name.split('-')[1].split('_')[0]
    dst = os.path.join(OUT, f)
    if os.path.exists(dst): return
    if 'Bath' in key: prompt = BATH
    else: prompt = KEEP + MAT + ROOM.get(key, '') + ' ' + END
    env = dict(os.environ, GUIDE='3.5')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'refine.py'), os.path.join(SRC, f), dst, prompt, '5'],
                       capture_output=True, text=True, env=env, timeout=600)
    print('ok' if r.returncode == 0 else 'FAIL ' + r.stderr[-200:], f, flush=True)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex: list(ex.map(job, sys.argv[1:] or sorted(os.listdir(SRC))))
