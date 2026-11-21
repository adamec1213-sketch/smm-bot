"""Карусель «28 тонн или 84?» — сколько металла в ангаре. 8 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_metall/'; os.makedirs(OUT,exist_ok=True)

def cover():
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),'М Е Т А Л Л',font=F(26,'700'),fill=GOLD); y=150
    for t,c in [('28 тонн',WHT),('или 84?',GOLD)]:
        d.text((X0,y),t,font=F(96),fill=c); y+=110
    rich(d,X0,y+24,[('От чего зависит, сколько металла уйдёт на ваш ангар',0)],38,900)
    footer(im,1); return im

def card(d,y,title,lines,big,unit,col):
    d.rounded_rectangle([X0,y,W-X0,y+300],radius=30,fill=(18,18,21),outline=(80,68,46),width=2)
    d.text((X0+44,y+34),title,font=F(40),fill=col)
    rich(d,X0+44,y+96,lines,32,560)
    d.text((W-X0-330,y+120),big,font=F(110),fill=col); w=d.textlength(big,font=F(110))
    d.text((W-X0-330+w+12,y+176),unit,font=F(44),fill=col)
    return y+330

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Д В А   Н А Ш И Х   О Б Ъ Е К Т А',[('Сравните',WHT),('металл',GOLD)],96)+30
    y=card(d,y,'Ангар 18 × 30 м',[('высота 6 м, фермы,',0),('без крана',0)],'28','т',WHT)
    y=card(d,y,'Склад 60 × 24 м',[('высота 10,8 м, фермы,',0),('мостовой кран 5 т',1)],'84','т',GOLD)
    rich(d,X0,y+10,[('Площадь больше в 2,7 раза, а металла — в 3 раза. Разницу дают высота и кран.',0)],38,W-2*X0)
    footer(im,2); return im

def factor(n,eyebrow,title,lines,tip):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,title,96)
    y=rich(d,X0,y+30,lines,44,W-2*X0)+60
    d.rounded_rectangle([X0,y,W-X0,y+230],radius=28,fill=(18,18,21),outline=(80,68,46),width=2)
    d.text((X0+44,y+34),'НА ПРАКТИКЕ',font=F(28,'700'),fill=GOLD)
    rich(d,X0+44,y+84,tip,36,W-2*X0-88)
    num=str(n-2); f=F(520); w=d.textlength(num,font=f)
    d.text((W-X0-w,H-640),num,font=f,fill=(58,50,36))
    d.text((X0,H-300),'ф а к т о р   '+num+'   и з   4',font=F(28,'700'),fill=GRY)
    footer(im,n); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'И Т О Г',[('Тоннаж зависит',WHT),('от условий',GOLD)],96)
    y=rich(d,X0,y+40,[('Пролёт, высота, снег и кран — четыре фактора, которые решают, сколько металла нужно каркасу.',0)],46,W-2*X0)+70
    for k,t in enumerate(['Пролёт','Высота','Снег','Кран'],1):
        d.text((X0,y),f'{k}',font=F(56),fill=GOLD); d.text((X0+80,y+6),t,font=F(48),fill=WHT); y+=86
    y+=40
    rich(d,X0,y,[('Поэтому цену ангара',0),('честно назвать только после расчёта',1),('под ваши условия.',0)],44,W-2*X0)
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Р А С С Ч И Т А Е М',[('Сколько металла',WHT),('нужно вашему',WHT),('ангару',GOLD)],84)
    y=rich(d,X0,y+20,[('Напишите размеры, высоту, город и нужен ли кран. В смете покажем тоннаж по позициям.',0)],42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

slides=[cover(),s2(),
 factor(3,'Ф А К Т О Р   1',[('Пролёт',GOLD)],[('Чем шире ангар без колонн внутри, тем мощнее',0),('фермы или балки',1),('на каждой раме.',0)],[('Пролёт 24 м вместо 18 м — тяжелее каждая из рам по всей длине здания.',0)]),
 factor(4,'Ф А К Т О Р   2',[('Высота',GOLD)],[('Выше колонны — длиннее металл, сильнее давит ветер,',0),('больше связей.',1)],[('Склад высотой 10,8 м: колонны и стойки — 29 т из 84.',0)]),
 factor(5,'Ф А К Т О Р   3',[('Снег',GOLD)],[('Каждая рама держит снег с кровли. Москва и Петербург — III снеговой район:',0),('150 кг на каждый м²',1),('кровли.',0)],[('Севернее район выше, и тот же ангар потребует больше металла.',0)]),
 factor(6,'Ф А К Т О Р   4',[('Кран',GOLD)],[('Кран-балка добавляет',0),('подкрановые балки',1),('и усиливает колонны.',0)],[('Склад с краном 5 т: подкрановые балки — около 7 т, колонны из прочной стали С355.',0)]),
 s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
print('ok')
