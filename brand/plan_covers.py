"""Обложки 9 каруселей из плана (drafts/plan-karuseli-noyabr-dekabr.md)."""
import os, importlib.util
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
spec=importlib.util.spec_from_file_location('v2',ROOT+'/brand/carousel_kapital_v2.py')
OUT=ROOT+'/drafts/plan_covers/'; os.makedirs(OUT,exist_ok=True)
# переиспользуем стиль из v2 без повторного рендера карусели
src=open(ROOT+'/brand/carousel_kapital_v2.py').read().split('\nslides = [')[0]
g={'__file__':ROOT+'/brand/carousel_kapital_v2.py'}; exec(compile(src,'v2','exec'),g)
F,W,H,GOLD,WHT,TXT,X0,background,footer,rich,MARK=[g[k] for k in 'F W H GOLD WHT TXT X0 background footer rich MARK'.split()]
hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
COV=[('20.11','Ц Е Н А',[('Ангар 1440 м²:',WHT),('куда уходят',WHT),('деньги',GOLD)],'Разбираем реальную смету по статьям'),
('24.11','Ц Е Н А',[('Ангар',WHT),('«от 3 000 ₽/м²»',GOLD),('— втрое дороже',WHT)],'Что не входит в цену «от» и как сравнивать сметы'),
('27.11','В Ы Б О Р',[('Холодный',WHT),('или тёплый',GOLD),('ангар?',WHT)],'Что выбрать под ваш бизнес в Москве и Петербурге'),
('01.12','Д О Г О В О Р',[('7 вопросов',GOLD),('подрядчику',WHT),('до подписи',WHT)],'Которые сэкономят вам деньги и нервы'),
('04.12','Ф У Н Д А М Е Н Т',[('Плита, лента',WHT),('или сваи?',GOLD)],'Какой фундамент нужен вашему ангару'),
('08.12','З А К О Н',[('Разрешение',GOLD),('на ангар:',WHT),('5 шагов',WHT)],'От участка до регистрации в ЕГРН'),
('11.12','С Е З О Н',[('Строить ангар',WHT),('зимой?',GOLD)],'Да, если знать 5 правил'),
('15.12','О Ш И Б К И',[('5 ошибок',GOLD),('на кровле',WHT)],'За которые заказчик платит дважды'),
('18.12','Э Т А П Ы',[('Ангар под ключ:',WHT),('9 этапов',GOLD)],'От участка до запуска объекта')]
files=[]
for k,(date,eyebrow,title,sub) in enumerate(COV,1):
    im=background()
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),eyebrow,font=F(26,'700'),fill=GOLD)
    y=150
    for t,c in title:
        f=F(96 if len(t)<15 else 84); d.text((X0,y),t,font=f,fill=c); y+=f.size+14
    rich(d,X0,y+24,[(sub,0)],38,900)
    footer(im,1)
    p=OUT+f'{k:02d}.jpg'; im.convert('RGB').save(p,quality=92); files.append(p)
sh=Image.new('RGB',(3*360+40,3*450+40),(255,255,255))
for k,p in enumerate(files):
    t=Image.open(p).resize((350,437),Image.LANCZOS); sh.paste(t,(15+(k%3)*360,15+(k//3)*450))
    dd=ImageDraw.Draw(sh); dd.rounded_rectangle([265+(k%3)*360,25+(k//3)*450,355+(k%3)*360,57+(k//3)*450],radius=16,fill=GOLD); dd.text((278+(k%3)*360,29+(k//3)*450),COV[k][0],font=F(22,'800'),fill=(12,13,16))
sh.save(OUT+'00_setka.jpg',quality=90); print('ok')
