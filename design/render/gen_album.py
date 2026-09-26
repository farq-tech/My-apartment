"""Build the render album page from design/renders/final/*.jpg."""
import os, html

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, '..', 'renders', 'final')
OUT = os.path.join(HERE, '..', 'renders', 'album', 'index.html')

ROOMS = {
    'F1': [('01', 'StairHall', 'Stair Hall'), ('02', 'Living', 'Living & Reception'), ('03', 'Dining', 'Dining'),
           ('04', 'Kitchen', 'Kitchen'), ('05', 'Staircase', 'Staircase'), ('06', 'GuestWC', 'Guest WC')],
    'F2': [('01', 'Entrance', 'Entrance'), ('02', 'FamilyLounge', 'Family Lounge'), ('03', 'Terrace', 'Greenhouse Terrace'),
           ('04', 'MasterBedroom', 'Master Bedroom'), ('05', 'MasterBath', 'Master Bathroom'),
           ('06', 'ChildBedroom', 'Child Bedroom'), ('07', 'Office', 'Office & Library'),
           ('08', 'OfficeBath', 'Office Bathroom'), ('09', 'GuestRoom', 'Guest Room'), ('10', 'GuestBath', 'Guest Bathroom')],
}
FLOORS = [('F1', 'First Floor', 'الدور الأول'), ('F2', 'Second Floor', 'الدور الثاني')]

files = sorted(f for f in os.listdir(FINAL) if f.endswith('.jpg'))

sections = []
order = []
for fk, fen, far in FLOORS:
    rooms = []
    for num, key, label in ROOMS[fk]:
        imgs = [f for f in files if f.startswith(f'{fk}-{num}_{key}_')]
        if not imgs:
            continue
        figs = []
        for f in imgs:
            v = f.rsplit('_V', 1)[1][:-4]
            idx = len(order)
            order.append((f, f'{fen} · {num} {label} · View {int(v):02d}'))
            figs.append(f'<figure><button class="shot" data-i="{idx}" aria-label="Open {html.escape(label)} view {v}">'
                        f'<img src="img/{f}" alt="{html.escape(label)}, view {v}" loading="lazy"></button>'
                        f'<figcaption><span>VIEW {int(v):02d}</span><span>OPTION 01</span></figcaption></figure>')
        rooms.append(f'<section class="room" id="{fk}-{num}"><header><span class="num">{num}</span><h3>{label}</h3>'
                     f'<span class="count">{len(imgs)} views</span></header><div class="grid">{"".join(figs)}</div></section>')
    sections.append(f'<section class="floor" id="{fk}"><div class="floorhead"><div><span class="eyebrow">{fen.upper()}</span>'
                    f'<h2>{far}</h2></div><img class="key" src="img/key_{fk}.png" alt="{fen} plan with camera positions"></div>'
                    f'{"".join(rooms)}</section>')

nav = ''.join(f'<a href="#{fk}-{num}">{fk[1]}.{num} {label}</a>' for fk, _, _ in FLOORS for num, key, label in ROOMS[fk]
              if any(f.startswith(f'{fk}-{num}_{key}_') for f in files))
data = ','.join('["img/%s","%s"]' % (f, html.escape(c)) for f, c in order)

page = f'''<title>Duplex Walkthrough</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=IBM+Plex+Sans+Arabic:wght@300;400;500&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
:root{{--bg:#EEEBE6;--surface:#F7F5F1;--ink:#24211D;--muted:#766C60;--line:#D8D1C6;--accent:#8A5A2B;
--f-d:"Cormorant Garamond",Georgia,serif;--f-b:"IBM Plex Sans Arabic",system-ui,sans-serif;--f-m:"IBM Plex Mono",ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#171614;--surface:#201E1B;--ink:#EDE7DE;--muted:#A59786;--line:#34302B;--accent:#D0A777;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#171614;--surface:#201E1B;--ink:#EDE7DE;--muted:#A59786;--line:#34302B;--accent:#D0A777;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-b)}}
.wrap{{max-width:1400px;margin:0 auto;padding-inline:20px;padding-block:32px 80px}}
.top{{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:12px 24px;padding-bottom:18px;border-bottom:1px solid var(--line)}}
h1{{font-family:var(--f-d);font-weight:500;font-size:clamp(30px,4vw,48px);margin:0;letter-spacing:.01em}}
.eyebrow,.count,figcaption,.num,nav a{{font-family:var(--f-m);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
nav{{display:flex;flex-wrap:wrap;gap:6px 16px;padding-block:14px;position:sticky;top:env(safe-area-inset-top,0px);background:var(--bg);z-index:5;border-bottom:1px solid var(--line)}}
nav a{{text-decoration:none}} nav a:hover,nav a:focus-visible{{color:var(--ink)}}
.floor{{padding-top:40px}}
.floorhead{{display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:end;padding-bottom:10px}}
.floorhead h2{{font-family:var(--f-b);font-weight:300;font-size:28px;margin:4px 0 0}}
.key{{justify-self:end;max-height:170px;width:auto;max-width:100%;background:#fff;border:1px solid var(--line)}}
.room{{padding-top:34px}}
.room header{{display:flex;align-items:baseline;gap:14px;padding-bottom:12px}}
.room h3{{font-family:var(--f-d);font-weight:500;font-size:28px;margin:0}}
.num{{color:var(--accent)}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
figure{{margin:0;display:flex;flex-direction:column;gap:6px}}
.shot{{all:unset;cursor:zoom-in;display:block}}
.shot img{{width:100%;display:block;aspect-ratio:1024/672;object-fit:cover;background:var(--surface)}}
.shot:focus-visible img{{outline:2px solid var(--accent);outline-offset:2px}}
figcaption{{display:flex;justify-content:space-between}}
.notes{{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;color:var(--muted);line-height:1.8;max-width:80ch}}
.lb{{position:fixed;inset:0;background:rgba(12,11,10,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;z-index:20;padding:16px}}
.lb img{{max-width:100%;max-height:calc(100% - 70px);object-fit:contain}}
.lb .bar{{display:flex;gap:18px;align-items:center;color:#EDE7DE;font-family:var(--f-m);font-size:12px;letter-spacing:.1em;text-transform:uppercase}}
.lb button{{background:none;border:1px solid #6b6258;color:#EDE7DE;padding:6px 14px;font:inherit;cursor:pointer}}
@media (max-width:760px){{.grid{{grid-template-columns:1fr}}.floorhead{{grid-template-columns:1fr}}.key{{justify-self:start}}}}
</style>
<div class="wrap">
  <div class="top"><div><span class="eyebrow">Master Design · Option 01</span><h1>Duplex Walkthrough</h1></div>
  <span class="eyebrow">First + Second Floor · {len(order)} views</span></div>
  <nav aria-label="Rooms">{nav}</nav>
  <section class="floor" id="walk"><div class="floorhead"><div><span class="eyebrow">WALKTHROUGH</span><h2>الجولة: من باب الشقة إلى الدور الأول</h2></div></div>
  <video src="img/walkthrough.mp4" controls playsinline preload="metadata" style="width:100%;background:#000"></video></section>
  {''.join(sections)}
  <div class="notes" dir="rtl" lang="ar">
    الهندسة من المخطط: الجدران والأبواب والنوافذ والدرج مبنية من ملف DWG بالمتر، والكاميرات في مواقع حقيقية كما في مفتاح كل دور.
    الأرضية: البلاط الرئيسي المركب في كل المساحات عدا الحمامات، والترافرتين في الحمامات أرضيات وجدراناً.
    افتراضات غير موجودة في المخطط: ارتفاع السقف 3.00 م وجلسات النوافذ.
    لون الجدران ‎#BFB2A2‎. غرفة الطفل مبنية على صورة المرجع بالأصفر بدل الوردي، ونقشة ورق الجدران مؤقتة حتى يصل كتالوج 5144-1. باب الشقة في الدور الثاني كما في المخطط.
  </div>
</div>
<div class="lb" id="lb" hidden><img id="lbimg" alt=""><div class="bar"><button id="prev">Prev</button><span id="cap"></span><button id="next">Next</button><button id="close">Close</button></div></div>
<script>
const D=[{data}];let i=0;const lb=document.getElementById('lb'),im=document.getElementById('lbimg'),cap=document.getElementById('cap');
function show(n){{i=(n+D.length)%D.length;im.src=D[i][0];im.alt=D[i][1];cap.textContent=D[i][1];lb.hidden=false;}}
document.querySelectorAll('.shot').forEach(b=>b.addEventListener('click',()=>show(+b.dataset.i)));
document.getElementById('prev').onclick=()=>show(i-1);document.getElementById('next').onclick=()=>show(i+1);
document.getElementById('close').onclick=()=>{{lb.hidden=true}};
document.addEventListener('keydown',e=>{{if(lb.hidden)return;if(e.key==='ArrowRight')show(i+1);if(e.key==='ArrowLeft')show(i-1);if(e.key==='Escape')lb.hidden=true;}});
</script>
'''
open(OUT, 'w').write(page)
print('views', len(order))
