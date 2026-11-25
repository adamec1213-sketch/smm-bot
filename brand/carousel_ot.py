"""Карусель №2 «Ангар „от 3 000 ₽/м²“: что не входит в цену» — 8 слайдов."""
import os, shutil
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0]
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(src,'v2','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1'.split()]
background,footer,rich=g['background'],g['footer'],g['rich']
OUT=ROOT+'/drafts/carousel_ot/'; os.makedirs(OUT,exist_ok=True)
RED=g['CRANE']; THEME=g['THEME']

def head(d,eyebrow,lines,size=80):
    d.text((X0,96),eyebrow,font=F(26,'700'),fill=GOLD); y=150
    for t,c in lines: d.text((X0,y),t,font=F(size),fill=c); y+=int(size*1.16)
    return y

def mark(d,x,y,ok):
    if ok:
        d.rounded_rectangle([x,y,x+44,y+44],radius=12,fill=GOLD); d.line([(x+11,y+23),(x+19,y+32),(x+33,y+13)],fill=BG1,width=5)
    else:
        d.rounded_rectangle([x,y,x+44,y+44],radius=12,outline=RED,width=3); d.line([(x+13,y+13),(x+31,y+31)],fill=RED,width=5); d.line([(x+31,y+13),(x+13,y+31)],fill=RED,width=5)

def bullets(d,y,items,size=42,gap=34):
    for b in items:
        d.rounded_rectangle([X0,y+12,X0+22,y+34],radius=6,fill=GOLD); y=rich(d,X0+46,y,b,size,W-2*X0-46)+gap
    return y

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Ч Т О   З А   Ц И Ф Р О Й',[('Что обычно',WHT),('стоит за «от»',GOLD)])
    y=rich(d,X0,y+20,[('Низкую цену в рекламе почти всегда считают',0),('за минимальную комплектацию.',1)],42,W-2*X0)+50
    y=bullets(d,y,[[('Только',0),('металлокаркас',1),('— без стен и кровли',0)],
                   [('Цена',0),('без монтажа',1),('и без доставки',0)],
                   [('Минимальная',0),('высота и пролёт',1)],
                   [('Цена за м²',0),('каркаса,',1),('а не готового здания',0)]])
    rich(d,X0,y+20,[('Проверяли сайты подрядчиков Москвы и Петербурга — так написано мелким шрифтом.',0)],30,W-2*X0)
    footer(im,2); return im

def s3():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Ч Е Г О   Н Е Т   В   Ц Е Н Е   « О Т »',[('Что придётся',WHT),('доплатить',GOLD)])+30
    for t in ['Проект (КЖ, КМ, КМД)','Фундамент и пол','Стены и кровля из сэндвич-панелей','Фасонные элементы и водосток','Ворота и окна','Доставка на объект','Монтаж с краном и техникой']:
        mark(d,X0,y,False); d.text((X0+70,y+2),t,font=F(40,'700'),fill=WHT); y+=84
    rich(d,X0,y+30,[('Каждая строка —',0),('отдельный счёт',1),('уже после подписания договора.',0)],36,W-2*X0)
    footer(im,3); return im

def s4():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С А М А Я   Д О Р О Г А Я   Ч А С Т Ь',[('Фундамент',GOLD),('и пол',WHT)],96)
    y=rich(d,X0,y+30,[('В смете на ангар фундамент и пол часто —',0),('самая крупная статья.',1),('А в цену «от» они не входят почти никогда.',0)],44,W-2*X0)+60
    y=bullets(d,y,[[('Разработка и',0),('вывоз грунта',1)],[('Ростверк',1),('или сваи под колонны',0)],[('Бетонная плита пола',1),('с армированием',0)],[('Песчаная и щебёночная',0),('подушка',1)]])
    footer(im,4); return im

def s5():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   С Р А В Н И В А Т Ь   С М Е Т Ы',[('5 правил',GOLD),('сравнения',WHT)])+30
    rules=[('1','Одинаковые площадь, высота и пролёт'),('2','Цена за готовое здание, а не за каркас'),('3','Полный список работ по статьям'),('4','Кто монтирует и чья техника'),('5','Что НЕ входит — списком, письменно')]
    for n,t in rules:
        d.text((X0,y),n,font=F(64),fill=GOLD); rich(d,X0+80,y+8,[(t,1)],44,W-2*X0-80); y+=150
    footer(im,5); return im

def s6():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К Р А С Н Ы Е   Ф Л А Г И',[('Когда смета',WHT),('вырастет',GOLD)])+30
    for t in ['«Точную цену скажем после фундамента»','В смете нет списка работ — одна строка «под ключ»','Не написано, что не входит в цену','Нет срока и графика работ','Гарантия только на словах']:
        mark(d,X0,y+4,False); yy=rich(d,X0+70,y,[(t,1)],42,W-2*X0-70); y=max(yy,y+60)+44
    footer(im,6); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   Д Е Л А Е М   М Ы',[('Смета без',WHT),('сюрпризов',GOLD)])+30
    for t in ['Все работы по статьям — от проекта до монтажа','Цена за готовое здание','Что не входит — списком, сразу в КП','Срок и порядок оплаты — в КП','Гарантия — в договоре']:
        mark(d,X0,y+4,True); yy=rich(d,X0+70,y,[(t,1)],42,W-2*X0-70); y=max(yy,y+60)+44
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'О С Т А Л И С Ь   В О П Р О С Ы ?',[('Пришлите смету',WHT),('другого',WHT),('подрядчика',GOLD)],84)
    y=rich(d,X0,y+20,[('Покажем, что в неё не вошло, и посчитаем свою —',0),('по статьям.',1)],46,W-2*X0)+90
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

shutil.copy(ROOT+'/drafts/plan_covers/02.jpg',OUT+'01.jpg')
slides=[Image.open(OUT+'01.jpg').convert('RGBA'),s2(),s3(),s4(),s5(),s6(),s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(4*300+50,2*375+30),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%4)*310,10+(k//4)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
