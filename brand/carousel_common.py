"""Общие функции для новых каруселей (стиль как у carousel_ot)."""
import os
from PIL import Image, ImageDraw, ImageEnhance
ROOT=os.path.dirname(os.path.abspath(__file__))+'/..'
src=open(ROOT+'/brand/carousel_ot.py').read().split('\nshutil.copy(')[0].split('\ndef s2():')[0]
g={'__file__':ROOT+'/brand/carousel_ot.py'}; exec(compile(src,'ot','exec'),g)
F,W,H,GOLD,WHT,TXT,GRY,X0,BG1,RED=[g[k] for k in 'F W H GOLD WHT TXT GRY X0 BG1 RED'.split()]
background,footer,rich,head,mark,bullets=[g[k] for k in 'background footer rich head mark bullets'.split()]
BOX=(18,18,21); EDGE=(80,68,46)

def cover(eyebrow,lines,sub,size=96):
    im=background()
    hang=Image.open(ROOT+'/brand/source/angar.jpg').convert('RGB').crop((0,0,1024,740))
    fg=hang.resize((W,int(hang.height*W/hang.width)),Image.LANCZOS); fg=ImageEnhance.Brightness(fg).enhance(0.75)
    m=Image.new('L',fg.size,0); md=ImageDraw.Draw(m)
    for y in range(fg.height): md.line([(0,y),(W,y)],fill=int(255*max(0,min(1,(fg.height-y)/260))*min(1,y/120+0.3)))
    im.paste(fg,(0,560),m); d=ImageDraw.Draw(im)
    d.text((X0,96),eyebrow,font=F(26,'700'),fill=GOLD); y=150
    for t,c in lines:
        d.text((X0,y),t,font=F(size),fill=c); y+=size+14
    rich(d,X0,y+20,[(sub,0)],38,900)
    footer(im,1); return im

def checks(n,eyebrow,title,intro,items,tip=None,ts=90,num=None):
    im=background(); d=ImageDraw.Draw(im)
    if num:
        f=F(520); w=d.textlength(num,font=f); d.text((W-X0-w,H-600),num,font=f,fill=(48,42,31))
    y=head(d,eyebrow,title,ts)
    if intro: y=rich(d,X0,y+30,intro,44,W-2*X0)+30
    y+=20
    for ok,t in items:
        mark(d,X0,y+4,ok); y=max(rich(d,X0+70,y,t,40,W-2*X0-70),y+60)+32
    if tip:
        y+=10; d.rounded_rectangle([X0,y,W-X0,y+200],radius=28,fill=BOX,outline=EDGE,width=2)
        d.text((X0+44,y+30),'СОВЕТ',font=F(28,'700'),fill=GOLD)
        rich(d,X0+44,y+78,tip,36,W-2*X0-88)
    footer(im,n); return im

def cta(n,eyebrow,title,text):
    im=background(); d=ImageDraw.Draw(im)
    y=head(d,eyebrow,title,90)
    y=rich(d,X0,y+20,text,42,W-2*X0)+80
    d.text((X0,y),'Нужно построить ангар?',font=F(52),fill=WHT); d.text((X0,y+70),'Пишите в директ',font=F(52),fill=GOLD)
    d.text((X0,y+190),'Сохраните, чтобы не потерять',font=F(30,'700'),fill=GRY)
    footer(im,n,last=True); return im

def save(slides,out):
    os.makedirs(out,exist_ok=True)
    for k,s in enumerate(slides,1): s.convert('RGB').save(out+f'{k:02d}.jpg',quality=93)
