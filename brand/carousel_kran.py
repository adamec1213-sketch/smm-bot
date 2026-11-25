"""Карусель «Кран в ангаре: что меняется» — 8 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_kran/'; os.makedirs(OUT,exist_ok=True)

def cover():
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y-60)/380))*min(1,y/180)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),'К Р А Н',font=F(26,'700'),fill=GOLD); y=150
    for t,c in [('Кран',WHT),('в ангаре',GOLD)]:
        d.text((X0,y),t,font=F(96),fill=c); y+=110
    rich(d,X0,y+24,[('Что меняется в проекте и в смете',0)],38,900)
    footer(im,1); return im

def card(n,eyebrow,title,lines,checks=None,tip=None,big=None):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,title,90)
    y=rich(d,X0,y+30,lines,44,W-2*X0)+50
    for t in checks or []:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+32
    if tip:
        y+=10; d.rounded_rectangle([X0,y,W-X0,y+230],radius=28,fill=((255,255,255) if g['THEME']=='light' else (18,18,21)),outline=((226,214,192) if g['THEME']=='light' else (80,68,46)),width=2)
        d.text((X0+44,y+34),'НА ПРАКТИКЕ',font=F(28,'700'),fill=GOLD)
        rich(d,X0+44,y+84,tip,36,W-2*X0-88)
    footer(im,n); return im

def s3():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Д В А   В А Р И А Н Т А',[('Подвесной',WHT),('или опорный',GOLD)],90)+40
    for name,col,lines in [('Подвесная кран-балка',WHT,[('Висит на',0),('фермах',1),('покрытия. Подходит для лёгких грузов — обычно до 5 т.',0)]),
                           ('Опорный кран',GOLD,[('Ездит по',0),('подкрановым балкам',1),('на колоннах. Для тяжёлых грузов и больших пролётов.',0)])]:
        d.rounded_rectangle([X0,y,W-X0,y+300],radius=30,fill=((255,255,255) if g['THEME']=='light' else (18,18,21)),outline=((226,214,192) if g['THEME']=='light' else (80,68,46)),width=2)
        d.text((X0+44,y+34),name,font=F(46),fill=col)
        rich(d,X0+44,y+110,lines,38,W-2*X0-88); y+=330
    footer(im,3); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'П Р И М Е Р   П Р О Е К Т А',[('Склад 60 × 24 м',WHT),('с краном 5 т',GOLD)],84)+40
    for lab,val in [('Высота крюка','6,0 м'),('Высота здания','10,8 м'),('Подкрановые балки','около 7 т'),('Металл всего','84 т')]:
        d.line([(X0,y-16),(W-X0,y-16)],fill=((224,215,200) if g['THEME']=='light' else (50,48,44)),width=2)
        d.text((X0,y),lab,font=F(42,'500'),fill=TXT); w=d.textlength(val,font=F(52)); d.text((W-X0-w,y-6),val,font=F(52),fill=GOLD); y+=110
    rich(d,X0,y+20,[('Кран заложен',0),('с самого начала проекта,',1),('поэтому каркас и фундамент сразу рассчитаны под него.',0)],40,W-2*X0)
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Р А С С Ч И Т А Е М',[('Ангар',WHT),('под ваш кран',GOLD)],90)
    y=rich(d,X0,y+20,[('Напишите, что будете поднимать, какой вес и на какую высоту. Заложим кран в проект и смету сразу.',0)],42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

slides=[cover(),
 card(2,'Г Л А В Н О Е',[('Решите',WHT),('до проекта',GOLD)],[('Кран — это не оборудование «потом». Под него считают колонны, фундаменты и высоту здания.',0)],
      [[('Грузоподъёмность,',1),('т',0)],[('Высота крюка,',1),('м',0)],[('Где ездит:',1),('весь пролёт или часть',0)]],
      [('Добавить кран в готовый ангар почти всегда дорого: каркас на него не рассчитан.',0)]),
 s3(),
 card(4,'К А Р К А С',[('Мощнее',WHT),('колонны',GOLD)],[('Опорный кран добавляет',0),('подкрановые балки',1),('по всей длине и нагружает колонны сверху и сбоку.',0)],
      [[('Колонны',1),('берут мощнее или из более прочной стали',0)],[('Добавляют',0),('связи',1),('— кран при торможении толкает каркас',0)]]),
 card(5,'В Ы С О Т А',[('Здание',WHT),('выше',GOLD)],[('Высота здания = высота крюка + сам кран + зазор до ферм.',0)],None,
      [('Крюк на 6 м — здание около 10,8 м. Выше здание — больше стен, панелей и металла.',0)]),
 card(6,'Ф У Н Д А М Е Н Т',[('Больше',WHT),('нагрузки',GOLD)],[('Кран нагружает фундамент не только весом, но и',0),('рывками',1),('при подъёме и торможении.',0)],
      [[('Фундаменты',1),('под колоннами крана больше',0)],[('Анкерные болты',1),('мощнее',0)]]),
 s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
print('ok')
