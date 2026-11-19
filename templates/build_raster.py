"""Собирает svg/05, 07, 09 из src/*.stripped.svg и assets/*.png (картинки из Figma, присланные вручную)."""
import base64,re
from PIL import Image
CFG={'05':('assets/05_girl.png',),'07':('assets/07_hamster.png',),'09':('assets/09_boy.png',)}
for n,(img,) in CFG.items():
    W,H=Image.open(img).size
    s=open(f'src/{n}.stripped.svg',encoding='utf-8').read()
    b64=base64.b64encode(open(img,'rb').read()).decode()
    s=s.replace('@IMG0@','data:image/png;base64,'+b64)
    s=re.sub(r'(<image id="[^"]+" )width="\d+" height="\d+"',rf'\1width="{W}" height="{H}"',s)
    if n=='05':   # ширина 1400, пропорции сохранены
        s=s.replace('translate(0 -0.0278351) scale(0.00103093)',f'translate(0 -0.0278351) scale({1/W:.8f})')
    if n=='07':   # картинка = рамка 920x990
        s=s.replace('matrix(0.000858124 0 0 0.000797448 -0.0380435 0)',f'matrix({1/W:.8f} 0 0 {1/H:.8f} 0 0)')
    if n=='09':   # по высоте блока 1184, по центру видимой части
        k=1184/H
        s=s.replace('matrix(0.000976562 0 0 0.00113162 0 -0.0793919)',f'matrix({k/1372:.8f} 0 0 {1/H:.8f} {150/1372:.6f} 0)')
    open(f'svg/{n}.svg','w',encoding='utf-8').write(s); print(n,len(s))
