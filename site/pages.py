"""Тексты и разметка страниц сайта. Источники: презентация компании (ноябрь 2026),
профиль .agents/product-marketing.md, карусели Instagram, калькулятор владельца."""
import os

# Адрес сайта. Когда подключите свой домен — замените и пересоберите.
BASE = 'https://adamec1213-sketch.github.io/smm-bot/'

CONTACTS = {
    'phone': '+7 981 908-22-97', 'phone_raw': '+79819082297',
    'email': 'rsk-47@bk.ru',
    'telegram': 'https://t.me/spbpokoleniya',
    'instagram': 'https://instagram.com/prorab.artem',
}
C = CONTACTS
HERE = os.path.dirname(os.path.abspath(__file__))


def img(up, name, alt, cls='', eager=False, sizes='100vw'):
    return (f'<img class="{cls}" src="{up}assets/img/{name}.jpg" '
            f'srcset="{up}assets/img/{name}-s.jpg 800w, {up}assets/img/{name}.jpg 1600w" sizes="{sizes}" '
            f'alt="{alt}"{"" if eager else " loading=\"lazy\""} decoding="async">')


# ---------------------------------------------------------------- общие блоки
TYPES = [('sklad', 'Склады и логистические комплексы'), ('ceh', 'Производственные здания и цеха'),
         ('angar', 'Холодные и тёплые ангары'), ('shop', 'Торговые павильоны и шоурумы'),
         ('office', 'Административно-бытовые блоки (АБК)'), ('car', 'Автосервисы, СТО, мойки'),
         ('sport', 'ФОКи и падел-корты'), ('bc', 'Бизнес-центры')]

STAGES = [('Анализ и ТЗ', 'Участок, задачи бизнеса, ограничения. Риски снимаем здесь, а не на стройке.'),
          ('Эскиз и бюджет', 'Объёмно-планировочное решение и первая оценка стоимости.'),
          ('Рабочий проект и экспертиза', 'КЖ, КМ, расчёт нагрузок под ваш регион.'),
          ('Разрешительная документация', 'Разрешение на строительство по ст. 51 ГрК РФ.'),
          ('Фиксированная смета и график', 'Каждая позиция с объёмом и ценой, календарный план с контрольными точками.'),
          ('Строительство и надзор', 'Своя команда на объекте, отчётность по графику.'),
          ('Подключение к сетям', 'Вводы электричества, воды, канализации.'),
          ('Ввод в эксплуатацию', 'Разрешение на ввод (ст. 55 ГрК РФ), технический план, регистрация в ЕГРН.'),
          ('Гарантия', 'Отвечаем за результат и после сдачи объекта.')]

QC = [('Нулевой цикл', ['Геодезическая разбивка', 'Грунты и основание', 'Бетонные работы: класс бетона, уход']),
      ('Несущий каркас и ограждения', ['Металлоконструкции: монтаж, узлы, антикоррозийная защита', 'Монолитные работы: опалубка, армирование', 'Ограждающие конструкции: примыкания, плоскостность']),
      ('Инженерные системы и тепловой контур', ['Герметичность и изоляция', 'Узлы примыканий и проходки', 'Инженерные вводы и разводки']),
      ('Фасад, кровля и безопасность', ['Кровельный пирог и водоотвод', 'Фасадные системы: крепление, стыки', 'Противопожарные конструкции']),
      ('Финиш и подготовка к эксплуатации', ['Внутренние сети: ВК, ЭС, вентиляция', 'Исполнительная документация', 'Комплексное опробование систем'])]

OBJECTS = [
    dict(tag='Москва', name='Бизнес-центр', photos=[('bc-fasad', 'Фасад бизнес-центра из сэндвич-панелей'), ('bc-montazh', 'Монтаж металлокаркаса с автокраном'), ('bc-zal', 'Зал на этапе отделки')],
         rows=[('Адрес', 'ул. Новопетровская, д. 1, стр. 1'), ('Площадь', '1 720 м²'), ('Сроки', 'февраль 2025 — апрель 2026')]),
    dict(tag='Санкт-Петербург', name='Бизнес-инкубатор, 3 корпуса', photos=[('inkub-1', 'Металлокаркасы корпусов бизнес-инкубатора, вид с дрона'), ('inkub-2', 'Стройплощадка бизнес-инкубатора'), ('inkub-4', 'Каркас корпуса на свайном поле')],
         rows=[('Адрес', 'ул. Евграфова, д. 27'), ('Объём', '3 корпуса'), ('Сроки', 'декабрь 2024 — декабрь 2026')]),
    dict(tag='Санкт-Петербург', name='Строительство храма', photos=[('hram-1', 'Строительство храма, вид с дрона'), ('hram-2', 'Башенный кран на строительстве храма'), ('hram-3', 'Храм и башенный кран')],
         rows=[('Техника', 'башенный кран TGM RGT 13-40'), ('Период работ', '2022–2026')]),
    dict(tag='Тендер', name='Физкультурно-оздоровительный комплекс', photos=[('fok', 'Проект ФОКа на экранах')], one=True,
         rows=[('Программа', '«Спорт — в каждый город»'), ('Площадь', '970 м²'), ('Сроки', 'сентябрь 2025 — декабрь 2026')]),
]

FAQ = {
 'kapital': ('Ангар капитальный или нет?',
   '<p>Суд и Росреестр смотрят не на материал стен, а на признаки капитального здания:</p><ul>'
   '<li>заглублённый фундамент: ленточный, плитный или сваи с ростверком;</li>'
   '<li>неразборный каркас: колонны забетонированы или вварены в закладные;</li>'
   '<li>стационарные сети: водопровод, канализация, газ, капитальный ввод электричества;</li>'
   '<li>проект и разрешение на строительство (ст. 51 ГрК РФ);</li>'
   '<li>учёт в ЕГРН и право собственности.</li></ul>'
   '<p>Сэндвич-панели сами по себе статус не решают, главное — фундамент и каркас. Капитальный ангар можно продать, заложить и внести в уставный капитал.</p>'),
 'razr': ('Нужно ли разрешение на строительство?',
   '<p>Для капитального здания — да. Путь такой:</p><ul>'
   '<li>проверить вид разрешённого использования участка;</li>'
   '<li>инженерные изыскания (геология, геодезия) и проект, в ряде случаев — экспертиза;</li>'
   '<li>разрешение на строительство в администрации (ст. 51 ГрК РФ), стройка начинается только после него;</li>'
   '<li>разрешение на ввод (ст. 55 ГрК РФ) и технический план;</li>'
   '<li>кадастровый учёт и регистрация права в ЕГРН.</li></ul>'
   '<p>Капитальный ангар без разрешения — самовольная постройка (ст. 222 ГК РФ). Ведём объект по всем шагам.</p>'),
 'teplo': ('Тёплый или холодный ангар?',
   '<p>Тип выбирают по тому, что и кто будет внутри зимой. Если там работают люди или хранится товар, которому нужен плюс, — тёплый: металлокаркас и сэндвич-панели с минватой. Минвата не горит, это важно для склада и производства.</p>'
   '<p>Холодный (каркас и профлист без утепления) подходит для хранения техники или стройматериалов, где мороз не страшен.</p>'),
 'fund': ('Сваи или монолитный фундамент?',
   '<p>Решают три вещи: геология участка, нагрузки и статус здания. Фундамент без геологии — выбор «на глаз»: изыскания покажут тип грунта, его несущую способность и грунтовые воды.</p>'
   '<p>Монолитный ростверк или лента под колонны с бетонной плитой пола — сильный довод за капитальность. Ангар на винтовых сваях суды признают по-разному. Если нужна регистрация в ЕГРН, кредит или продажа как недвижимости, обсуждаем фундамент до проекта.</p>'),
 'ot': ('Почему у других «от» дешевле?',
   '<p>Низкую цену в рекламе обычно считают за минимальную комплектацию: только металлокаркас без стен и кровли, без монтажа и доставки, на минимальную высоту и пролёт. Мы проверяли сайты подрядчиков Москвы и Петербурга: так написано мелким шрифтом.</p>'
   '<p>Фундамент и пол в смете на ангар часто самая крупная статья, а в цену «от» они почти никогда не входят. Пришлите смету другого подрядчика — покажем, что в неё не вошло.</p>'),
 'vopr': ('Что спросить у подрядчика до подписи договора?',
   '<ul><li>Что входит в смету — по статьям?</li><li>Что не входит в цену?</li><li>Какой срок и что будет, если сорвёте?</li>'
   '<li>Как устроена оплата?</li><li>Какая гарантия и на что?</li><li>Кто будет монтировать?</li><li>Какие объекты уже построили?</li></ul>'
   '<p>Ответим на каждый вопрос письменно и по статьям.</p>'),
 'kp': ('Насколько точен расчёт в калькуляторе?',
   '<p>Калькулятор считает по той же смете, по которой инженеры готовят КП: металл, панели, фундамент, пол, техника, доставка. Это предварительный расчёт по введённым параметрам. Окончательную цену фиксируем в договоре после уточнения ТЗ, геологии и участка.</p>'),
}


def faq(keys, I):
    items = ''.join(f'<details><summary>{FAQ[k][0]}</summary><div class="a">{FAQ[k][1]}</div></details>' for k in keys)
    return items


def faq_ld(keys):
    import re
    def clean(h): return re.sub(r'<[^>]+>', ' ', h).replace('  ', ' ').strip()
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": FAQ[k][0], "acceptedAnswer": {"@type": "Answer", "text": clean(FAQ[k][1])}} for k in keys]}


def final_cta(up, I, kp_q=''):
    return f'''
<section class="s final" id="kontakty">
  {img(up, 'kaska', '', 'bgimg')}
  <div class="in">
    <span class="kicker">Контакты</span>
    <h2>Строим так, чтобы ваш бизнес <em>начал зарабатывать раньше</em></h2>
    <p class="sub">Один подрядчик на весь цикл под ключ: меньше рисков, быстрее запуск, предсказуемый результат. Отправьте вводные — подготовим расчёт, проконсультируем и предложим оптимальное решение.</p>
    <div class="contacts">
      <div class="cbox">
        <p>Звоните или пишите</p>
        <a class="big" href="tel:{C['phone_raw']}">{C['phone']}</a>
        <p><a href="mailto:{C['email']}" style="text-decoration:none">{C['email']}</a></p>
        <div class="links">
          <a class="chip" href="{C['telegram']}" target="_blank" rel="noopener">{I['tg']}Telegram</a>
          <a class="chip" href="{C['instagram']}" target="_blank" rel="noopener">{I['ig']}Instagram</a>
          <a class="chip" href="mailto:{C['email']}">{I['mail']}Почта</a>
        </div>
      </div>
      <div class="cbox" style="background:linear-gradient(135deg,#F8EFDD,#FFFFFF 70%);border-color:#E9D6B0">
        <p>Хотите сначала понять бюджет?</p>
        <div style="font-size:22px;font-weight:800;margin:6px 0 10px">Посчитайте стоимость сами за 2 минуты</div>
        <p style="margin-bottom:20px">КП с разбивкой по позициям откроется сразу, его можно скачать в PDF.</p>
        <a class="cta" href="{up}kp/{kp_q}">{I['calc']}Рассчитать стоимость</a>
      </div>
    </div>
  </div>
</section>'''


def objects(up, I, only=None):
    out = []
    for o in OBJECTS if only is None else [OBJECTS[i] for i in only]:
        ph = ''.join(img(up, n, a, sizes='(max-width:860px) 100vw, 50vw') for n, a in o['photos'])
        dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in o['rows'])
        out.append(f'<article class="obj"><div class="ph{" one" if o.get("one") else ""}">{ph}</div>'
                   f'<div class="tx"><span class="tag">{o["tag"]}</span><h3>{o["name"]}</h3><dl>{dl}</dl></div></article>')
    return '<div class="objs">' + ''.join(out) + '</div>'


def stages(I):
    return '<ol class="steps">' + ''.join(f'<li><div><b>{t}</b><span>{d}</span></div></li>' for t, d in STAGES) + '</ol>'


def promo(up, I, kp_q=''):
    return f'''
<section class="s tight"><div class="in">
  <div class="promo">
    <div>
      <span class="kicker">Калькулятор</span>
      <h2>Цена здания <em>за 2 минуты</em></h2>
      <p class="sub">Калькулятор считает по нашей смете: те же позиции и цены, по которым инженеры готовят коммерческие предложения.</p>
      <ol>
        <li><b>1</b><span>Укажите размеры, фундамент, пол, ворота и окна.</span></li>
        <li><b>2</b><span>Выберите: без НДС или с НДС 22 %.</span></li>
        <li><b>3</b><span>Получите КП с объёмами и ценой каждой позиции. Его можно скачать в PDF.</span></li>
      </ol>
      <a class="cta" href="{up}kp/{kp_q}">{I['calc']}Рассчитать стоимость</a>
    </div>
    <div class="kp-mock" aria-hidden="true">
      <div class="h">Коммерческое предложение <small>КП № 261120</small></div>
      <div class="r"><span>Изготовление металлоконструкций</span><i></i></div>
      <div class="r"><span>Монтаж металлоконструкций</span><i class="w"></i></div>
      <div class="r"><span>Сэндвич-панели стен и кровли</span><i></i></div>
      <div class="r"><span>Фундамент и плита пола</span><i class="w"></i></div>
      <div class="r"><span>Ворота, окна, двери</span><i></i></div>
      <div class="r"><span>Доставка, автокран, подъёмник</span><i class="w"></i></div>
      <div class="t"><span>Итого</span><i></i></div>
    </div>
  </div>
</div></section>'''


# ---------------------------------------------------------------- главная
def home(up, I):
    types = ''.join(f'<div class="type">{I[i]}{t}</div>' for i, t in TYPES)
    qc = ''.join(f'<div class="tile"><h3>{I["check"]}{t}</h3><ul>{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for t, xs in QC)
    return f'''
<section class="hero">
  {img(up, 'hero', 'Металлокаркас здания и строительная каска', 'bg', eager=True)}
  <div class="in">
    <span class="kicker">Генподряд в Москве и Санкт-Петербурге</span>
    <h1>Коммерческая недвижимость под ключ</h1>
    <div class="dim" aria-hidden="true"><i></i><span class="lg">от технического задания до ввода в эксплуатацию</span><span class="sm">от ТЗ до ввода в эксплуатацию</span><i></i></div>
    <p class="lead">Склады, цеха, ангары и автосервисы. Одна команда, прозрачная смета с объёмом и ценой каждой позиции и вся ответственность за результат на нас.</p>
    <div class="acts">
      <a class="cta" href="{up}kp/">{I['calc']}Рассчитать стоимость</a>
      <a class="cta line" href="tel:{C['phone_raw']}">{I['phone']}{C['phone']}</a>
    </div>
    <div class="stats">
      <div class="stat"><b>15+ лет</b><span>строим с 2011 года</span></div>
      <div class="stat"><b>200+</b><span>завершённых объектов</span></div>
      <div class="stat"><b>9 этапов</b><span>полный цикл генподряда</span></div>
    </div>
  </div>
</section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Чем занимаемся</span><h2>Строим, поставляем, <em>изготавливаем</em></h2></div></div>
  <div class="dirs">
    <a class="dir" href="{up}angary/">{img(up, 'inkub-4', '', sizes='(max-width:900px) 100vw, 33vw')}<div class="t"><h3>Ангары и здания под ключ</h3><p>Проект, фундамент, металлокаркас, сэндвич-панели, ворота и монтаж в одной смете.</p><span class="go">Подробнее {I['arrow']}</span></div></a>
    <a class="dir" href="{up}sendvich-paneli/">{img(up, 'bc-fasad', '', sizes='(max-width:900px) 100vw, 33vw')}<div class="t"><h3>Сэндвич-панели</h3><p>Стеновые и кровельные панели с минватой. Привезём на объект и смонтируем.</p><span class="go">Подробнее {I['arrow']}</span></div></a>
    <a class="dir" href="{up}metallokonstrukcii/">{img(up, 'bc-montazh', '', sizes='(max-width:900px) 100vw, 33vw')}<div class="t"><h3>Металлоконструкции</h3><p>Каркасы, фермы, колонны, лестницы и навесы. По вашим чертежам или с разработкой КМД.</p><span class="go">Подробнее {I['arrow']}</span></div></a>
  </div>
</div></section>

<section class="s alt tight"><div class="in">
  <div class="head-row"><div><span class="kicker">Что строим</span><h2>Коммерческие и промышленные <em>объекты</em></h2><p class="sub">От проекта до готового здания с подключёнными сетями.</p></div></div>
  <div class="types">{types}</div>
</div></section>

<section class="s light"><div class="in">
  <div class="head-row"><div><span class="kicker">Риски снимаем на этапе ТЗ</span><h2>Не теряете деньги <em>на чужих ошибках</em></h2>
  <p class="sub">Для собственников и инвесторов, которым нужен предсказуемый объект по срокам, бюджету и качеству. Ваша задача — получать доход от объекта, а не управлять строительными рисками.</p></div></div>
  <div class="grid4">
    <div class="tile"><div class="ic">{I['smeta']}</div><h3>Прозрачная смета</h3><p>Каждая позиция с объёмом и ценой. Полный контроль над бюджетом без внезапных счетов.</p></div>
    <div class="tile"><div class="ic">{I['eng']}</div><h3>Инженерная проработка</h3><p>Прорабатываем ТЗ и узлы до монтажа, а не исправляем ошибки на объекте.</p></div>
    <div class="tile"><div class="ic">{I['clock']}</div><h3>Управление сроками</h3><p>Календарный план, контрольные точки и регулярная отчётность.</p></div>
    <div class="tile"><div class="ic">{I['shield']}</div><h3>Генподряд под ключ</h3><p>Один контур ответственности: от проекта до ввода в эксплуатацию.</p></div>
  </div>
</div></section>

{promo(up, I)}

<section class="s" id="etapy"><div class="in">
  <div class="head-row"><div><span class="kicker">Полный цикл генподряда</span><h2>9 этапов <em>от ТЗ до гарантии</em></h2></div></div>
  <div class="grid2" style="gap:48px;align-items:start">
    {stages(I)}
    <div><h3 style="font-size:20px;margin-bottom:16px">Контроль качества на каждом этапе</h3><div class="qc">{qc}</div></div>
  </div>
</div></section>

<section class="s alt" id="obekty"><div class="in">
  <div class="head-row"><div><span class="kicker">Действующие объекты</span><h2>Что мы строим <em>сейчас</em></h2></div>
  <a class="chip" href="{C['instagram']}" target="_blank" rel="noopener">{I['ig']}Стройка в Instagram</a></div>
  {objects(up, I)}
</div></section>

<section class="s" id="voprosy"><div class="in">
  <div class="head-row"><div><span class="kicker">Вопросы</span><h2>Что спрашивают <em>до начала стройки</em></h2></div></div>
  <div class="faq">{faq(['kapital','razr','teplo','fund','ot','vopr','kp'], I)}</div>
</div></section>
{final_cta(up, I)}'''


# ---------------------------------------------------------------- ангары
def angary(up, I):
    rows = [('Проектирование', 'КЖ, КМ, геология — пакетом.'),
            ('Фундамент', 'Винтовые сваи Ø133 с оголовками или монолитные столбчатые фундаменты с разработкой грунта.'),
            ('Пол', 'Монолитная плита с армированием и подушкой, толщина 180–300 мм. Или пол из плит ПАГ по щебню.'),
            ('Металлокаркас', 'Изготовление, окраска грунт-эмалью, доставка, монтаж с автокраном и подъёмником.'),
            ('Стены и кровля', 'Сэндвич-панели с минватой: стены 100 или 120 мм, кровля 120 или 150 мм. Фасонные элементы и расходники для монтажа.'),
            ('Водоотвод', 'Водосток и снегозадержатели.'),
            ('Проёмы', 'Секционные ворота с автоматикой, окна ПВХ, наружные металлические двери.'),
            ('Логистика', 'Доставка металла и панелей, разгрузка автокраном.')]
    table = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in rows)
    return f'''
<section class="page-hero">
  {img(up, 'inkub-1', '', 'bg', eager=True)}
  <div class="in">
    <div class="crumbs"><a href="{up}">Главная</a> / Ангары под ключ</div>
    <h1>Строительство ангаров <em>под ключ</em></h1>
    <p class="lead">Тёплые ангары и склады из металлокаркаса и сэндвич-панелей с минватой. Считаем по смете с объёмами, строим своей командой и ведём объект до ввода в эксплуатацию.</p>
    <div class="acts" style="display:flex;gap:14px;flex-wrap:wrap">
      <a class="cta" href="{up}kp/">{I['calc']}Рассчитать стоимость ангара</a>
      <a class="cta line" href="tel:{C['phone_raw']}">{I['phone']}{C['phone']}</a>
    </div>
  </div>
</section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Состав сметы</span><h2>Что входит <em>в цену ангара</em></h2>
  <p class="sub">Эти позиции калькулятор считает сразу, по размерам здания. В КП у каждой строки свой объём и цена.</p></div></div>
  <div class="scroll"><table class="table"><thead><tr><th>Раздел</th><th>Что входит</th></tr></thead><tbody>{table}</tbody></table></div>
  <p class="note">Отдельно, по запросу: топпинг пола, огнезащита металлоконструкций, перегородки, инженерные системы, подключение к сетям, благоустройство.</p>
</div></section>

<section class="s alt"><div class="in">
  <div class="head-row"><div><span class="kicker">Варианты</span><h2>Из чего <em>складывается решение</em></h2></div></div>
  <div class="grid3">
    <div class="tile"><div class="ic">{I['sklad']}</div><h3>Фундамент</h3><p>Винтовые сваи ставятся быстрее. Монолит — сильный довод за капитальность, если нужна регистрация в ЕГРН, кредит или продажа как недвижимости.</p></div>
    <div class="tile"><div class="ic">{I['beam']}</div><h3>Пол</h3><p>Бетонная плита 180, 200, 250 или 300 мм с армированием и подушкой. Плиты ПАГ — сборный вариант по щебню.</p></div>
    <div class="tile"><div class="ic">{I['panel']}</div><h3>Утепление</h3><p>Стандарт: стены 100 мм, кровля 120 мм. Усиленное: стены 120 мм, кровля 150 мм. Минвата не горит, это важно для склада и производства.</p></div>
  </div>
</div></section>

<section class="s"><div class="in split">
  <div>
    <span class="kicker">Капитальный или нет</span>
    <h2>Статус здания решают <em>фундамент и каркас</em></h2>
    <ul class="checks">
      <li><div>Заглублённый фундамент<span>Ленточный, плитный или сваи с ростверком</span></div></li>
      <li><div>Неразборный каркас<span>Колонны забетонированы или вварены в закладные</span></div></li>
      <li><div>Стационарные сети<span>Водопровод, канализация, газ, капитальный ввод электричества</span></div></li>
      <li><div>Проект и разрешение<span>Строительство по ст. 51 ГрК РФ</span></div></li>
      <li><div>Учёт в ЕГРН<span>Ангар можно продать, заложить и внести в уставный капитал</span></div></li>
    </ul>
  </div>
  {img(up, 'inkub-3', 'Монтаж металлокаркасов на свайном поле', sizes='(max-width:900px) 100vw, 50vw')}
</div></section>

{promo(up, I)}

<section class="s alt"><div class="in">
  <div class="head-row"><div><span class="kicker">Как работаем</span><h2>9 этапов <em>генподряда</em></h2></div></div>
  <div style="max-width:820px">{stages(I)}</div>
</div></section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Объекты</span><h2>Каркасные здания <em>в работе</em></h2></div></div>
  {objects(up, I, [1, 0])}
</div></section>

<section class="s alt"><div class="in">
  <div class="head-row"><div><span class="kicker">Вопросы</span><h2>Об ангарах</h2></div></div>
  <div class="faq">{faq(['kapital','fund','teplo','razr','ot','kp'], I)}</div>
</div></section>
{final_cta(up, I)}'''


# ---------------------------------------------------------------- сэндвич-панели
def paneli(up, I):
    return f'''
<section class="page-hero">
  {img(up, 'bc-fasad', '', 'bg', eager=True)}
  <div class="in">
    <div class="crumbs"><a href="{up}">Главная</a> / Сэндвич-панели</div>
    <h1>Сэндвич-панели <em>с минватой</em></h1>
    <p class="lead">Стеновые и кровельные панели для складов, цехов и ангаров. Поставим на объект и смонтируем своей бригадой.</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap">
      <a class="cta" href="{up}kp/?t=panel">{I['calc']}Рассчитать панели</a>
      <a class="cta line" href="tel:{C['phone_raw']}">{I['phone']}{C['phone']}</a>
    </div>
  </div>
</section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Что поставляем</span><h2>Панели <em>под задачу</em></h2></div></div>
  <div class="grid3">
    <div class="tile"><div class="ic">{I['panel']}</div><h3>Стеновые</h3><p>Минеральная вата, толщина 100 или 120 мм. Для тёплых складов, цехов и автосервисов.</p></div>
    <div class="tile"><div class="ic">{I['roof']}</div><h3>Кровельные</h3><p>Минеральная вата, толщина 120 или 150 мм. Считаем вместе с фасонными элементами, водостоком и снегозадержателями.</p></div>
    <div class="tile"><div class="ic">{I['gear']}</div><h3>Под заказ</h3><p>Другие толщины, панели PIR и цвет по RAL подберём по запросу.</p></div>
  </div>
</div></section>

<section class="s alt"><div class="in split">
  <div>
    <span class="kicker">Почему минвата</span>
    <h2>Тёплый контур, <em>который не горит</em></h2>
    <p class="sub">Тип здания выбирают по тому, что и кто будет внутри зимой. Если там работают люди или хранится товар, которому нужен плюс, — стены и кровля из сэндвич-панелей с минватой.</p>
    <ul class="checks">
      <li><div>Негорючий утеплитель<span>Важно для склада и производства</span></div></li>
      <li><div>Плюсовая температура зимой<span>Для людей и товара</span></div></li>
      <li><div>Готовая поверхность<span>Не нужна отделка фасада и потолка</span></div></li>
    </ul>
  </div>
  {img(up, 'bc-karkas', 'Монтаж стеновых сэндвич-панелей на каркас', sizes='(max-width:900px) 100vw, 50vw')}
</div></section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Поставка и монтаж</span><h2>От завода <em>до готовой стены</em></h2></div></div>
  <div class="grid3">
    <div class="tile"><div class="ic">{I['truck']}</div><h3>Доставка</h3><p>Привозим фурами на объект, в одну машину помещается около 250 м² панелей. Разгрузка автокраном.</p></div>
    <div class="tile"><div class="ic">{I['ceh']}</div><h3>Монтаж</h3><p>Своя бригада. В смету сразу входят расходники: герметик, саморезы, уплотнительная лента.</p></div>
    <div class="tile"><div class="ic">{I['shield']}</div><h3>Узлы и примыкания</h3><p>Фасонные элементы, примыкания и стыки проверяем на этапе контроля качества.</p></div>
  </div>
</div></section>

{promo(up, I, '?t=panel')}

<section class="s alt"><div class="in">
  <div class="head-row"><div><span class="kicker">Вопросы</span><h2>О панелях</h2></div></div>
  <div class="faq">{faq(['teplo','kp'], I)}</div>
</div></section>
{final_cta(up, I, '?t=panel')}'''


# ---------------------------------------------------------------- металлоконструкции
def mk(up, I):
    kinds = [('sklad', 'Каркасы зданий', 'Колонны, ригели, прогоны и связи для складов, цехов и ангаров.'),
             ('truss', 'Фермы и балки', 'Стропильные фермы и балки перекрытий под ваши пролёты и нагрузки.'),
             ('beam', 'Колонны', 'Колонны каркаса, фахверк, закладные детали.'),
             ('stairs', 'Лестницы и площадки', 'Лестницы, площадки обслуживания, ограждения.'),
             ('roof', 'Навесы и козырьки', 'Навесы над рампами, парковками и входами.'),
             ('gear', 'Нестандартные конструкции', 'Изделия по индивидуальным чертежам.')]
    tiles = ''.join(f'<div class="tile"><div class="ic">{I[i]}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in kinds)
    return f'''
<section class="page-hero">
  {img(up, 'bc-montazh', '', 'bg', eager=True)}
  <div class="in">
    <div class="crumbs"><a href="{up}">Главная</a> / Металлоконструкции</div>
    <h1>Металлоконструкции: <em>изготовление и монтаж</em></h1>
    <p class="lead">Каркасы зданий, фермы, колонны, лестницы и навесы. Работаем по вашим чертежам КМД или разрабатываем их сами.</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap">
      <a class="cta" href="{up}kp/?t=mk">{I['calc']}Рассчитать металлоконструкции</a>
      <a class="cta line" href="tel:{C['phone_raw']}">{I['phone']}{C['phone']}</a>
    </div>
  </div>
</section>

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Что изготавливаем</span><h2>Металл <em>для любого объекта</em></h2></div></div>
  <div class="grid3">{tiles}</div>
</div></section>

<section class="s alt"><div class="in split">
  <div>
    <span class="kicker">Как работаем</span>
    <h2>От чертежа <em>до монтажа</em></h2>
    <ul class="checks">
      <li><div>Чертежи КМД<span>Берём ваши или разрабатываем по проекту КМ</span></div></li>
      <li><div>Изготовление<span>По чертежам КМД, с узлами, пластинами и болтами</span></div></li>
      <li><div>Антикоррозийная защита<span>Окраска грунт-эмалью</span></div></li>
      <li><div>Доставка<span>Около 8,5 т металла на одну фуру, разгрузка автокраном</span></div></li>
      <li><div>Монтаж<span>Своя бригада, автокран и подъёмник</span></div></li>
    </ul>
  </div>
  {img(up, 'inkub-2', 'Монтаж металлокаркасов, вид с дрона', sizes='(max-width:900px) 100vw, 50vw')}
</div></section>

{promo(up, I, '?t=mk')}

<section class="s"><div class="in">
  <div class="head-row"><div><span class="kicker">Объекты</span><h2>Наш металл <em>на объектах</em></h2></div></div>
  {objects(up, I, [0, 1])}
</div></section>
{final_cta(up, I, '?t=mk')}'''


# ---------------------------------------------------------------- калькулятор
def read(n): return open(os.path.join(HERE, 'kp', n), encoding='utf-8').read()


def kp(up, I):
    return f'<div class="calc in" style="max-width:800px;padding-top:28px;padding-bottom:60px">\n{read("calc.html")}</div>'


# ---------------------------------------------------------------- политика
def politika(up, I):
    return f'''
<section class="s"><div class="in prose">
  <div class="crumbs"><a href="{up}">Главная</a> / Политика конфиденциальности</div>
  <h1 style="font-size:clamp(28px,4vw,40px);font-weight:800">Политика обработки персональных данных</h1>
  <p>Политика описывает, как РСК Групп обрабатывает персональные данные посетителей сайта в соответствии с Федеральным законом № 152-ФЗ «О персональных данных».</p>
  <h2>Какие данные мы получаем</h2>
  <p>Имя, номер телефона и город объекта, которые вы указываете в калькуляторе стоимости, а также параметры расчёта.</p>
  <h2>Зачем</h2>
  <p>Чтобы подготовить коммерческое предложение, связаться с вами по нему и обсудить строительство. Рекламные рассылки мы не делаем.</p>
  <h2>Как храним</h2>
  <p>Данные хранятся в защищённой таблице, доступ к ней есть только у сотрудников компании, которые готовят предложения. Мы не передаём данные третьим лицам, кроме случаев, предусмотренных законом.</p>
  <h2>Сколько храним</h2>
  <p>До достижения целей обработки или до отзыва согласия.</p>
  <h2>Как отозвать согласие</h2>
  <p>Напишите на <a href="mailto:{C['email']}">{C['email']}</a> или позвоните по телефону <a href="tel:{C['phone_raw']}">{C['phone']}</a>. Удалим данные в течение 30 дней.</p>
</div></section>'''


def notfound(up, I):
    return f'''
<section class="s"><div class="in" style="text-align:center;padding:60px 16px">
  <span class="kicker">Ошибка 404</span>
  <h2>Такой страницы <em>нет</em></h2>
  <p class="sub" style="margin:16px auto 30px">Возможно, ссылка устарела. Начните с главной или посчитайте стоимость в калькуляторе.</p>
  <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap"><a class="cta" href="{up}kp/">{I['calc']}Рассчитать стоимость</a><a class="cta line" href="{up}">На главную</a></div>
</div></section>'''


def bc(name, path):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": name, "item": BASE + path}]}


PAGES = [
    dict(path='', body=home, title='Коммерческая недвижимость под ключ в Москве и СПб — РСК Групп',
         desc='Генподряд под ключ: склады, цеха, ангары, автосервисы. Прозрачная смета, 15+ лет, 200+ объектов. Рассчитайте стоимость за 2 минуты.',
         ld=faq_ld(['kapital','razr','teplo','fund','ot','vopr','kp'])),
    dict(path='angary/', body=angary, og='inkub-1', title='Строительство ангаров под ключ в Москве и СПб — РСК Групп',
         desc='Тёплые ангары и склады из металлокаркаса и сэндвич-панелей. Смета с объёмами по каждой позиции, расчёт стоимости онлайн за 2 минуты.',
         ld=bc('Ангары под ключ', 'angary/')),
    dict(path='sendvich-paneli/', body=paneli, og='bc-fasad', kp_q='?t=panel', title='Сэндвич-панели с минватой: поставка и монтаж — РСК Групп',
         desc='Стеновые 100–120 мм и кровельные 120–150 мм сэндвич-панели с минватой. Доставка на объект, монтаж своей бригадой. Расчёт онлайн.',
         ld=bc('Сэндвич-панели', 'sendvich-paneli/')),
    dict(path='metallokonstrukcii/', body=mk, og='bc-montazh', kp_q='?t=mk', title='Изготовление и монтаж металлоконструкций — РСК Групп',
         desc='Каркасы зданий, фермы, колонны, лестницы и навесы. Разработка КМД, окраска, доставка и монтаж. Расчёт стоимости онлайн.',
         ld=bc('Металлоконструкции', 'metallokonstrukcii/')),
    dict(path='kp/', body=kp, no_fab=True, title='Калькулятор стоимости ангара — КП за 2 минуты | РСК Групп',
         desc='Рассчитайте стоимость ангара, сэндвич-панелей или металлоконструкций и сразу получите коммерческое предложение с разбивкой по позициям.',
         head=f'<style>\n{read("calc.css")}\n{read("deck.css")}</style>\n',
         foot=f'<script>\n{read("config.js")}\n</script>\n<script>\n{read("panels.js")}</script>\n<script>\n{read("deck.js")}</script>\n<script>\n{read("calc.js")}</script>'),
    dict(path='politika/', body=politika, title='Политика обработки персональных данных — РСК Групп',
         desc='Как РСК Групп обрабатывает персональные данные посетителей сайта.'),
    dict(path='', file='404.html', abs=True, noindex=True, body=notfound, title='Страница не найдена — РСК Групп',
         desc='Страница не найдена.'),
]
