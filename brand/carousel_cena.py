"""Карусель №1 «Ангар 1000 м²: куда уходят деньги». Цифры — из SHARE (пока пусто: [__])."""
import os, shutil
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0]
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(src,'v2','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1'.split()]
background,footer,rich,pills=g['background'],g['footer'],g['rich'],g['pills']
OUT=ROOT+'/drafts/carousel_cena/'; os.makedirs(OUT,exist_ok=True)

# Источник: КП №192 от 29.09.2026 — ангар (склад) 1440 м², высота 8 м, Москва, итого 55 343 780 ₽ без НДС
AREA=1440; TOTAL=55343780
SUM={'Проект':900000,'Фундамент и пол':16678800,'Каркас':13298000,'Стены и кровля':12589780,'Ворота и окна':1529500,'Монтаж':10347700}
SHARE={'Проект':2,'Фундамент и пол':30,'Каркас':24,'Стены и кровля':23,'Ворота и окна':3,'Монтаж':18}  # округлено, сумма 100
def pct(k): return f'{SHARE[k]}%'
def m2(k): return f'~{round(SUM[k]/AREA/100)*100:,}'.replace(',', '\u00a0')+'\u00a0₽/м²'

ITEMS=[('Проект',[[('Чертежи',0),('КЖ, КМ и КМД',1)],[('По ним делают',0),('фундамент и металл',1)],[('Расчёт нагрузок',1),('под ваш регион',0)]]),
('Фундамент и пол',[[('Разработка грунта',1),('с вывозом — 720\u00a0м³',0)],[('Монолитный ростверк',1),('под колонны',0)],[('Плита пола 200\u00a0мм,',1),('двойное армирование',0)]]),
('Каркас',[[('76 тонн',1),('металлоконструкций',0)],[('Изготовление',1),('по чертежам КМД',0)],[('Доставка',1),('на объект',0)]]),
('Стены и кровля',[[('Сэндвич-панели:',1),('стены 120\u00a0мм, кровля 150\u00a0мм минваты',0)],[('Фасонные элементы',1),('— примыкания, отливы, коньки',0)],[('Водосток',1),('и снегозадержатели',0)]]),
('Ворота и окна',[[('Секционные ворота',1),('3×3,5\u00a0м с автоматикой',0)],[('Окна ПВХ',1),('— 65\u00a0м²',0)]]),
('Монтаж',[[('Монтаж каркаса',1),('с краном и техникой',0)],[('Монтаж панелей',1),('— 2\u00a0937\u00a0м²',0)],[('Гарантия',1),('24 месяца',0)]])]
LABELS=[k for k,_ in ITEMS]

def item(i,name,bullets):
    n=i+1; im=background(); d=ImageDraw.Draw(im)
    pills(d,n,['Проект','Фундамент','Каркас','Стены','Ворота','Монтаж'])
    d.rounded_rectangle([X0,160,X0+104,226],radius=33,outline=GOLD,width=3); d.text((X0+22,168),f'{n:02d}',font=F(42),fill=GOLD)
    d.text((X0,246),name,font=F(80 if len(name)<14 else 72),fill=WHT)
    top=380; d.rounded_rectangle([X0,top,W-X0,top+330],radius=36,fill=(18,18,21),outline=(80,68,46),width=2)
    d.text((X0+56,top+48),'ДОЛЯ В ЦЕНЕ АНГАРА',font=F(26,'700'),fill=GRY)
    p=pct(name); d.text((X0+50,top+96),p,font=F(150),fill=GOLD)
    t=m2(name); d.text((W-X0-56-d.textlength(t,font=F(40,'700')),top+170),t,font=F(40,'700'),fill=WHT)
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
    d.text((X0,96),'И Т О Г   П О   С М Е Т Е',font=F(26,'700'),fill=GOLD)
    d.text((X0,150),'55,3 млн ₽',font=F(110),fill=GOLD)
    y=rich(d,X0,290,[('Склад 1440\u00a0м², высота 8\u00a0м, Москва —',0),('38\u00a0400\u00a0₽/м²',1),('без НДС',0)],38,W-2*X0)+10
    y=rich(d,X0,y,[('Срок —',0),('95 рабочих дней.',1),('Гарантия —',0),('24 месяца.',1)],38,W-2*X0)+40
    d.rounded_rectangle([X0,y,W-X0,y+250],radius=24,fill=(26,25,24)); d.rectangle([X0,y+24,X0+6,y+226],fill=GOLD)
    d.text((X0+40,y+28),'ЧЕСТНО: НЕ ВХОДИТ В ЭТУ СМЕТУ',font=F(26,'700'),fill=GOLD)
    rich(d,X0+40,y+76,[('Топпинг пола, сваи, двери, инженерные системы, огнезащита, подключение к сетям — считаем отдельно, заранее.',0)],34,W-2*X0-80)
    y+=300
    d.text((X0,y),'Нужно построить ангар?',font=F(48),fill=WHT)
    d.text((X0,y+64),'Пишите в директ',font=F(48),fill=GOLD)
    footer(im,8,last=True); return im

shutil.copy(ROOT+'/drafts/plan_covers/01.jpg',OUT+'01.jpg')
slides=[Image.open(OUT+'01.jpg').convert('RGBA')]+[item(i,n,b) for i,(n,b) in enumerate(ITEMS)]+[final()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(4*300+50,2*375+30),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%4)*310,10+(k//4)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
