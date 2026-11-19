import glob,os,sys
from playwright.sync_api import sync_playwright
files=sorted(glob.glob('svg/*.svg'))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1917})
    for f in files:
        n=os.path.basename(f)[:-4]; svg=open(f,encoding='utf-8').read()
        html=f'<!doctype html><meta charset="utf-8"><title>Шаблон {n}</title><style>html,body{{margin:0;background:#fff}}svg{{display:block;width:1080px;height:1917px}}</style>\n{svg}'
        open(f'html/{n}.html','w',encoding='utf-8').write(html)
        pg.set_content(html); pg.screenshot(path=f'png/{n}.png',clip={'x':0,'y':0,'width':1080,'height':1917})
        print(n,'ok')
    b.close()
