"""Карусель «216 тонн снега на крыше» — снеговые районы. 8 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_sneg/'; os.makedirs(OUT,exist_ok=True)
BLUE=(150,185,215)

def cover():
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),'С Н Е Г',font=F(26,'700'),fill=GOLD); y=150
    for t,c in [('216 тонн',WHT),('на крыше',GOLD)]:
        d.text((X0,y),t,font=F(96),fill=c); y+=110
    rich(d,X0,y+24,[('Почему снег решает, сколько стоит ангар',0)],38,900)
    footer(im,1); return im

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'О Т К У Д А   Ц И Ф Р А',[('Склад',WHT),('60 × 24 м',GOLD)],96)+30
    for lab,val in [('Площадь кровли','1 440 м²'),('Расчётный снег для Москвы и СПб','150 кг/м²'),('Расчётный снег на всей кровле','216 т')]:
        d.rounded_rectangle([X0,y,W-X0,y+170],radius=28,fill=(18,18,21),outline=(80,68,46),width=2)
        rich(d,X0+44,y+30,[(lab,0)],34,W-2*X0-88)
        d.text((X0+44,y+82),val,font=F(64),fill=GOLD if '216' in val else WHT); y+=195
    rich(d,X0,y+10,[('Каркас обязан держать этот вес',0),('с запасом,',1),('каждую зиму.',0)],42,W-2*X0)
    footer(im,2); return im

def s3():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Н Е Г О В Ы Е   Р А Й О Н Ы',[('Нормы',WHT),('по СП 20.13330',GOLD)],84)+60
    rows=[('I','50'),('II','100'),('III','150'),('IV','200'),('V','250'),('VI','300'),('VII','350'),('VIII','400')]
    d.text((X0,y),'Район',font=F(32,'700'),fill=GRY); d.text((X0+300,y),'Вес снега, кг/м² *',font=F(32,'700'),fill=GRY); y+=62
    for r,v in rows:
        hl=r=='III'
        if hl: d.rounded_rectangle([X0-20,y-14,W-X0+20,y+66],radius=18,fill=(40,34,22))
        d.text((X0,y),r,font=F(46),fill=GOLD if hl else WHT); d.text((X0+300,y),v,font=F(46),fill=GOLD if hl else TXT)
        if hl: d.text((X0+520,y+8),'Москва, СПб',font=F(34,'700'),fill=GOLD)
        y+=84
    rich(d,X0,y+10,[('* вес снегового покрова земли, Sg',0)],28,W-2*X0)
    footer(im,3); return im

def card(n,eyebrow,title,lines,tip):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,title,90)
    y=rich(d,X0,y+30,lines,44,W-2*X0)+60
    if tip:
        d.rounded_rectangle([X0,y,W-X0,y+230],radius=28,fill=(18,18,21),outline=(80,68,46),width=2)
        d.text((X0+44,y+34),'НА ПРАКТИКЕ',font=F(28,'700'),fill=GOLD)
        rich(d,X0+44,y+84,tip,36,W-2*X0-88)
    footer(im,n); return im

def s4():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Ч Т О   М Е Н Я Е Т С Я',[('Больше снега —',WHT),('мощнее каркас',GOLD)],90)+30
    for t in [[('Прогоны',1),('ставят чаще: панель между ними держит меньший пролёт',0)],
              [('Фермы и балки',1),('берут мощнее',0)],
              [('Колонны и фундаменты',1),('получают больше нагрузки',0)],
              [('Итог:',1),('больше металла и бетона — выше цена',0)]]:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,t,42,W-2*X0-70),y+60)+40
    footer(im,4); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'И Т О Г',[('Цена начинается',WHT),('с адреса',GOLD)],96)+40
    for k,t in enumerate(['Город','Снеговой район','Нагрузка на кровлю','Металл и фундамент','Цена'],1):
        d.text((X0,y),str(k),font=F(56),fill=GOLD); d.text((X0+80,y+6),t,font=F(48),fill=WHT); y+=96
    rich(d,X0,y+30,[('Поэтому, прежде чем назвать цену, мы спрашиваем,',0),('где будет стоять ангар.',1)],42,W-2*X0)
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Р А С С Ч И Т А Е М',[('Ангар под',WHT),('снег вашего',WHT),('города',GOLD)],84)
    y=rich(d,X0,y+20,[('Напишите адрес участка и размеры. Посчитаем каркас под нагрузки вашего района по СП.',0)],42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

slides=[cover(),s2(),s3(),s4(),
 card(5,'О П А С Н Ы Е   М Е С Т А',[('Снеговые',WHT),('мешки',GOLD)],[('У парапетов, перепадов высот и пристроек снег наметает сугробами. Там нагрузка',0),('в разы выше средней,',1),('и это учитывают в расчёте.',0)],[('Плоская кровля с парапетом копит снег по краям — узлы там усиливают.',0)]),
 card(6,'О Ш И Б К А',[('Каркас',WHT),('«из каталога»',GOLD)],[('Типовой каркас могут рассчитать на более тёплый регион. Дешевле на старте, но под снегом',0),('вашего района',1),('он работает на пределе.',0)],[('Спросите подрядчика: на какой снеговой район рассчитан каркас? Ответ должен быть в проекте.',0)]),
 s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
print('ok')
