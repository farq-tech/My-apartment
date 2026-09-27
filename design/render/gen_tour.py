"""Build the 360 tour page (Pannellum) from design/renders/tour/pano/*.jpg and panos.NODES."""
import json, math, os
from panos import NODES, EYE

HERE = os.path.dirname(os.path.abspath(__file__))
TOUR = os.path.join(HERE, '..', 'renders', 'tour')
css = open(os.path.join(TOUR, 'pannellum.css')).read()
byid = {n[0]: n for n in NODES}
have = {f[:-4] for f in os.listdir(os.path.join(TOUR, 'pano')) if f.endswith('.jpg')}

scenes = {}
for (nid, z, x, y, title, links) in NODES:
    if nid not in have:
        continue
    spots = []
    for l in links:
        if l not in have:
            continue
        _, z2, x2, y2, t2, _ = byid[l]
        dx, dy, dz = x2 - x, y2 - y, z2 - z
        yaw = math.degrees(math.atan2(dx, dy))
        pitch = math.degrees(math.atan2(dz, max(0.5, math.hypot(dx, dy)))) - 12
        spots.append(dict(pitch=round(pitch, 1), yaw=round(yaw, 1), type='scene', text=t2, sceneId=l))
    scenes[nid] = dict(title=title, type='equirectangular', panorama=f'pano/{nid}.jpg', hotSpots=spots,
                       hfov=100, autoLoad=True)

floors = [('الدور الثاني', [n for n in NODES if n[1] > 1 and n[0] in have]),
          ('الدور الأول', [n for n in NODES if n[1] < 1 and n[0] in have])]
menu = ''.join(f'<div class="grp"><span>{f}</span>' + ''.join(
    f'<button data-s="{n[0]}">{n[4]}</button>' for n in ns) + '</div>' for f, ns in floors)
cfg = dict(default=dict(firstScene='E1' if 'E1' in have else next(iter(scenes)), sceneFadeDuration=600,
                        autoLoad=True, showControls=True, compass=False), scenes=scenes)

page = f'''<title>جولة الشقة 360</title>
<style>{css}</style>
<style>
:root{{--bg:#151412;--ink:#F1ECE4;--muted:#B8AC9C;--accent:#D6B98C;--chip:#2A2724;color-scheme:dark}}
html,body{{height:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans Arabic",system-ui,sans-serif}}
#pano{{position:fixed;inset:0}}
.bar{{position:fixed;left:0;right:0;bottom:0;z-index:5;padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px));
 background:linear-gradient(transparent,rgba(12,11,10,.92) 35%);display:flex;flex-direction:column;gap:8px}}
.now{{font-size:18px;font-weight:500;text-align:center}}
.menu{{display:flex;gap:14px;overflow-x:auto;padding-bottom:2px;direction:rtl}}
.grp{{display:flex;gap:6px;align-items:center;flex:none}}
.grp span{{font-size:12px;color:var(--muted);white-space:nowrap}}
.menu button{{flex:none;background:var(--chip);color:var(--ink);border:1px solid #3d3833;border-radius:999px;padding:6px 12px;font:inherit;font-size:13px;cursor:pointer}}
.menu button.on{{background:var(--accent);color:#1b1815;border-color:var(--accent)}}
.hint{{position:fixed;top:calc(12px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);z-index:5;background:rgba(20,18,16,.8);
 padding:6px 12px;border-radius:999px;font-size:12.5px;color:var(--muted);white-space:nowrap}}
.pnlm-hotspot-base.pnlm-scene{{width:34px;height:34px;border-radius:50%;background:rgba(214,185,140,.95);border:3px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.4)}}
.pnlm-tooltip span{{font-family:inherit;font-size:13px;background:rgba(20,18,16,.9);color:#fff;padding:5px 9px;border-radius:6px}}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500&display=swap">
<div id="pano"></div>
<div class="hint" dir="rtl">اسحب لتلتفت · اضغط الدائرة للانتقال</div>
<div class="bar" dir="rtl"><div class="now" id="now"></div><div class="menu">{menu}</div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.js"></script>
<script>
const cfg={json.dumps(cfg, ensure_ascii=False)};
const v=pannellum.viewer('pano',cfg);
const now=document.getElementById('now');
function mark(){{const s=v.getScene();now.textContent=cfg.scenes[s].title;
 document.querySelectorAll('.menu button').forEach(b=>b.classList.toggle('on',b.dataset.s===s));}}
v.on('scenechange',()=>setTimeout(mark,50));v.on('load',mark);
document.querySelectorAll('.menu button').forEach(b=>b.addEventListener('click',()=>v.loadScene(b.dataset.s)));
setTimeout(()=>{{const h=document.querySelector('.hint');if(h)h.hidden=true}},6000);
</script>
'''
open(os.path.join(TOUR, 'index.html'), 'w').write(page)
print('scenes', len(scenes))
