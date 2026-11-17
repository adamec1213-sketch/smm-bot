"""Карусель №3 «Холодный или тёплый ангар?» — 8 слайдов."""
import os, shutil
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_teplo/'; os.makedirs(OUT,exist_ok=True)
BLUE=(120,160,190)

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Г Л А В Н Ы Й   В О П Р О С',[('Что будет',WHT),('внутри?',GOLD)],96)
    y=rich(d,X0,y+30,[('Тип ангара выбирают не по цене, а по тому,',0),('что и кто будет внутри зимой.',1)],44,W-2*X0)+60
    y=bullets(d,y,[[('Нужна',0),('плюсовая температура',1),('— для людей или товара?',0)],
                   [('Люди будут работать',0),('каждый день?',1)],
                   [('Или это',0),('хранение,',1),('куда заходят время от времени?',0)]])
    footer(im,2); return im

def typ(n,eyebrow,title,col,what,uses,pros,cons):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,[(title,col)],96)
    y=rich(d,X0,y+20,what,46,W-2*X0)+70
    d.text((X0,y),'П О Д Х О Д И Т   Д Л Я',font=F(28,'700'),fill=GOLD); y+=64
    y=bullets(d,y,[[(u,1)] for u in uses],48,34)+60
    for ok,t in [(True,pros),(False,cons)]:
        mark(d,X0,y+4,ok); y=max(rich(d,X0+70,y,[(t,0)],44,W-2*X0-70),y+60)+36
    footer(im,n); return im

def s5():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Н А Ш   С Т А Н Д А Р Т   Д Л Я   М С К   И   С П Б',[('Толщина',WHT),('утеплителя',GOLD)])+40
    for lab,mm,note in [('Стены','120','сэндвич-панели, минеральная вата'),('Кровля','150','толще стен — тепло уходит вверх')]:
        d.rounded_rectangle([X0,y,W-X0,y+250],radius=30,fill=(18,18,21),outline=(80,68,46),width=2)
        d.text((X0+48,y+36),lab.upper(),font=F(30,'700'),fill=GRY)
        d.text((X0+44,y+80),mm,font=F(130),fill=GOLD); w=d.textlength(mm,font=F(130))
        d.text((X0+60+w,y+138),'мм',font=F(54),fill=GOLD)
        rich(d,X0+48+w+150,y+110,[(note,0)],32,W-2*X0-(w+260)); y+=290
    rich(d,X0,y+10,[('Минвата не горит — это важно для склада и производства.',0)],36,W-2*X0)
    footer(im,5); return im

def s6():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Р А В Н Е Н И Е',[('Холодный',BLUE),('vs тёплый',GOLD)])+40
    cx=[X0,X0+430,X0+700]
    d.text((cx[1],y),'Холодный',font=F(32,'700'),fill=BLUE); d.text((cx[2],y),'Тёплый',font=F(32,'700'),fill=GOLD); y+=66
    rows=[('Утепление','нет','сэндвич'),('Отопление','нет','можно'),('Люди внутри','временно','постоянно'),('Конденсат','бывает','меньше'),('Зимой внутри','как снаружи','плюс'),('Стоимость','дешевле','дороже')]
    for r in rows:
        d.line([(X0,y-14),(W-X0,y-14)],fill=(50,48,44),width=2)
        d.text((cx[0],y),r[0],font=F(36,'700'),fill=WHT); d.text((cx[1],y),r[1],font=F(36,'500'),fill=TXT); d.text((cx[2],y),r[2],font=F(36,'500'),fill=TXT); y+=88
    footer(im,6); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   В Ы Б Р А Т Ь',[('Выбирайте',WHT),('тёплый, если…',GOLD)])+30
    for t in ['Люди работают внутри каждый день','Товару или технике нужен плюс','Внутри будет автосервис, цех или офис','Планируете сдавать в аренду под разные задачи']:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,[(t,1)],40,W-2*X0-70),y+60)+34
    y+=20; d.text((X0,y),'Холодный — если',font=F(44),fill=BLUE)
    rich(d,X0,y+66,[('это хранение техники или стройматериалов, где мороз не страшен.',0)],38,W-2*X0)
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Н Е   У В Е Р Е Н Ы ?',[('Расскажите,',WHT),('что будет',WHT),('в ангаре',GOLD)],84)
    y=rich(d,X0,y+20,[('Подберём тип, утепление и посчитаем смету',0),('по статьям.',1)],46,W-2*X0)+90
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

shutil.copy(ROOT+'/drafts/plan_covers/03.jpg',OUT+'01.jpg')
slides=[Image.open(OUT+'01.jpg').convert('RGBA'),s2(),
 typ(3,'В А Р И А Н Т   1','Холодный',BLUE,[('Металлокаркас и',0),('профлист без утепления.',1)],['Хранение техники','Стройматериалы','Сельхозтехника и сено'],'Дешевле и быстрее','Зимой внутри как на улице, на металле бывает конденсат'),
 typ(4,'В А Р И А Н Т   2','Тёплый',GOLD,[('Металлокаркас и',0),('сэндвич-панели с минватой.',1)],['Производство и цех','Автосервис','Склад с плюсовой температурой'],'Можно работать круглый год','Дороже холодного: панели и отопление'),
 s5(),s6(),s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(4*300+50,2*375+30),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%4)*310,10+(k//4)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
