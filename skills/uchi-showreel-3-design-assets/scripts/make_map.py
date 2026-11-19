# -*- coding: utf-8 -*-
"""Карта регионов России из Natural Earth в src/map.ts (контур, выделенный регион, две точки).
Скачай: curl -sL -o /tmp/a1.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson
Запуск из папки проекта: python3 make_map.py (правь имя региона и координаты точек ниже). Данные: Natural Earth, общественное достояние."""
import json, math
d=json.load(open('/tmp/a1.geojson'))
f1,f2,lat0,lon0=math.radians(50),math.radians(70),math.radians(60),math.radians(100)
n=(math.sin(f1)+math.sin(f2))/2; C=math.cos(f1)**2+2*n*math.sin(f1); r0=math.sqrt(C-2*n*math.sin(lat0))/n
def pr(lon,lat):
    if lon<0: lon+=360
    l=math.radians(lon); p=math.radians(lat); r=math.sqrt(C-2*n*math.sin(p))/n; t=n*(l-lon0)
    return r*math.sin(t), r0-r*math.cos(t)
feats=[f for f in d['features'] if f['properties'].get('admin')=='Russia']
def rings(g):
    return [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
pts=[]; data=[]
for f in feats:
    name=f['properties']['name']; paths=[]
    for poly in rings(f['geometry']):
        for ring in poly[:1]:
            P=[pr(x,y) for x,y in ring]
            # skip huge jumps (antimeridian artifacts)
            paths.append(P); pts+=P
    data.append((name,paths))
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
S=1000/(x1-x0); H=(y1-y0)*S
def fmt(P):
    return 'M'+' L'.join('%.1f,%.1f'%((x-x0)*S,(y1-y)*S) for x,y in P)+'Z'
out={'w':1000,'h':round(H,1),'sakha':'','rest':''}
for name,paths in data:
    s=' '.join(fmt(P) for P in paths)
    if name=='Sakha (Yakutia)': out['sakha']+=s
    else: out['rest']+=s+' '
ox,oy=pr(142.78,63.46); vx,vy=pr(133.39,67.55)
out['oy']=[round((ox-x0)*S,1),round((y1-oy)*S,1)]; out['vh']=[round((vx-x0)*S,1),round((y1-vy)*S,1)]
open('src/map.ts','w').write('export const MAP = '+json.dumps(out)+' as const;\n')
print(out['w'],out['h'],out['oy'],out['vh'],len(out['rest'])//1000,'KB')
