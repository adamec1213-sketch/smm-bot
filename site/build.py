#!/usr/bin/env python3
"""Сборка сайта РСК «Поколения» в папку docs/ (её публикует GitHub Pages).

    python3 site/build.py

Тексты страниц — в site/pages.py, общий стиль — site/site.css,
калькулятор — site/kp/ (config.js: ссылка на таблицу и контакты).
"""
import json, os, shutil, html
from pages import PAGES, CONTACTS, BASE

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '..', 'docs')

ICON = {
 'calc': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2.5" width="14" height="19" rx="2.5"/><path d="M8.5 6.5h7M8.5 11h.01M12 11h.01M15.5 11h.01M8.5 14.5h.01M12 14.5h.01M15.5 14.5h.01M8.5 18h.01M12 18h3.5"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 4.2 2 2 0 0 1 3.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L7 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'tg': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.9 4.3 18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1 9.3-8.4c.4-.4-.1-.6-.6-.2L6 13.5l-4.9-1.5c-1.1-.3-1.1-1.1.2-1.6L20.5 3c.9-.3 1.7.2 1.4 1.3z"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 6 9 7 9-7"/></svg>',
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9.5"/><path d="m8 12.5 2.8 2.8L16.5 9.5"/></svg>',
 'smeta': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2.5H6.5a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8.5 13h7M8.5 17h4.5"/></svg>',
 'eng': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V10l7-6 7 6v11"/><path d="M9.5 21v-6h5v6"/></svg>',
 'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9.5"/><path d="M12 6.5V12l3.5 2"/></svg>',
 'shield': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5 4 5.5v6c0 5 3.4 8.8 8 10 4.6-1.2 8-5 8-10v-6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/></svg>',
 'sklad': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 21V8.5L12 3l9.5 5.5V21"/><path d="M6.5 21v-8h11v8M6.5 16.5h11"/></svg>',
 'ceh': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 21V11l5 3V11l5 3V11l5 3V4h4v17z"/><path d="M6.5 17.5h2M11 17.5h2M15.5 17.5h2"/></svg>',
 'angar': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 21V12a9.5 9 0 0 1 19 0v9"/><path d="M7.5 21v-7h9v7"/></svg>',
 'shop': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 9.5 5 3.5h14l1.5 6M3.5 9.5h17v1.5a3 3 0 0 1-5.7 1.3 3 3 0 0 1-5.6 0A3 3 0 0 1 3.5 11z"/><path d="M5 13.5V21h14v-7.5"/></svg>',
 'office': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4.5" y="2.5" width="15" height="19" rx="1.5"/><path d="M8.5 7h2M13.5 7h2M8.5 11h2M13.5 11h2M8.5 15h2M13.5 15h2M10.5 21.5v-3h3v3"/></svg>',
 'car': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17.5H3.5V12l2-5h13l2 5v5.5H19"/><path d="M3.5 12h17"/><circle cx="7.5" cy="17.5" r="2"/><circle cx="16.5" cy="17.5" r="2"/></svg>',
 'sport': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.8 2.6 4.2 5.8 4.2 9.5s-1.4 6.9-4.2 9.5M12 2.5C9.2 5.1 7.8 8.3 7.8 12s1.4 6.9 4.2 9.5"/></svg>',
 'bc': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21.5h18M5.5 21.5V8l6.5-5 6.5 5v13.5"/><path d="M9.5 10.5h5M9.5 14h5M9.5 17.5h5"/></svg>',
 'panel': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5.5h18v4H3zM3 9.5h18v4H3zM3 13.5h18v4H3z"/><path d="M7 5.5v12"/></svg>',
 'beam': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4.5h18M3 19.5h18M12 4.5v15M8 4.5v2M16 4.5v2M8 17.5v2M16 17.5v2"/></svg>',
 'truss': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 17.5h20L12 6.5z"/><path d="m7 17.5 2.5-5.5L12 17.5l2.5-5.5L17 17.5"/></svg>',
 'stairs': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20.5h5v-5h5v-5h5v-5h3"/></svg>',
 'roof': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 9.5 12 4l9.5 5.5M5 8v12.5M19 8v12.5"/></svg>',
 'gear': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/></svg>',
 'truck': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 5.5h12.5v10H1.5zM14 9.5h4.5l3 3.5v2.5H14"/><circle cx="6" cy="17.5" r="2"/><circle cx="17.5" cy="17.5" r="2"/></svg>',
 'fire': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21.5c4 0 7-2.8 7-6.8 0-4.4-3.8-6.6-5-11.2-2.8 2-4 4.5-3.6 7.2-1.4-.6-2.2-1.8-2.4-3.2C6.3 9.4 5 11.8 5 14.7c0 4 3 6.8 7 6.8z"/></svg>',
}

NAV = [('angary/', 'Ангары под ключ'), ('sendvich-paneli/', 'Сэндвич-панели'),
       ('metallokonstrukcii/', 'Металлоконструкции'), ('#obekty', 'Объекты'), ('#kontakty', 'Контакты')]


def page(p):
    depth = p['path'].count('/')
    up = BASE if p.get('abs') else '../' * depth     # 404.html открывается по любому адресу — ссылки абсолютные
    C = CONTACTS
    def nav_href(h):
        return up + h if (up or not h.startswith('#')) else h
    nav = ''.join(f'<a href="{nav_href(h)}"{" aria-current=\"page\"" if h == p["path"] else ""}>{t}</a>' for h, t in NAV)
    drop = ''.join(f'<a href="{nav_href(h)}">{t}</a>' for h, t in NAV)
    canon = BASE + p['path']
    ld = json.dumps(p.get('ld') or {}, ensure_ascii=False) if p.get('ld') else ''
    org = json.dumps({
        "@context": "https://schema.org", "@type": "GeneralContractor", "name": "РСК «Поколения»",
        "url": BASE, "logo": BASE + "assets/img/logo.jpg", "image": BASE + "assets/img/hero.jpg",
        "telephone": C['phone_raw'], "email": C['email'], "foundingDate": "2011",
        "areaServed": ["Москва", "Московская область", "Санкт-Петербург", "Ленинградская область"],
        "sameAs": [C['instagram'], C['telegram']]}, ensure_ascii=False)
    fab = '' if p.get('no_fab') else f'''<div class="fab"><a class="cta" href="{up}kp/{p.get('kp_q','')}">{ICON['calc']}Рассчитать стоимость</a><a class="cta tel" href="tel:{C['phone_raw']}" aria-label="Позвонить">{ICON['phone']}</a></div>'''
    body = p['body'](up, ICON)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(p['title'])}</title>
<meta name="description" content="{html.escape(p['desc'])}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(p['title'])}">
<meta property="og:description" content="{html.escape(p['desc'])}">
<meta property="og:image" content="{BASE}assets/img/{p.get('og','hero')}.jpg">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="ru_RU">
<meta name="theme-color" content="#0b0b0c">
<link rel="icon" href="{up}assets/img/logo.jpg">
<link rel="preload" href="{up}assets/fonts/Montserrat-800.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="{up}assets/site.css">
{p.get('head','')}<script type="application/ld+json">{org}</script>
{f'<script type="application/ld+json">{ld}</script>' if ld else ''}
</head>
<body class="{'' if p.get('no_fab') else 'has-fab'}">
<header class="site-head noprint"><div class="in">
  <a class="brand" href="{up or './'}"><img src="{up}assets/img/logo.jpg" alt="" width="42" height="42"><span><b>РСК «Поколения»</b><small>Генподряд под ключ</small></span></a>
  <nav class="nav" aria-label="Основное меню">{nav}</nav>
  <a class="head-tel" href="tel:{C['phone_raw']}">{C['phone']}</a>
  <a class="cta sm cta-head" href="{up}kp/">Рассчитать стоимость</a>
  <details class="menu"><summary aria-label="Меню"><i></i></summary><div class="drop">{drop}<a href="tel:{C['phone_raw']}">{C['phone']}</a><a class="cta" href="{up}kp/">{ICON['calc']}Рассчитать стоимость</a></div></details>
</div></header>
<main>
{body}
</main>
<footer class="site-foot noprint"><div class="in">
  <div class="cols">
    <div><a class="brand" href="{up or './'}"><img src="{up}assets/img/logo.jpg" alt="" width="42" height="42"><span><b style="color:var(--txt)">РСК «Поколения»</b><small>Коммерческая недвижимость под ключ</small></span></a>
      <p style="margin-top:16px">Склады, цеха, ангары и коммерческие здания в Москве, Санкт-Петербурге и областях. Строим с 2011 года.</p></div>
    <div><h4>Услуги</h4><a href="{up}angary/">Ангары под ключ</a><a href="{up}sendvich-paneli/">Сэндвич-панели</a><a href="{up}metallokonstrukcii/">Металлоконструкции</a><a href="{up}kp/">Калькулятор стоимости</a></div>
    <div><h4>Компания</h4><a href="{up}#obekty">Объекты</a><a href="{up}#etapy">Этапы работ</a><a href="{up}#voprosy">Вопросы</a><a href="{up}politika/">Политика конфиденциальности</a></div>
    <div><h4>Контакты</h4><a href="tel:{C['phone_raw']}">{C['phone']}</a><a href="mailto:{C['email']}">{C['email']}</a><a href="{C['telegram']}" target="_blank" rel="noopener">Telegram</a><a href="{C['instagram']}" target="_blank" rel="noopener">Instagram @prorab.artem</a></div>
  </div>
  <div class="bottom"><span>© 2011–2026 РСК «Поколения»</span><span>Информация на сайте не является публичной офертой</span></div>
</div></footer>
{fab}
{p.get('foot','')}
</body>
</html>
'''


def main():
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
    urls = []
    for p in PAGES:
        d = os.path.join(OUT, p['path'])
        os.makedirs(d, exist_ok=True)
        name = p.get('file', 'index.html')
        with open(os.path.join(d, name), 'w', encoding='utf-8') as f:
            f.write(page(p))
        if not p.get('noindex'):
            urls.append(BASE + p['path'])
    with open(os.path.join(OUT, 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w') as f:
        f.write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print('Собрано страниц:', len(PAGES))


if __name__ == '__main__':
    main()
