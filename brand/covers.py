from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os; ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'

OUT=ROOT+'/drafts/covers/'
W,H=1080,1920
GOLD=(217,176,94); WHT=(255,255,255)
def F(sz,w='800'): return ImageFont.truetype(ROOT+f'/brand/fonts/Montserrat-{w}.ttf',sz)
man=Image.open(ROOT+'/brand/source/prorab.jpg').convert('RGB')
hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
logo=Image.open(ROOT+'/brand/logo.jpg').convert('RGB')
# logo mark -> gold with alpha from luminance
mark=logo.crop((180,120,1820,1240)); g=mark.convert('L').point(lambda v:255 if v>90 else 0)
markA=Image.new('RGBA',mark.size,GOLD+(0,)); markA.putalpha(g)

def fit_bg(src, box_y=None, zoom=None):
    # blurred fill + sharp image fitted by width
    bg=src.resize((int(src.width*H/src.height),H)); x=(bg.width-W)//2; bg=bg.crop((x,0,x+W,H)).filter(ImageFilter.GaussianBlur(40))
    bg=ImageEnhance.Brightness(bg).enhance(0.45)
    fg=src.resize((W,int(src.height*W/src.width)),Image.LANCZOS)
    y=box_y if box_y is not None else (H-fg.height)//2
    # soft edges
    m=Image.new('L',fg.size,255); md=ImageDraw.Draw(m)
    for i in range(120):
        a=int(255*i/120); md.line([(0,i),(fg.width,i)],fill=a); md.line([(0,fg.height-1-i),(fg.width,fg.height-1-i)],fill=a)
    bg.paste(fg,(0,y),m); return bg

def cover_portrait(src,crop):
    p=src.crop(crop); p=p.resize((W,int(p.height*W/p.width)),Image.LANCZOS)
    y=(p.height-H)//2 if p.height>H else 0
    if p.height<H:
        return fit_bg(src.crop(crop))
    return p.crop((0,y,W,y+H))

def shade(im,start=900,maxa=235):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for y in range(start,H):
        a=int(maxa*min(1,(y-start)/500)); d.line([(0,y),(W,y)],fill=(0,0,0,a))
    for y in range(0,420):
        a=int(160*(1-y/420)); d.line([(0,y),(W,y)],fill=(0,0,0,a))
    return Image.alpha_composite(im.convert('RGBA'),ov)

def brand(im,y=280):
    m=markA.resize((130,int(130*markA.height/markA.width)),Image.LANCZOS)
    im.alpha_composite(m,(W//2-65,y)); d=ImageDraw.Draw(im)
    f=F(30,'700'); t='П О К О Л Е Н И Я'; d.text(((W-d.textlength(t,font=f))/2,y+m.height+16),t,font=f,fill=GOLD)
    return im

def lines(im,y,spec,center=True):
    d=ImageDraw.Draw(im)
    for txt,sz,col,wt in spec:
        f=F(sz,wt); w=d.textlength(txt,font=f); d.text(((W-w)/2,y),txt,font=f,fill=col); y+=int(sz*1.18)
    return y

def accent(im,y,w=140):
    ImageDraw.Draw(im).rectangle([(W-w)//2,y,(W+w)//2,y+8],fill=GOLD)

# 1 Прораб
im=shade(cover_portrait(man,(0,60,500,1024)),start=780); im=brand(im,y=1490)
accent(im,1060)
lines(im,1100,[('ДЕШЕВЛЕ —',92,WHT,'800'),('НЕ ЗНАЧИТ',92,WHT,'800'),('КАЧЕСТВЕННО',92,GOLD,'800')])
im.convert('RGB').save(OUT+'1_prorab.jpg',quality=92)

# 2 Цифра
im=shade(fit_bg(hang,box_y=420),start=1000); im=brand(im)
y=lines(im,1180,[('АНГАР ПОД КЛЮЧ',54,WHT,'700')]); 
y=lines(im,y+10,[('от 20 000 ₽/м²',112,GOLD,'800')]); accent(im,y+40); lines(im,y+70,[('смета без доплат',54,WHT,'500')])
im.convert('RGB').save(OUT+'2_cifra.jpg',quality=92)

# 3 Вопрос
h2=hang.crop((60,120,980,700))
im=shade(cover_portrait(h2,(200,0,700,580)),start=850); im=brand(im)
accent(im,1130)
lines(im,1170,[('СКОЛЬКО СТОИТ',84,WHT,'800'),('АНГАР 1000 м²',84,GOLD,'800'),('В 2026 ГОДУ?',84,WHT,'800')])
im.convert('RGB').save(OUT+'3_vopros.jpg',quality=92)

# 4 Рубрика
im=shade(cover_portrait(hang,(0,100,520,740)),start=800); im=brand(im); d=ImageDraw.Draw(im)
f=F(40,'700'); t='ОШИБКИ НА СТРОЙКЕ'; w=d.textlength(t,font=f)
d.rounded_rectangle([(W-w)/2-36,1110,(W+w)/2+36,1110+76],radius=38,outline=GOLD,width=4); d.text(((W-w)/2,1124),t,font=f,fill=GOLD)
lines(im,1240,[('ПОТЕРЯЛИ',96,WHT,'800'),('50 000 ₽',110,GOLD,'800'),('НА КРОВЛЕ',96,WHT,'800')])
im.convert('RGB').save(OUT+'4_rubrika.jpg',quality=92)

# сетка и обзор
names=['1_prorab.jpg','2_cifra.jpg','3_vopros.jpg','4_rubrika.jpg']
files=names+['2_cifra.jpg','1_prorab.jpg','4_rubrika.jpg','3_vopros.jpg','1_prorab.jpg']
cw,ch=360,480; gr=Image.new('RGB',(cw*3+8,ch*3+8),(255,255,255))
for k,fn in enumerate(files):
    t=Image.open(OUT+fn); top=(H-1440)//2; t=t.crop((0,top,W,top+1440)).resize((cw-4,ch-4),Image.LANCZOS); gr.paste(t,((k%3)*cw+4,(k//3)*ch+4))
gr.save(OUT+'0_setka.jpg',quality=90)
labels=['1. Прораб','2. Цифра','3. Вопрос','4. Рубрика']
sw,sh=420,746; sh_=Image.new('RGB',(sw*4+100,sh+110),(18,18,18)); sd=ImageDraw.Draw(sh_)
for k,fn in enumerate(names):
    sh_.paste(Image.open(OUT+fn).resize((sw,sh),Image.LANCZOS),(20+k*(sw+20),90)); sd.text((20+k*(sw+20),28),labels[k],font=F(38,'700'),fill=GOLD)
sh_.save(OUT+'0_varianty.jpg',quality=90)
print('ok')
