"""Карусель №6 «Разрешение на ангар: 5 шагов» — 9 слайдов (по ГрК РФ, без конкретики владельца)."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
N=9
v2=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0].replace("f'{n}/8'","f'{n}/%d'"%N)
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(v2,'v2','exec'),g)
ot=open(ROOT+'/brand/carousel_ot.py').read(); exec(compile(ot[ot.index('RED='):ot.index('def s2():')],'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_razreshenie/'; os.makedirs(OUT,exist_ok=True)
hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))

def cover():
    im=background()
    fg=ImageEnhance.Brightness(hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS)).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    y=head(d,'З А К О Н',[('Разрешение',GOLD),('на ангар:',WHT),('5 шагов',WHT)],96)
    rich(d,X0,y+20,[('От участка до регистрации в ЕГРН',0)],38,900)
    footer(im,1); return im

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Н А Ч А Л А',[('Нужно ли',WHT),('разрешение?',GOLD)],96)+40
    for ok,t,sub in [(True,'Капитальный ангар — да','Разрешение на строительство — ст. 51 ГрК РФ'),
                     (False,'Некапитальный — нет','Но и зарегистрировать его в ЕГРН как недвижимость нельзя')]:
        d.rounded_rectangle([X0,y,W-X0,y+250],radius=30,fill=(18,18,21),outline=(80,68,46) if ok else (110,60,50),width=2)
        mark(d,X0+40,y+44,ok); d.text((X0+110,y+44),t,font=F(46),fill=WHT)
        rich(d,X0+40,y+120,[(sub,0)],40,W-2*X0-80); y+=290
    rich(d,X0,y+10,[('Что такое капитальный ангар — в нашей карусели про 6 признаков.',0)],34,W-2*X0)
    footer(im,2); return im

STEPS=[('Участок',[[('Проверить',0),('вид разрешённого использования',1),('— можно ли строить склад или производство',0)],[('Получить',0),('ГПЗУ',1),('— где и что можно строить на участке',0)]],'Градостроительный план участка'),
('Изыскания и проект',[[('Инженерные изыскания:',1),('геология и геодезия',0)],[('Проектная документация',1),('— по ней получают разрешение и строят',0)],[('В ряде случаев —',0),('экспертиза проекта',1)]],'Проект ангара'),
('Разрешение',[[('Заявление в администрацию',1),('с проектом и документами на участок',0)],[('Основание —',0),('ст. 51 ГрК РФ',1)],[('Только после него',0),('начинают стройку',1)]],'Разрешение на строительство'),
('Ввод в эксплуатацию',[[('Ангар построен',1),('по проекту',0)],[('Заявление на',0),('разрешение на ввод',1),('— ст. 55 ГрК РФ',0)],[('Нужен',0),('технический план',1),('от кадастрового инженера',0)]],'Разрешение на ввод'),
('Регистрация в ЕГРН',[[('Кадастровый учёт',1),('и регистрация права собственности',0)],[('Ангар становится',0),('недвижимостью',1)],[('Его можно',0),('продать, заложить, сдать',1)]],'Выписка из ЕГРН')]

def step(i,title,bl,doc):
    n=i+1; im=background(); d=ImageDraw.Draw(im)
    d.text((X0,96),'Ш А Г',font=F(26,'700'),fill=GOLD)
    d.text((X0,130),f'{n:02d}',font=F(150),fill=GOLD)
    d.text((X0,330),title,font=F(72 if len(title)<16 else 64),fill=WHT)
    y=bullets(d,470,bl,46,44)+50
    d.rounded_rectangle([X0,y,W-X0,y+150],radius=28,fill=(30,27,22),outline=GOLD,width=2)
    d.text((X0+40,y+28),'Н А   В Ы Х О Д Е',font=F(24,'700'),fill=GOLD)
    d.text((X0+40,y+70),doc,font=F(44),fill=WHT)
    footer(im,n+2); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    d.polygon([(X0,236),(X0+70,116),(X0+140,236)],outline=RED,width=8); d.text((X0+58,150),'!',font=F(64),fill=RED)
    d.text((X0,270),'Б Е З   Р А З Р Е Ш Е Н И Я',font=F(28,'700'),fill=RED)
    y=rich(d,X0,320,[('Капитальный ангар без разрешения —',1),('самовольная постройка',1)],62,W-2*X0,1.15)+40
    y=bullets(d,y,[[('Основание —',0),('ст. 222 ГК РФ',1)],[('Риск',0),('сноса',1),('по решению суда',0)],[('Нельзя',0),('зарегистрировать,',1),('продать или заложить',0)],[('Узаконить потом —',0),('через суд,',1),('долго и без гарантий',0)]],42,34)
    footer(im,8); return im

def s9():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'О С Т А Л И С Ь   В О П Р О С Ы ?',[('Строите',WHT),('капитальный',GOLD),('ангар?',WHT)],90)
    y=rich(d,X0,y+20,[('Подскажем, что нужно для вашего участка, и посчитаем смету',0),('по статьям.',1)],46,W-2*X0)+90
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,N,last=True); return im

slides=[cover(),s2()]+[step(i,*s) for i,s in enumerate(STEPS)]+[s8(),s9()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(3*300+40,3*375+40),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%3)*310,10+(k//3)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
