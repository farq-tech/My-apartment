"""Floor plan keys with camera positions for the album."""
import math, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geometry import L01_WALLS, L02_WALLS, L01_COLUMNS
from views import VIEWS

def draw(walls, level_z, out, width, extra=()):
    fig, ax = plt.subplots(figsize=(width * 0.62, 8.1 * 0.62))
    for (x0, y0, x1, y1, ops) in walls:
        horiz = (x1 - x0) >= (y1 - y0)
        segs, cur = [], (x0 if horiz else y0)
        end = x1 if horiz else y1
        for (a, b, z0, z1, k) in sorted(ops):
            segs.append((cur, a)); cur = b
            if k in ('window', 'glass'):
                if horiz: ax.add_patch(plt.Rectangle((a, y0 + (y1 - y0) * 0.35), b - a, (y1 - y0) * 0.3, color='#9CB4C0'))
                else: ax.add_patch(plt.Rectangle((x0 + (x1 - x0) * 0.35, a), (x1 - x0) * 0.3, b - a, color='#9CB4C0'))
        segs.append((cur, end))
        for (p, q) in segs:
            if q - p <= 0: continue
            if horiz: ax.add_patch(plt.Rectangle((p, y0), q - p, y1 - y0, color='#3B342D'))
            else: ax.add_patch(plt.Rectangle((x0, p), x1 - x0, q - p, color='#3B342D'))
    for c in extra:
        ax.add_patch(plt.Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], color='#3B342D'))
    for i in range(10):
        x = 4.1 - (i + 1) * 0.305
        ax.plot([x, x], [5.7, 6.8], color='#A89A88', lw=0.6); ax.plot([1.05 + i * 0.305] * 2, [6.8, 7.9], color='#A89A88', lw=0.6)
    for (name, z, e, t, lens) in VIEWS:
        if abs(z - level_z) > 0.01 or 'Staircase_V3' in name and level_z == 0: continue
        dx, dy = t[0] - e[0], t[1] - e[1]; L = math.hypot(dx, dy) or 1
        ax.annotate('', xy=(e[0] + dx / L * 0.8, e[1] + dy / L * 0.8), xytext=(e[0], e[1]),
                    arrowprops=dict(arrowstyle='-|>', color='#8A5A2B', lw=1.4))
        ax.plot(e[0], e[1], 'o', color='#8A5A2B', ms=4)
        tag = name.split('_')[0].split('-')[1] + '.' + name.split('_V')[1]
        ax.text(e[0] - dx / L * 0.25, e[1] - dy / L * 0.25, tag, fontsize=7, color='#5B3A1B', ha='center', va='center')
    ax.set_xlim(-0.3, width + 0.3); ax.set_ylim(-0.3, 8.4); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')

out = sys.argv[1]
draw(L01_WALLS, 0.0, out + '/key_F1.png', 12.7, extra=L01_COLUMNS)
draw(L02_WALLS, 3.5, out + '/key_F2.png', 20.0)
