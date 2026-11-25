"""Карусель «Онлайн-калькулятор vs смета» — 8 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_calc/'; os.makedirs(OUT,exist_ok=True)

def cover():
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y-60)/380))*min(1,y/180)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),'К А Л Ь К У Л Я Т О Р',font=F(26,'700'),fill=GOLD); y=150
    for t,c in [('Онлайн —',WHT),('одна цифра,',WHT),('смета — другая',GOLD)]:
        d.text((X0,y),t,font=F(84),fill=c); y+=98
    rich(d,X0,y+20,[('Почему так бывает',0)],38,900)
    footer(im,1); return im

def card(n,eyebrow,title,lines,tip=None,num=None,ts=90):
    im=background(); d=ImageDraw.Draw(im)
    if num:
        f=F(520); w=d.textlength(num,font=f); d.text((W-X0-w,H-600),num,font=f,fill=((236,227,210) if g['THEME']=='light' else (48,42,31)))
    y=head(d,eyebrow,title,ts)
    y=rich(d,X0,y+30,lines,44,W-2*X0)+60
    if tip:
        d.rounded_rectangle([X0,y,W-X0,y+230],radius=28,fill=((255,255,255) if g['THEME']=='light' else (18,18,21)),outline=((226,214,192) if g['THEME']=='light' else (80,68,46)),width=2)
        d.text((X0+44,y+34),'ЧТО ЭТО ЗНАЧИТ',font=F(28,'700'),fill=GOLD)
        rich(d,X0+44,y+84,tip,36,W-2*X0-88)
    footer(im,n); return im

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'М Ы   П Р О В Е Р И Л И',[('313 расчётов',WHT),('в онлайн-',GOLD),('конструкторе',GOLD)],84)
    y=rich(d,X0,y+30,[('Меняли пролёт от 12 до 36 м, высоту от 4 до 14 м, снег, грунт, ветер, кран. Сравнивали, что меняется в результате.',0)],42,W-2*X0)+50
    rich(d,X0,y,[('Вот 4 вещи, из-за которых онлайн-цифра',0),('ниже реальной сметы.',1)],42,W-2*X0)
    footer(im,2); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   П О Л Ь З О В А Т Ь С Я',[('Калькулятор —',WHT),('для порядка цифр',GOLD)],84)+30
    for t in [[('Онлайн-расчёт подходит, чтобы',0),('прикинуть бюджет.',1)],
              [('Для решения нужна',0),('смета по проекту:',1),('снег вашего района, грунт, кран, ворота, полы.',0)],
              [('Сравнивайте сметы',0),('по объёмам:',1),('тонны металла, м² панелей, м³ бетона.',0)]]:
        mark(d,X0,y+4,True); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+40
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'П О С Ч И Т А Е М',[('Смету под',WHT),('ваш участок',GOLD)],90)
    y=rich(d,X0,y+20,[('Пришлите размеры, город и задачу. Покажем все объёмы по статьям.',0)],42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

slides=[cover(),s2(),
 card(3,'П Р И Ч И Н А   1',[('Снег один',WHT),('на всех',GOLD)],[('Снеговой район в списке выбрать можно, но расчёт берёт',0),('одно число нагрузки,',1),('которое стоит в соседнем поле. Город ни на что не влияет.',0)],[('Если не поменять число вручную, каркас посчитают не под ваш снег.',0)],'1'),
 card(4,'П Р И Ч И Н А   2',[('Балка не проходит,',WHT),('а металл есть',GOLD)],[('На пролётах 24–36 м балки перегружены',0),('в несколько раз.',1),('Конструктор пишет предупреждение, но тоннаж всё равно считает по этой балке.',0)],[('Реальный каркас для такого пролёта будет заметно тяжелее и дороже.',0)],'2',76),
 card(5,'П Р И Ч И Н А   3',[('Колонны',WHT),('легче, чем есть',GOLD)],[('Вес колонны в расчёте взят',0),('почти вдвое меньше,',1),('чем по её же размерам сечения.',0)],[('Масса колонн занижена примерно на 45 %, а с ней и металл в итоге.',0)],'3'),
 card(6,'П Р И Ч И Н А   4',[('Грунт',WHT),('«средний»',GOLD)],[('Без данных изысканий для любого грунта берётся',0),('одно и то же значение.',1),('Ветер и сейсмика в подборе каркаса не участвуют.',0)],[('На слабом грунте фундамент выйдет больше, чем в онлайн-расчёте.',0)],'4'),
 s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
print('ok')
