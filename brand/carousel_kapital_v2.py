"""Карусель «Что делает ваш ангар капитальным» (8 слайдов) в фирменном стиле.
Иллюстрации берутся из исходных слайдов brand/source/kapital_v1/ и перекрашиваются в золото.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__)) + '/..'
SRC = ROOT + '/brand/source/kapital_v1/'
OUT = ROOT + '/drafts/carousel_kapital_v2/'
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
GOLD = (217, 176, 94)
WHT = (244, 240, 232)
TXT = (200, 195, 186)
GRY = (120, 118, 114)
BG1, BG2 = (12, 13, 16), (24, 24, 28)
X0 = 64


def F(sz, w='800'):
    return ImageFont.truetype(ROOT + f'/brand/fonts/Montserrat-{w}.ttf', sz)


logo = Image.open(ROOT + '/brand/logo.jpg').convert('RGB')
_mark = logo.crop((180, 120, 1820, 1240))
MARK = Image.new('RGBA', _mark.size, GOLD + (0,))
MARK.putalpha(_mark.convert('L').point(lambda v: 255 if v > 90 else 0))


def background():
    im = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] * (1 - k) + BG2[i] * k) for i in range(3)))
    d.ellipse([740, -260, 1340, 340], outline=(48, 44, 36), width=3)
    d.ellipse([-260, 1090, 240, 1590], outline=(40, 37, 31), width=3)
    return im


def gold_art(img):
    """Иллюстрацию — в дуотон: тёмное -> почти чёрный, светлое -> золото."""
    g = ImageOps.autocontrast(img.convert('L'), cutoff=1)
    return ImageOps.colorize(g, black=(16, 16, 19), mid=(110, 88, 50), white=(240, 214, 160))


def rounded(img, r=36):
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=255)
    out = Image.new('RGBA', img.size)
    out.paste(img, (0, 0), m)
    return out


def rich(d, x, y, segs, size, maxw, lh=1.32):
    """segs: [(текст, жирный?)]; перенос по словам с сохранением жирности."""
    words = []
    for t, b in segs:
        for i, w in enumerate(t.split(' ')):
            if w:
                words.append((w, b))
    fb, fr = F(size, '800'), F(size, '500')
    line, lines = [], []
    width = 0
    sp = d.textlength(' ', font=fr)
    for w, b in words:
        ww = d.textlength(w, font=fb if b else fr)
        if line and width + sp + ww > maxw:
            lines.append(line); line, width = [], 0
        line.append((w, b, ww)); width += (sp if len(line) > 1 else 0) + ww
    if line: lines.append(line)
    for ln in lines:
        cx = x
        for w, b, ww in ln:
            d.text((cx, y), w, font=fb if b else fr, fill=WHT if b else TXT)
            cx += ww + sp
        y += int(size * lh)
    return y


def footer(im, n, last=False):
    d = ImageDraw.Draw(im)
    d.text((X0, H - 92), f'{n}/8', font=F(28, '700'), fill=GRY)
    m = MARK.resize((56, int(56 * MARK.height / MARK.width)), Image.LANCZOS)
    tw = d.textlength('ПОКОЛЕНИЯ', font=F(24, '700'))
    x = (W - (56 + 14 + tw)) / 2
    im.alpha_composite(m, (int(x), H - 104))
    d.text((x + 70, H - 90), 'ПОКОЛЕНИЯ', font=F(24, '700'), fill=GOLD)
    if last:
        pass
    else:
        cx, cy, r = W - X0 - 36, H - 78, 36
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
        d.line([(cx - 14, cy), (cx + 12, cy)], fill=BG1, width=6)
        d.polygon([(cx + 16, cy), (cx + 2, cy - 13), (cx + 2, cy + 13)], fill=BG1)
        t = 'Листайте'
        d.text((cx - r - 18 - d.textlength(t, font=F(28, '700')), cy - 18), t, font=F(28, '700'), fill=GRY)


def pills(d, active, labels):
    x, y = X0, 76
    for i, lab in enumerate(labels, 1):
        if i == active:
            t = f'{i} · {lab}'
            w = d.textlength(t, font=F(26, '700')) + 48
            d.rounded_rectangle([x, y, x + w, y + 46], radius=23, fill=GOLD)
            d.text((x + 24, y + 7), t, font=F(26, '700'), fill=BG1)
        else:
            w = 46
            done = i < active
            d.ellipse([x, y, x + w, y + 46], outline=GOLD if not done else (90, 76, 52), width=2,
                      fill=(60, 52, 38) if done else None)
            t = str(i)
            d.text((x + (w - d.textlength(t, font=F(24, '700'))) / 2, y + 8), t, font=F(24, '700'),
                   fill=GOLD if not done else (160, 140, 100))
        x += w + 12


LABELS = ['Фундамент', 'Каркас', 'Стены', 'Сети', 'Разрешение', 'ЕГРН']
SIGNS = [
    ('Заглублённый\nфундамент', [[('Ленточный или плитный', 1), ('с котлованом — прочная связь с землёй', 0)],
                                [('Сваи с ростверком', 1), ('— тоже сильный довод за капитальность', 0)],
                                [('Без фундамента, на анкерах —', 0), ('некапитальный', 1)]]),
    ('Неразборный каркас', [[('Колонны', 0), ('забетонированы', 1), ('или', 0), ('вварены', 1), ('в закладные', 0)],
                           [('Нельзя разобрать без ущерба —', 0), ('ключевой признак', 1)],
                           [('Болтовой каркас, который можно перевезти, —', 0), ('некапитальный', 1)]]),
    ('Капитальные стены', [[('Кирпич, бетон, монолит', 1), ('— признак капитального здания', 0)],
                          [('Сэндвич-панели и тент', 1), ('сами по себе статус не решают', 0)],
                          [('Главное —', 0), ('фундамент и каркас', 1)]]),
    ('Стационарные сети', [[('Врезка в', 0), ('водопровод, канализацию, газ', 1)],
                          [('Капитальный ввод', 1), ('электричества', 0)],
                          [('Одна электросеть', 0), ('не делает', 1), ('ангар капитальным', 0)]]),
    ('Проект и разрешение', [[('Строят', 0), ('по проекту и разрешению', 1), ('— ст.\u00a051\u00a0ГрК\u00a0РФ', 0)],
                            [('Без разрешения — риск', 0), ('самовольной постройки,', 1), ('ст.\u00a0222\u00a0ГК\u00a0РФ', 0)]]),
    ('Учёт в ЕГРН', [[('Кадастровый учёт', 1), ('и регистрация права собственности', 0)],
                    [('Ангар можно', 0), ('продать, заложить', 1), ('и внести в уставный капитал', 0)]]),
]


def cover():
    im = background(); d = ImageDraw.Draw(im)
    d.text((X0, 96), 'Д Л Я   Т Е Х ,   К Т О   С Т Р О И Т   А Н Г А Р Ы', font=F(24, '700'), fill=GOLD)
    y = 150
    for t, c in [('Что делает', WHT), ('ваш ангар', WHT), ('капитальным', GOLD)]:
        d.text((X0, y), t, font=F(104), fill=c); y += 118
    y = rich(d, X0, y + 30, [('6 признаков, по которым суд и Росреестр определяют статус', 0)], 40, 900)
    src = Image.open(SRC + '01.jpg').convert('RGB')
    caps = ['Основание', 'Каркас', 'Сети']
    for i, x in enumerate([60, 390, 720]):
        tile = rounded(gold_art(src.crop((x + 14, 874, x + 286, 1090))).resize((300, 238), Image.LANCZOS), 28)
        tx = X0 + i * 324
        d.rounded_rectangle([tx - 2, 818, tx + 302, 1150], radius=30, outline=(70, 60, 42), width=2, fill=(18, 18, 21))
        im.alpha_composite(tile, (tx, 820))
        d.text((tx + 24, 1080), str(i + 1), font=F(40), fill=GOLD)
        d.text((tx + 60, 1080), caps[i], font=F(40), fill=WHT)
    footer(im, 1)
    return im


def sign(i, title, bullets):
    n = i + 1
    im = background(); d = ImageDraw.Draw(im)
    pills(d, n, LABELS)
    d.rounded_rectangle([X0, 160, X0 + 104, 226], radius=33, outline=GOLD, width=3)
    d.text((X0 + 22, 168), f'{n:02d}', font=F(42), fill=GOLD)
    y = 246
    for ln in title.split('\n'):
        d.text((X0, y), ln, font=F(76), fill=WHT); y += 88
    src = Image.open(SRC + f'{n + 1:02d}.jpg').convert('RGB')
    art = src.crop((270, 470, 810, 890))
    art = gold_art(art).resize((W - 2 * X0 - 80, int((W - 2 * X0 - 80) * 420 / 540)), Image.LANCZOS)
    top = max(y + 30, 450)
    box_h = 400
    card = Image.new('RGB', (W - 2 * X0, box_h), (16, 16, 19))
    a = art.resize((int(box_h * art.width / art.height), box_h - 40), Image.LANCZOS)
    card.paste(a, ((card.width - a.width) // 2, 20))
    im.alpha_composite(rounded(card, 36), (X0, top))
    d.rounded_rectangle([X0, top, W - X0, top + box_h], radius=36, outline=(80, 68, 46), width=2)
    y = top + box_h + 36
    for b in bullets:
        d.rounded_rectangle([X0, y + 12, X0 + 22, y + 34], radius=6, fill=GOLD)
        y = rich(d, X0 + 46, y, b, 34, W - 2 * X0 - 46) + 16
    footer(im, n + 1)
    return im


def final():
    im = background(); d = ImageDraw.Draw(im)
    d.text((X0, 96), 'О С Т А Л И С Ь   В О П Р О С Ы ?', font=F(24, '700'), fill=GOLD)
    y = 150
    for t, c in [('Поможем выбрать', WHT), ('и построить ваш', WHT), ('ангар', GOLD)]:
        d.text((X0, y), t, font=F(84), fill=c); y += 98
    y += 30
    d.rounded_rectangle([X0, y, W - X0, y + 150], radius=24, fill=(26, 25, 24))
    d.rectangle([X0, y + 24, X0 + 6, y + 126], fill=GOLD)
    rich(d, X0 + 40, y + 30, [('Серая зона — винтовые сваи:', 1), ('суды решают по-разному. Обсудим ваш случай до начала стройки.', 0)], 32, W - 2 * X0 - 80)
    y += 200
    d.text((X0, y), 'Напишите', font=F(52), fill=WHT)
    x = X0 + d.textlength('Напишите ', font=F(52))
    d.text((x, y), '«РАСЧЁТ»', font=F(52), fill=GOLD)
    d.text((X0, y + 64), 'в директ — смета «всё включено»', font=F(40, '500'), fill=TXT)
    y += 170
    dv = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    for icon, text, fnt in [('☎', '+7 981 908-22-97', dv), ('@', 'rsk-47@bk.ru', F(40))]:
        d.rounded_rectangle([X0, y, X0 + 72, y + 72], radius=18, fill=GOLD)
        d.text((X0 + 36 - d.textlength(icon, font=fnt) / 2, y + 12), icon, font=fnt, fill=BG1)
        d.text((X0 + 100, y + 6), text, font=F(50), fill=WHT); y += 96
    d.text((X0, y + 10), 'Артём, главный инженер', font=F(32, '500'), fill=GRY)
    d.text((X0, y + 60), 'Сохраните, чтобы не потерять', font=F(30, '700'), fill=GOLD)
    footer(im, 8, last=True)
    return im


slides = [cover()] + [sign(i, t, b) for i, (t, b) in enumerate(SIGNS)] + [final()]
for k, s in enumerate(slides, 1):
    s.convert('RGB').save(OUT + f'{k:02d}.jpg', quality=93)
sheet = Image.new('RGB', (4 * 300 + 50, 2 * 375 + 30), (40, 40, 40))
for k, s in enumerate(slides):
    sheet.paste(s.convert('RGB').resize((290, 362), Image.LANCZOS), (10 + (k % 4) * 310, 10 + (k // 4) * 385))
sheet.save(OUT + '00_preview.jpg', quality=90)
print('ok')
