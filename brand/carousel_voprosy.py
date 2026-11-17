"""Карусель №4 «7 вопросов подрядчику до подписи» — 9 слайдов."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
N=9
v2=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0].replace("f'{n}/8'","f'{n}/%d'"%N)
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(v2,'v2','exec'),g)
ot=open(ROOT+'/brand/carousel_ot.py').read(); ot=ot[ot.index('RED='):ot.index('def s2():')]
exec(compile(ot,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark=[g[k] for k in 'background footer rich head mark'.split()]
OUT=ROOT+'/drafts/carousel_voprosy/'; os.makedirs(OUT,exist_ok=True)
hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))

def cover():
    im=background()
    fg=ImageEnhance.Brightness(hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS)).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    y=head(d,'Д О Г О В О Р',[('7 вопросов',GOLD),('подрядчику',WHT),('до подписи',WHT)],96)
    rich(d,X0,y+20,[('Которые сэкономят вам деньги и нервы',0)],38,900)
    footer(im,1); return im

Q=[('Что входит в смету — по статьям?','Каждая работа и материал — отдельной строкой: от проекта до монтажа','Одна строка «ангар под ключ» без расшифровки'),
('Что НЕ входит в цену?','Список исключений письменно — сразу в коммерческом предложении','«Потом посмотрим», «по ходу решим»'),
('Какой срок и что будет, если сорвёте?','Срок и график этапов — в договоре','«Как пойдёт», срок только на словах'),
('Как устроена оплата?','Аванс и оплата по этапам — по актам выполненных работ','Вся сумма вперёд'),
('Какая гарантия и на что?','Срок гарантии и что она покрывает — прописано в договоре','Гарантия «на словах»'),
('Кто будет монтировать?','Называет, кто отвечает на объекте и чья техника','«Найдём бригаду», ответственного нет'),
('Какие объекты уже построили?','Показывает свои объекты, можно приехать посмотреть','Только картинки из интернета')]

def qslide(i,q,good,bad):
    n=i+1; im=background(); d=ImageDraw.Draw(im)
    d.text((X0,96),'В О П Р О С',font=F(26,'700'),fill=GOLD)
    d.text((X0,130),f'{n:02d}',font=F(150),fill=GOLD)
    y=rich(d,X0,330,[(q,1)],68,W-2*X0,1.16)+70
    for ok,lab,t,col in [(True,'ХОРОШИЙ ОТВЕТ',good,GOLD),(False,'КРАСНЫЙ ФЛАГ',bad,RED)]:
        top=y
        mark(d,X0+40,y+40,ok); d.text((X0+106,y+44),lab,font=F(32,'700'),fill=col)
        yy=rich(d,X0+40,y+116,[(t,0)],46,W-2*X0-80)
        d.rounded_rectangle([X0,top,W-X0,yy+40],radius=28,outline=(80,68,46) if ok else (110,60,50),width=2)
        y=yy+80
    footer(im,n+1); return im

def final():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'П Р О В Е Р Ь Т Е   Н А С',[('Задайте эти',WHT),('7 вопросов',GOLD),('и нам',WHT)],90)
    y=rich(d,X0,y+20,[('Ответим на каждый —',0),('письменно и по статьям.',1)],46,W-2*X0)+90
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,N,last=True); return im

slides=[cover()]+[qslide(i,*q) for i,q in enumerate(Q)]+[final()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(3*300+40,3*375+40),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%3)*310,10+(k//3)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
