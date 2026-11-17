"""Карусель №1 «Ангар 1000 м²: куда уходят деньги». Цифры — из SHARE (пока пусто: [__])."""
import os, shutil
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0]
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(src,'v2','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1'.split()]
background,footer,rich,pills=g['background'],g['footer'],g['rich'],g['pills']
OUT=ROOT+'/drafts/carousel_cena/'; os.makedirs(OUT,exist_ok=True)

# Доля статьи в цене, % — заполнить по данным владельца (None = пусто)
SHARE={'Проект':None,'Фундамент':None,'Каркас':None,'Стены и кровля':None,'Ворота и окна':None,'Монтаж':None}
def pct(k): return f'{SHARE[k]}%' if SHARE[k] is not None else '[__]%'

ITEMS=[('Проект',[[('Расчёт нагрузок:',1),('снег, ветер, оборудование',0)],[('Чертежи',0),('КМ и КМД',1),('— по ним делают металл',0)],[('Архитектура и планировка',1),('под ваш процесс',0)]]),
('Фундамент',[[('Геология',1),('участка — без неё фундамент «на глаз»',0)],[('Тип фундамента:',0),('плита, лента или сваи',1)],[('Бетон, арматура',1),('и закладные под колонны',0)]]),
('Каркас',[[('Металлоконструкции',1),('по чертежам КМД',0)],[('Антикоррозийная обработка',1),('и покраска',0)],[('Изготовление',1),('и доставка на объект',0)]]),
('Стены и кровля',[[('Сэндвич-панели:',1),('толщина утеплителя под ваш регион',0)],[('Фасонные элементы',1),('и герметизация стыков',0)],[('Водосток',1),('и снегозадержание',0)]]),
('Ворота и окна',[[('Ворота:',0),('секционные или откатные',1)],[('Двери',1),('и аварийные выходы',0)],[('Окна',1),('и световые проёмы',0)]]),
('Монтаж',[[('Бригада',1),('и прораб на объекте',0)],[('Кран и техника',1),('для сборки каркаса',0)],[('Сдача объекта',1),('и гарантия',0)]])]
LABELS=[k for k,_ in ITEMS]

def item(i,name,bullets):
    n=i+1; im=background(); d=ImageDraw.Draw(im)
    pills(d,n,['Проект','Фундамент','Каркас','Стены','Ворота','Монтаж'])
    d.rounded_rectangle([X0,160,X0+104,226],radius=33,outline=GOLD,width=3); d.text((X0+22,168),f'{n:02d}',font=F(42),fill=GOLD)
    d.text((X0,246),name,font=F(80),fill=WHT)
    top=380; d.rounded_rectangle([X0,top,W-X0,top+330],radius=36,fill=(18,18,21),outline=(80,68,46),width=2)
    d.text((X0+56,top+48),'ДОЛЯ В ЦЕНЕ АНГАРА',font=F(26,'700'),fill=GRY)
    p=pct(name); d.text((X0+50,top+96),p,font=F(150),fill=GOLD)
    # шкала
    bx,by,bw=X0+56,top+270,W-2*X0-112
    d.rounded_rectangle([bx,by,bx+bw,by+18],radius=9,fill=(40,38,34))
    if SHARE[name] is not None: d.rounded_rectangle([bx,by,bx+int(bw*SHARE[name]/100),by+18],radius=9,fill=GOLD)
    y=top+380; d.text((X0,y),'ЧТО ВХОДИТ',font=F(26,'700'),fill=GOLD); y+=54
    for b in bullets:
        d.rounded_rectangle([X0,y+12,X0+22,y+34],radius=6,fill=GOLD); y=rich(d,X0+46,y,b,36,W-2*X0-46)+18
    footer(im,n+1); return im

def final():
    im=background(); d=ImageDraw.Draw(im)
    d.text((X0,96),'И Т О Г',font=F(26,'700'),fill=GOLD)
    y=150
    for t,c in [('Всё включено —',WHT),('от 20 000 ₽/м²',GOLD)]:
        d.text((X0,y),t,font=F(84),fill=c); y+=100
    y=rich(d,X0,y+20,[('Ангар 1000 м² — от',0),('20 млн ₽',1),('под ключ. Все 6 статей в одной смете, без доплат по ходу стройки.',0)],38,W-2*X0)+30
    for k in LABELS:
        d.rounded_rectangle([X0,y+6,X0+40,y+46],radius=10,fill=GOLD)
        d.line([(X0+10,y+26),(X0+18,y+35),(X0+31,y+16)],fill=BG1,width=5)
        d.text((X0+64,y+4),k,font=F(40,'700'),fill=WHT); y+=64
    y+=30
    d.text((X0,y),'Нужно построить ангар?',font=F(48),fill=WHT)
    d.text((X0,y+64),'Пишите в директ',font=F(48),fill=GOLD)
    footer(im,8,last=True); return im

shutil.copy(ROOT+'/drafts/plan_covers/01.jpg',OUT+'01.jpg')
slides=[Image.open(OUT+'01.jpg').convert('RGBA')]+[item(i,n,b) for i,(n,b) in enumerate(ITEMS)]+[final()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(4*300+50,2*375+30),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%4)*310,10+(k//4)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
