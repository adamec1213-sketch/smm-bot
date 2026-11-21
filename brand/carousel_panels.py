"""Карусель «Минвата или PIR?» — 8 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_panels/'; os.makedirs(OUT,exist_ok=True)
BLUE=(120,160,190)

def cover():
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),'П А Н Е Л И',font=F(26,'700'),fill=GOLD); y=150
    for t,c in [('Минвата',WHT),('или PIR?',GOLD)]:
        d.text((X0,y),t,font=F(96),fill=c); y+=110
    rich(d,X0,y+24,[('Какие сэндвич-панели брать для ангара',0)],38,900)
    footer(im,1); return im

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Ч Т О   В Н У Т Р И',[('Панель —',WHT),('это пирог',GOLD)],96)
    y=rich(d,X0,y+30,[('Два листа металла, а между ними',0),('утеплитель.',1),('От него зависят тепло, пожарная безопасность и цена.',0)],44,W-2*X0)+60
    for name,desc,col in [('Минвата','каменная вата из базальта',WHT),('PIR','пенополиизоцианурат, жёсткая пена',GOLD)]:
        d.rounded_rectangle([X0,y,W-X0,y+150],radius=28,fill=(18,18,21),outline=(80,68,46),width=2)
        d.text((X0+44,y+28),name,font=F(54),fill=col); rich(d,X0+44,y+96,[(desc,0)],32,W-2*X0-88); y+=180
    footer(im,2); return im

def typ(n,eyebrow,title,col,pros,cons,uses):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,[(title,col)],96)+20
    for t in pros:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+28
    for t in cons:
        mark(d,X0,y+4,False); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+28
    y+=30; d.text((X0,y),'П О Д Х О Д И Т   Д Л Я',font=F(28,'700'),fill=GOLD); y+=60
    bullets(d,y,[[(u,1)] for u in uses],44,30)
    footer(im,n); return im

def s5():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Р А В Н Е Н И Е',[('Минвата',WHT),('vs PIR',GOLD)])+40
    cx=[X0,X0+380,X0+680]
    d.text((cx[1],y),'Минвата',font=F(32,'700'),fill=WHT); d.text((cx[2],y),'PIR',font=F(32,'700'),fill=GOLD); y+=66
    rows=[('Огонь','не горит (НГ)','горючий, Г 1'),('Теплопроводн.','0,040–0,045','0,022–0,025'),('Толщина*','150 мм','80–90 мм'),('Вес','тяжелее','легче'),('Влага','боится','не боится'),('Цена за м²','ниже','обычно выше')]
    for r in rows:
        d.line([(X0,y-14),(W-X0,y-14)],fill=(50,48,44),width=2)
        d.text((cx[0],y),r[0],font=F(34,'700'),fill=WHT); d.text((cx[1],y),r[1],font=F(32,'500'),fill=TXT); d.text((cx[2],y),r[2],font=F(32,'500'),fill=TXT); y+=84
    rich(d,X0,y+16,[('* при одинаковом тепле. Теплопроводность — Вт/(м·°C): чем меньше, тем теплее.',0)],28,W-2*X0)
    footer(im,5); return im

def s6():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Г Л А В Н О Е',[('Сначала пожарные',WHT),('нормы, потом цена',GOLD)],80)
    y=rich(d,X0,y+30,[('Что можно ставить, решает',0),('проект',1),('— класс пожарной опасности здания и категория склада.',0)],42,W-2*X0)+50
    for t in [[('Противопожарные стены и стены с пределом огнестойкости —',0),('только негорючие панели, то есть минвата.',1)],
              [('Склады с горючими товарами, производство со сваркой —',0),('чаще всего минвата.',1)],
              [('PIR можно там, где проект это разрешает.',0)]]:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+34
    footer(im,6); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   В Ы Б Р А Т Ь',[('Минвата,',WHT),('если…',GOLD)])+20
    for t in ['Склад, цех или автосервис','В проекте есть требования по огнестойкости','Внутри работают с огнём или сваркой']:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,[(t,1)],40,W-2*X0-70),y+60)+28
    y+=40; d.text((X0,y),'PIR, если…',font=F(72),fill=GOLD); y+=110
    for t in ['Холодильник или морозильный склад','Пищевое производство, где важна влагостойкость','Нужна тёплая стена при малой толщине']:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,[(t,1)],40,W-2*X0-70),y+60)+28
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Н А Ш   В Ы Б О Р',[('Для складов',WHT),('и цехов —',WHT),('минвата',GOLD)],84)
    y=rich(d,X0,y+20,[('Стены 120 мм, кровля 150 мм. PIR ставим, когда этого требует задача: холод, влага, тонкая стена.',0)],42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

slides=[cover(),s2(),
 typ(3,'В А Р И А Н Т   1','Минвата',WHT,[[('Не горит:',1),('из неё делают противопожарные стены',0)],[('Лучше глушит шум',0)]],[[('Тяжелее и боится влаги на стыках —',0),('нужна герметизация',1)]],['Склады','Производство и цеха','Автосервисы']),
 typ(4,'В А Р И А Н Т   2','PIR',GOLD,[[('Теплее',1),('в 1,7–2 раза при той же толщине',0)],[('Легче и не впитывает воду',0)]],[[('Горючий:',1),('лучшие марки — Г 1 (слабогорючие)',0)]],['Холодильные склады','Пищевое производство','Офисы и тёплые пристройки']),
 s5(),s6(),s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
print('ok')
