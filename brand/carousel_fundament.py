"""Карусель №5 «Плита, лента или сваи?» — 8 слайдов. По словам владельца: чаще монолит; сваи — для некапитальных или при проблемном грунте."""
import os, shutil
from PIL import Image, ImageDraw
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
OUT=ROOT+'/drafts/carousel_fundament/'; os.makedirs(OUT,exist_ok=True)
BLUE=(120,160,190)

def s2():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К А К   В Ы Б И Р А Ю Т',[('3 вещи решают',WHT),('всё',GOLD)],96)+40
    for n,t,sub in [('1','Грунт','что под участком: песок, глина, торф, вода'),('2','Нагрузки','каркас, снег, оборудование, техника на полу'),('3','Статус','нужен ли капитальный объект с регистрацией в ЕГРН')]:
        d.text((X0,y),n,font=F(80),fill=GOLD); d.text((X0+90,y+6),t,font=F(54),fill=WHT)
        y=rich(d,X0+90,y+80,[(sub,0)],38,W-2*X0-90)+50
    footer(im,2); return im

def s3():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Ч А Щ Е   В С Е Г О   Д Е Л А Е М',[('Монолит',GOLD)],110)
    y=rich(d,X0,y+20,[('Монолитный ростверк или лента под колонны',1),('+ бетонная плита пола.',0)],48,W-2*X0)+80
    for t in ['Держит тяжёлый каркас и снег','Пол сразу — под технику и стеллажи','Капитальный объект — можно в ЕГРН','Работает на большинстве грунтов']:
        mark(d,X0,y+6,True); y=max(rich(d,X0+70,y,[(t,1)],48,W-2*X0-70),y+60)+56
    footer(im,3); return im

def s4():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'К О Г Д А   С В А И',[('Сваи —',WHT),('в двух случаях',GOLD)],90)+40
    for n,t,items in [('1','Некапитальный ангар',['Быстровозводимый, сборно-разборный','Не нужна регистрация как недвижимости']),
                      ('2','Сложный грунт',['Слабый грунт или торф','Высокие грунтовые воды, перепады рельефа'])]:
        d.rounded_rectangle([X0,y,W-X0,y+330],radius=30,fill=(18,18,21),outline=(80,68,46),width=2)
        d.text((X0+40,y+30),n,font=F(64),fill=GOLD); d.text((X0+110,y+40),t,font=F(46),fill=WHT)
        yy=y+130
        for it in items:
            d.rounded_rectangle([X0+40,yy+12,X0+62,yy+34],radius=6,fill=GOLD); yy=rich(d,X0+86,yy,[(it,0)],38,W-2*X0-130)+20
        y+=370
    footer(im,4); return im

def s5():
    im=background(); d=ImageDraw.Draw(im)
    d.polygon([(X0,236),(X0+70,116),(X0+140,236)],outline=GOLD,width=8); d.text((X0+58,150),'!',font=F(64),fill=GOLD)
    y=head(d,'',[],80)
    d.text((X0,270),'С Е Р А Я   З О Н А',font=F(28,'700'),fill=GOLD)
    y=rich(d,X0,320,[('Винтовые сваи и статус ангара',1)],66,W-2*X0,1.15)+40
    y=rich(d,X0,y,[('Суды решают по-разному:',0),('ангар на винтовых сваях',1),('могут признать и капитальным, и нет.',0)],44,W-2*X0)+50
    y=rich(d,X0,y,[('Нужна регистрация в ЕГРН, кредит или продажа как недвижимости?',0),('Обсуждаем фундамент до проекта.',1)],44,W-2*X0)
    footer(im,5); return im

def s6():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Н А Ч А Л А',[('Геология',GOLD),('участка',WHT)],100)
    y=rich(d,X0,y+20,[('Фундамент без геологии —',0),('выбор «на глаз».',1)],46,W-2*X0)+60
    y=bullets(d,y,[[('Покажет',0),('тип грунта',1),('и его несущую способность',0)],[('Найдёт',0),('грунтовые воды',1)],[('Подскажет,',0),('монолит или сваи',1)]],44,40)
    footer(im,6); return im

def s7():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'С Р А В Н Е Н И Е',[('Монолит',GOLD),('vs сваи',BLUE)])+40
    cx=[X0,X0+370,X0+650]
    d.text((cx[1],y),'Монолит',font=F(32,'700'),fill=GOLD); d.text((cx[2],y),'Сваи',font=F(32,'700'),fill=BLUE); y+=70
    for r in [('Когда','чаще всего','особые случаи'),('Грунт','нормальный','сложный'),('Капитальность','да','серая зона'),('Пол','сразу','отдельно'),('Скорость','дольше','быстрее')]:
        d.line([(X0,y-16),(W-X0,y-16)],fill=(50,48,44),width=2)
        d.text((cx[0],y),r[0],font=F(36,'700'),fill=WHT); d.text((cx[1],y),r[1],font=F(36,'500'),fill=TXT); d.text((cx[2],y),r[2],font=F(36,'500'),fill=TXT); y+=100
    footer(im,7); return im

def s8():
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,'Н Е   У В Е Р Е Н Ы ?',[('Пришлите участок',WHT),('и задачу',GOLD)],84)
    y=rich(d,X0,y+20,[('Подберём фундамент под ваш грунт и нагрузки и посчитаем смету',0),('по статьям.',1)],46,W-2*X0)+90
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,8,last=True); return im

shutil.copy(ROOT+'/drafts/plan_covers/05.jpg',OUT+'01.jpg')
slides=[Image.open(OUT+'01.jpg').convert('RGBA'),s2(),s3(),s4(),s5(),s6(),s7(),s8()]
for k,s in enumerate(slides,1): s.convert('RGB').save(OUT+f'{k:02d}.jpg',quality=93)
sheet=Image.new('RGB',(4*300+50,2*375+30),(40,40,40))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((290,362),Image.LANCZOS),(10+(k%4)*310,10+(k//4)*385))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
