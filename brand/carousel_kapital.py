"""Карусель «Капитальный ангар или нет» — 9 слайдов 1080x1350 в фирменном стиле."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
OUT=ROOT+'/drafts/carousel_kapital/'; os.makedirs(OUT,exist_ok=True)
W,H=1080,1350; GOLD=(217,176,94); WHT=(245,242,236); GRY=(170,170,170); BG=(14,15,18)
def F(sz,w='800'): return ImageFont.truetype(ROOT+f'/brand/fonts/Montserrat-{w}.ttf',sz)
hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
logo=Image.open(ROOT+'/brand/logo.jpg').convert('RGB')
mark=logo.crop((180,120,1820,1240)); a=mark.convert('L').point(lambda v:255 if v>90 else 0)
markA=Image.new('RGBA',mark.size,GOLD+(0,)); markA.putalpha(a)

def base(dim=0.18):
    bg=hang.resize((int(hang.width*H/hang.height),H)); x=(bg.width-W)//2
    bg=bg.crop((x,0,x+W,H)).filter(ImageFilter.GaussianBlur(18))
    bg=ImageEnhance.Brightness(bg).enhance(dim)
    return bg.convert('RGBA')

def footer(im,n):
    m=markA.resize((64,int(64*markA.height/markA.width)),Image.LANCZOS); im.alpha_composite(m,(72,H-112))
    d=ImageDraw.Draw(im); d.text((150,H-96),'ПОКОЛЕНИЯ',font=F(26,'700'),fill=GOLD)
    t=f'{n} / 9'; d.text((W-72-d.textlength(t,font=F(26,'500')),H-96),t,font=F(26,'500'),fill=GRY)

def wrap(d,text,font,maxw):
    out=[]
    for para in text.split('\n'):
        line=''
        for w in para.split(' '):
            t=(line+' '+w).strip()
            if d.textlength(t,font=font)<=maxw: line=t
            else: out.append(line); line=w
        out.append(line)
    return out

def para(d,x,y,text,font,fill,maxw,lh=1.3):
    for ln in wrap(d,text,font,maxw):
        d.text((x,y),ln,font=font,fill=fill); y+=int(font.size*lh)
    return y

# 1 обложка
fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS)
im=base(0.35); msk=Image.new('L',fg.size,255); md=ImageDraw.Draw(msk)
for i in range(160): v=int(255*i/160); md.line([(0,fg.height-1-i),(W,fg.height-1-i)],fill=v)
im.paste(fg,(0,0),msk); d=ImageDraw.Draw(im)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
for y in range(500,H): od.line([(0,y),(W,y)],fill=(0,0,0,int(235*min(1,(y-500)/350))))
im=Image.alpha_composite(im,ov); d=ImageDraw.Draw(im)
d.rectangle([72,690,212,698],fill=GOLD)
y=720
for t,c in [('ВАШ АНГАР —',WHT),('КАПИТАЛЬНЫЙ',GOLD),('ИЛИ НЕТ?',WHT)]:
    d.text((72,y),t,font=F(96),fill=c); y+=110
para(d,72,y+20,'6 признаков, на которые смотрят суд и Росреестр',F(38,'500'),WHT,900)
d.text((W-72-d.textlength('листайте »',font=F(30,'700')),H-96),'листайте »',font=F(30,'700'),fill=GOLD)
m=markA.resize((64,int(64*markA.height/markA.width)),Image.LANCZOS); im.alpha_composite(m,(72,H-112)); ImageDraw.Draw(im).text((150,H-96),'ПОКОЛЕНИЯ',font=F(26,'700'),fill=GOLD)
im.convert('RGB').save(OUT+'01.jpg',quality=93)

# 2 почему важно
im=base(); d=ImageDraw.Draw(im)
d.text((72,150),'ПОЧЕМУ ЭТО ВАЖНО',font=F(30,'700'),fill=GOLD)
para(d,72,210,'Суд и Росреестр смотрят не на материал стен, а на признаки. От ответа зависит:',F(54,'800'),WHT,936,1.22)
y=520
for t in ['нужно ли разрешение на строительство','можно ли зарегистрировать ангар в ЕГРН','есть ли риск признания самовольной постройкой и сноса']:
    d.rectangle([72,y+18,84,y+30],fill=GOLD); y=para(d,112,y,t,F(42,'500'),WHT,880)+34
footer(im,2); im.convert('RGB').save(OUT+'02.jpg',quality=93)

signs=[('01','Заглублённый фундамент',['Ленточный или плитный фундамент с котлованом — прочная связь с землёй','Сваи с ростверком под каркасом — тоже довод за капитальность','Площадка или короткие анкеры без фундамента — некапитальный']),
('02','Неразборный каркас',['Колонны забетонированы в фундамент или вварены в закладные','Нельзя разобрать и собрать заново без ущерба — ключевой признак','Болтовой каркас, который можно перевезти, — довод за некапитальность']),
('03','Капитальные стены',['Кирпич, бетон, монолит — признак капитального здания','Сэндвич-панели или тент сами по себе статус не решают','Главное — фундамент и каркас']),
('04','Стационарные сети',['Врезка в водопровод, канализацию или газ','Капитальный ввод электричества','Одно подключение к электросети ангар капитальным не делает']),
('05','Проект и разрешение',['Капитальный ангар строят по проекту и разрешению — ст. 51 ГрК РФ','Без разрешения — риск самовольной постройки и сноса, ст. 222 ГК РФ']),
('06','Учёт в ЕГРН',['Ангар ставят на кадастровый учёт и регистрируют право собственности','Его можно продать, заложить, внести в уставный капитал'])]
for i,(num,head,pts) in enumerate(signs):
    im=base(); d=ImageDraw.Draw(im)
    d.text((72,110),num,font=F(220,'800'),fill=GOLD)
    d.text((72,380),'ПРИЗНАК',font=F(30,'700'),fill=GRY)
    y=para(d,72,430,head,F(70,'800'),WHT,936,1.15)+40
    d.rectangle([72,y,212,y+8],fill=GOLD); y+=50
    for t in pts:
        d.rectangle([72,y+18,84,y+30],fill=GOLD); y=para(d,112,y,t,F(40,'500'),WHT,880)+30
    footer(im,i+3); im.convert('RGB').save(OUT+f'{i+3:02d}.jpg',quality=93)

# 9 серая зона + призыв
im=base(0.25); d=ImageDraw.Draw(im)
d.polygon([(72,230),(132,130),(192,230)],outline=GOLD,width=8); d.text((124,160),'!',font=F(56),fill=GOLD)
d.text((72,270),'СЕРАЯ ЗОНА',font=F(30,'700'),fill=GOLD)
y=para(d,72,320,'Винтовые сваи: суды решают по-разному',F(58,'800'),WHT,936,1.18)
y=para(d,72,y+20,'Статус ангара лучше определить до стройки, а не в суде.',F(40,'500'),GRY,936)
d.rectangle([72,y+50,W-72,y+54],fill=(60,60,60)); y+=110
y=para(d,72,y,'Не уверены в своём случае?',F(48,'800'),WHT,936)
d.text((72,y+10),'Напишите',font=F(48,'800'),fill=WHT); x=72+d.textlength('Напишите ',font=F(48,'800'))
d.text((x,y+10),'«РАСЧЁТ»',font=F(48,'800'),fill=GOLD); d.text((72,y+72),'в директ',font=F(48,'800'),fill=WHT)
para(d,72,y+160,'Посчитаем смету «всё включено» — от\u00a035\u00a0000\u00a0₽/м²',F(38,'500'),WHT,936)
footer(im,9); im.convert('RGB').save(OUT+'09.jpg',quality=93)

# превью-лист
sheet=Image.new('RGB',(3*360+40,3*450+40),(30,30,30))
for k in range(9):
    t=Image.open(OUT+f'{k+1:02d}.jpg').resize((350,437),Image.LANCZOS); sheet.paste(t,(10+(k%3)*360+5,10+(k//3)*450+5))
sheet.save(OUT+'00_preview.jpg',quality=90); print('ok')
