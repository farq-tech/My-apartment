"""Apply the B+C design constitution to every final view (one Kontext pass each)."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'renders', 'final'); OUT = os.path.join(HERE, '..', 'renders', 'bc')
KEEP = ('Keep the exact room geometry, camera angle, walls, doors, ceiling, floor tiles and window sizes; windows stay windows, '
        'no balconies, no railings, no new doors, no text on walls. Outside: beige flat-roofed Riyadh villas, no towers. ')
STYLE = ('Restyle as soft modern with a modern Saudi touch: warm white limewash walls, pale limed oak only (no dark brown wood), '
         'ivory linen and boucle, honed travertine, brushed brass, lit arched niches, a subtle Najdi triangular relief band. ')
END = 'Calm, refined, ultra photorealistic editorial interior photograph.'
ROOM = {
 'StairHall': 'Add an arched lit niche with a slim limed oak console, a ceramic vase and a linen artwork.',
 'Living': 'Ivory plaster TV wall with the TV recessed, arched lit niches each side, oat linen sofa, boucle armchair, cane chair, travertine coffee table, wool rug with a rust border, paper lantern pendant.',
 'Dining': 'Limed oak dining table, oat linen upholstered chairs, two paper lantern pendants, an arched niche sideboard with ceramics.',
 'Kitchen': 'Kitchen with pale limed oak lower cabinets and warm white flat upper cabinets, honed travertine countertops and backsplash, limed oak island with travertine top, cane bar stools, brass handles.',
 'Staircase': 'Stair with slim brass handrail on glass, a runner-lit wall with an arched niche and a large linen artwork, wall sconces.',
 'GuestWC': 'Bathroom: travertine only on the floor and the vanity wall, other walls warm white tadelakt plaster, floating limed oak vanity with travertine top, arched backlit mirror, brass tap and sconces.',
 'Entrance': 'Entrance with a limed oak bench and shoe cabinet, an arched lit niche with a ceramic piece, a woven runner, linen artwork, wall sconces.',
 'FamilyLounge': 'Family lounge: sage linen sofa, butter yellow and rust cushions, ivory boucle armchair, travertine coffee table, wool rug, paper lantern pendant, glass wall to the greenhouse stays.',
 'MasterBedroom': 'Master bedroom: upholstered oat linen headboard wall framed by a plaster arch with hidden light, ivory bedding with dusty blush throw and cushions, limed oak nightstands, brass sconces, blush boucle bench, sheer linen curtains, wool rug.',
 'MasterBath': 'Master bathroom: travertine only on the floor and in the shower and vanity wall, other walls warm white tadelakt, floating limed oak double vanity with travertine top, arched backlit mirrors, brass fittings, lit niche, frameless glass shower.',
 'MasterDressing': 'Dressing and sitting area, no bed: limed oak wardrobes with fluted glass doors, travertine-top island, full-length arched mirror, blush boucle lounge chair by the window.',
 'ChildBedroom': 'Child bedroom in off-white and pale oak with butter yellow only as accent: an arched butter yellow headboard niche with soft light, cream bed, yellow cushion bench, pale oak shelves, cream rug, sheer curtains. Not a themed nursery.',
 'Office': 'Light home office: pale limed oak desk under the window, ivory built-in shelving with arched lit niches, sage boucle chair, linen curtains, wool rug.',
 'ChildBath': 'Bathroom: travertine only on the floor and the vanity wall, other walls warm white tadelakt, floating limed oak vanity with travertine top, arched mirror, brass fittings, butter yellow towels.',
 'GuestRoom': 'Guest bedroom: oat linen headboard, limed oak nightstand and wardrobe, sage throw, paper lamp, sheer curtain.',
 'GuestBath': 'Bathroom: travertine only on the floor and the shower wall, other walls warm white tadelakt, compact limed oak vanity, arched mirror, brass fittings, glass shower screen.',
}
SKIP = ('F2-03_Terrace', 'F2-05_MasterBath', 'F2-08_OfficeBath')

def job(f):
    name = f[:-4]; room = name.split('_')[1]
    dst = os.path.join(OUT, f)
    if os.path.exists(dst) or name.startswith(SKIP) or room not in ROOM:
        return
    env = dict(os.environ, GUIDE='4')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'refine.py'), os.path.join(SRC, f), dst,
                        KEEP + STYLE + ROOM[room] + ' ' + END, '5'], capture_output=True, text=True, env=env, timeout=600)
    print('ok' if r.returncode == 0 else 'FAIL ' + r.stderr[-200:], f, flush=True)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    files = sys.argv[1:] or sorted(os.listdir(SRC))
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(job, files))
