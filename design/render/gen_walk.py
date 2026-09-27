"""Build the walkthrough page: renders in walking order with a live plan marker."""
import json, math, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geometry import L01_WALLS, L02_WALLS, L01_COLUMNS  # noqa
from views import VIEWS  # noqa

OUT = os.path.join(HERE, '..', 'renders', 'walk-page')
IMG = os.path.join(OUT, 'img')
FINAL = os.path.join(HERE, '..', 'renders', 'final')
FACADE = os.path.join(HERE, '..', 'facade')

LABEL = {
    'Entrance': 'المدخل', 'FamilyLounge': 'الصالة العائلية', 'Terrace': 'المشتل', 'GuestRoom': 'غرفة الضيوف',
    'GuestBath': 'حمام الضيوف', 'Office': 'المكتب', 'MasterBedroom': 'غرفة الماستر', 'MasterBath': 'حمام الماستر',
    'MasterDressing': 'غرفة الملابس والجلسة', 'ChildBedroom': 'غرفة الطفل', 'ChildBath': 'حمام الطفل',
    'Staircase': 'الدرج', 'StairHall': 'بهو الدرج', 'Living': 'المعيشة', 'Dining': 'الطعام', 'Kitchen': 'المطبخ',
    'GuestWC': 'دورة مياه الضيوف',
}
# walking order: in through the unit door on the second floor, round the second floor, down the stair
ORDER = ['F2-01_Entrance', 'F2-02_FamilyLounge', 'F2-03_Terrace', 'F2-09_GuestRoom', 'F2-10_GuestBath',
         'F2-07_Office', 'F2-04_MasterBedroom', 'F2-04b_MasterBath', 'F2-05_MasterDressing', 'F2-06_ChildBedroom',
         'F2-08_ChildBath', 'F1-05_Staircase', 'F1-01_StairHall', 'F1-02_Living', 'F1-03_Dining', 'F1-04_Kitchen',
         'F1-06_GuestWC']

os.makedirs(IMG, exist_ok=True)
stops = []
vmap = {v[0]: v for v in VIEWS}
for key in ORDER:
    names = sorted(n for n in vmap if n.startswith(key + '_V'))
    if key == 'F1-05_Staircase':
        names = sorted(names, reverse=True)  # from the top down
    for n in names:
        _, z, e, t, lens = vmap[n]
        room = key.split('_', 1)[1]
        floor = 2 if z > 1 else 1
        if n == 'F1-05_Staircase_V3':
            floor = 2
        shutil.copy(os.path.join(FINAL, n + '.jpg'), os.path.join(IMG, n + '.jpg'))
        stops.append(dict(img=f'img/{n}.jpg', floor=floor, room=LABEL.get(room, room),
                          view=n.rsplit('_V', 1)[1], x=e[0], y=e[1], tx=t[0], ty=t[1],
                          fov=round(math.degrees(2 * math.atan(18 / lens)), 1)))
for f, lab in [('A_current.jpg', 'الواجهة الحالية'), ('B_no_granite.jpg', 'واجهة B بدون جرانيت'),
               ('C_budget_paint.jpg', 'واجهة C اقتصادية')]:
    shutil.copy(os.path.join(FACADE, f), os.path.join(IMG, 'facade_' + f))
    stops.append(dict(img='img/facade_' + f, floor=0, room=lab, view='', x=0, y=0, tx=0, ty=0, fov=0))


def walls(ws, extra=()):
    out = []
    for (x0, y0, x1, y1, ops) in ws:
        horiz = (x1 - x0) >= (y1 - y0)
        cur = x0 if horiz else y0
        end = x1 if horiz else y1
        segs, wins = [], []
        for (a, b, z0, z1, k) in sorted(ops):
            segs.append((cur, a)); cur = b
            if k in ('window', 'glass'):
                wins.append((a, b))
        segs.append((cur, end))
        for p, q in segs:
            if q > p:
                out.append(('w', *( (p, y0, q - p, y1 - y0) if horiz else (x0, p, x1 - x0, q - p))))
        for p, q in wins:
            out.append(('g', *((p, y0, q - p, y1 - y0) if horiz else (x0, p, x1 - x0, q - p))))
    for c in extra:
        out.append(('w', c[0], c[1], c[2] - c[0], c[3] - c[1]))
    return [[k, round(a, 3), round(b, 3), round(c, 3), round(d, 3)] for (k, a, b, c, d) in out]


plans = {1: dict(w=12.7, rects=walls(L01_WALLS, L01_COLUMNS)), 2: dict(w=20.0, rects=walls(L02_WALLS))}

html = open(os.path.join(HERE, 'walk_template.html')).read()
html = html.replace('/*STOPS*/', json.dumps(stops, ensure_ascii=False)).replace('/*PLANS*/', json.dumps(plans))
open(os.path.join(OUT, 'index.html'), 'w').write(html)
print(len(stops), 'stops')
