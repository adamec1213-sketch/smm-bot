/**
 * РСК Групп — КП с сайта по калькулятору владельца.
 *
 * Код вставляется в ту же Google Таблицу, где лежит калькулятор
 * (листы «Ввод», «Смета», «График», «Справочник»…).
 * Сайт присылает параметры → скрипт подставляет их в лист «Ввод»,
 * таблица пересчитывает «Смету» по своим формулам → скрипт забирает строки
 * сметы, возвращает исходные значения «Ввода», пишет заявку в лист «Заявки»
 * и отдаёт КП сайту.
 *
 * Подключение — см. kp/ИНСТРУКЦИЯ.md.
 */

const NOTIFY_EMAIL = 'rsk-47@bk.ru';   // письмо о новой заявке ('' — не присылать)
const KP_DAYS = 10;                    // сколько дней действует КП
const LEADS = 'Заявки';
const HEADERS = ['Дата', '№ КП', 'Имя', 'Телефон', 'Город', 'Направление', 'Объект',
  'Параметры', 'Сумма, ₽', '₽/м²', 'Состав КП', 'Источник', 'Статус', 'Комментарий'];

// Поля листа «Ввод», которые заполняет клиент на сайте.
// label — подпись строки в столбце A (значение пишется в столбец B), name — как поле называется в КП.
// list — допустимые значения (как в выпадающих списках файла); min/max — границы для чисел.
// Поле, которое клиент не заполнил, не трогаем: остаётся значение из таблицы.
// Наценку, проектирование, надбавки, γf, массу колонн и % узлов сайт НЕ меняет — это настройки владельца.
const YN = ['да', 'нет'];
const FIELDS = {
  L:         { label: 'Длина здания, м', name: 'Длина', unit: 'м', min: 6, max: 300 },
  W:         { label: 'Ширина (пролёт), м', name: 'Ширина (пролёт)', unit: 'м', min: 12, max: 36 },
  H:         { label: 'Высота до карниза, м', name: 'Высота до карниза', unit: 'м', min: 4, max: 14 },
  step:      { label: 'Шаг рам, м', name: 'Шаг рам', unit: 'м', min: 3, max: 12 },
  slope:     { label: 'Уклон кровли, градусы', name: 'Уклон кровли', unit: '°', min: 1, max: 30 },
  snowReg:   { label: 'Снеговой район (СП 20.13330)', name: 'Снеговой район', list: ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'] },
  snowMan:   { label: 'Снеговая нагрузка вручную, кПа (пусто = по району)', name: 'Снеговая нагрузка', unit: 'кПа', min: 0.3, max: 8 },
  steel:     { label: 'Марка стали', name: 'Марка стали', list: ['С255', 'С355'] },
  floorLoad: { label: 'Нагрузка на пол, т/м²', name: 'Нагрузка на пол', unit: 'т/м²', min: 0.1, max: 20 },
  soilData:  { label: 'Данные о грунте', name: 'Данные о грунте', list: ['нет геологии', 'основные данные', 'ИГИ'] },
  soilType:  { label: 'Тип грунта', name: 'Тип грунта', list: ['не знаю', 'скальный', 'крупнообломочный', 'песок крупный', 'песок средний', 'песок мелкий', 'песок пылеватый', 'супесь', 'суглинок', 'глина', 'насыпной', 'торф'] },
  soilState: { label: 'Состояние грунта', name: 'Состояние грунта', list: ['неизвестно', 'плотный', 'средней плотности', 'рыхлый'] },
  water:     { label: 'Уровень грунтовых вод', name: 'Грунтовые воды', list: ['неизвестно', 'ниже 5 м', '3–5 м', '1–3 м', 'менее 1 м'] },
  soilR:     { label: 'Расчётное сопротивление R по изысканиям, кПа (0 = по таблице)', name: 'R по изысканиям', unit: 'кПа', min: 0, max: 2000 },
  frost:     { label: 'Глубина промерзания, м (0 = 1,4 м)', name: 'Глубина промерзания', unit: 'м', min: 0, max: 4 },
  bearing:   { label: 'Глубина несущего слоя для свай, м (0 = сваи 6 м)', name: 'Несущий слой', unit: 'м', min: 0, max: 40 },
  scheme:    { label: 'Схема каркаса', name: 'Схема каркаса', list: ['КП (фермы)', 'П³ (балки)'], show: { 'КП (фермы)': 'рамы с фермами', 'П³ (балки)': 'рамы из балок' } },
  fachwerk:  { label: 'Фахверковые колонны на торцах', name: 'Фахверк на торцах', list: YN },
  layout:    { label: 'Раскладка стеновых панелей', name: 'Раскладка стеновых панелей', list: ['вертикальная', 'горизонтальная'] },
  base:      { label: 'Основание стен', name: 'Основание стен', list: ['швеллер'] },   // «цоколь» — нет цены в «Справочнике»
  wallCore:  { label: 'Утеплитель стеновых панелей', name: 'Утеплитель стен', list: ['минвата', 'пенопласт', 'КОМБИ'] },
  roofCore:  { label: 'Утеплитель кровельных панелей', name: 'Утеплитель кровли', list: ['минвата', 'пенопласт', 'КОМБИ'] },
  wallW:     { label: 'Ширина стеновой панели, мм', name: 'Ширина стеновой панели', unit: 'мм', list: [1000, 1190] },
  mTop:      { label: 'Металл панелей снаружи, мм', name: 'Металл снаружи', unit: 'мм', list: [0.4, 0.45, 0.5] },
  mBot:      { label: 'Металл панелей внутри, мм', name: 'Металл внутри', unit: 'мм', list: [0.4, 0.45, 0.5] },
  ral:       { label: 'Цвет панелей снаружи (RAL)', name: 'Цвет панелей (RAL)', list: [1014, 1015, 5005, 6005, 7004, 7024, 7035, 8017, 9002, 9003, 9006] },
  wallThk:   { label: 'Толщина стеновых панелей, мм', name: 'Стеновые панели', unit: 'мм', list: [50, 60, 80, 100, 120, 150, 180, 200, 220, 250, 300] },   // цена — с листа «Панели МП»
  roofThk:   { label: 'Толщина кровельных панелей, мм', name: 'Кровельные панели', unit: 'мм', list: [50, 60, 80, 100, 120, 150, 180, 200, 220, 250, 300] },
  ovhEnd:    { label: 'Свес кровли по торцам (с каждой стороны), м', name: 'Свес по торцам', unit: 'м', min: 0, max: 2 },
  ovhEave:   { label: 'Свес кровли по карнизу, м (по скату)', name: 'Свес по карнизу', unit: 'м', min: 0, max: 2 },
  fund:      { label: 'Фундамент', name: 'Фундамент', list: ['винтовые сваи', 'монолит'] },
  piles:     { label: 'Свай под одну колонну, шт', name: 'Свай под колонну', unit: 'шт', min: 1, max: 9, int: true },
  floor:     { label: 'Пол', name: 'Пол', list: ['монолитная плита', 'плиты ПАГ', 'нет'], show: { 'нет': 'не нужен' } },
  slabMode:  { label: 'Плита пола: подбор толщины', name: 'Подбор толщины плиты', list: ['по нагрузке', 'вручную'], hide: true },
  slabT:     { label: 'Толщина монолитной плиты, мм', name: 'Толщина бетонной плиты', unit: 'мм', list: [180, 200, 250, 300] },
  xps:       { label: 'Утепление под плитой ПЕНОПЛЭКС 50 мм', name: 'Утепление под плитой', list: YN, hide: true },   // сайт всегда шлёт «нет»
  gates:     { label: 'Ворота, шт', name: 'Ворота', unit: 'шт', min: 0, max: 30, int: true },
  windows:   { label: 'Окна, м²', name: 'Окна', unit: 'м²', min: 0, max: 2000 },
  doors:     { label: 'Двери, шт', name: 'Двери', unit: 'шт', min: 0, max: 30, int: true },
  flash:     { label: 'Фасонные элементы включить в смету', name: 'Фасонные элементы', list: YN, hide: true },   // сайт шлёт «нет»
  gutter:    { label: 'Водосток и снегозадержание', name: 'Водосток и снегозадержатели', list: YN, hide: true },   // сайт шлёт «нет»
  delivery:  { label: 'Доставка металла и панелей', name: 'Доставка', list: YN },
  vat:       { label: 'НДС для клиента (выберите «без НДС» или «22 %»)', name: 'НДС', list: ['без НДС', '22 %'] }
};
const IN = {};
Object.keys(FIELDS).forEach(k => IN[k] = FIELDS[k].label);
const IN_VAT_RATE = 'Ставка НДС (считается сама из выбора ниже)';
const IN_DAYS = 'Срок монтажных работ, дней';
const ALLOWED = { vat: FIELDS.vat.list, wallThk: FIELDS.wallThk.list, roofThk: FIELDS.roofThk.list };

// Строки листа «Расчёт» (столбец A → значение в B), которые идут в КП: чертежи, ведомость металла, объёмы.
const FACTS = {
  frames: 'Число рам', step: 'Фактический шаг рам, м', fachwerkCols: 'Колонн фахверка (оба торца)',
  slopeRad: 'Уклон, рад', slopeLen: 'Длина ската, м', purlinRows: 'Рядов прогонов', snow: 'Снеговая нагрузка, кПа',
  colsKg: 'Колонны рам, кг', raftersKg: 'Стропильные балки / фермы, кг', eaveKg: 'Карнизные балки, кг',
  purlinsKg: 'Прогоны, кг', wallBrKg: 'Связи по стенам, кг', roofBrKg: 'Связи по кровле, кг',
  kneeKg: 'Укосины торцевых стен, кг', fachwerkKg: 'Фахверк, кг', girtsKg: 'Ригели стен, кг',
  channelKg: 'Нижний прогон-швеллер, кг', nodesKg: 'Узлы, пластины, болты, кг',
  steelT: 'МЕТАЛЛОКОНСТРУКЦИИ ВСЕГО, т', steelKgM2: 'Металлоёмкость, кг/м²',
  wallM2: 'Стеновые панели, м²', roofM2: 'Кровельные панели, м²',
  colsAll: 'Колонн всего (с фахверком)', piles: 'Винтовых свай, шт', footings: 'Монолитных фундаментов (ростверков), шт',
  footV: 'Бетон фундаментов, м³', footRebar: 'Арматура фундаментов, кг', anchors: 'Анкерные болты, шт',
  bored: 'Буронабивных свай, шт', pileLen: 'Длина сваи, м',
  slabT: 'Толщина монолитной плиты, мм', slabV: 'Бетон плиты B25, м³', slabRebar: 'Арматура плиты, кг',
  sand: 'Песок на подушку, м³', gravel: 'Щебень на подушку, м³', pag: 'Плиты ПАГ 6 × 2 м, шт',
  tripsSteel: 'Рейсов доставки МК', tripsPanel: 'Рейсов доставки панелей', flashing: 'Итого фасонки, м.п. (ориентировочный расчёт)'
};
function facts_() {
  const sh = SpreadsheetApp.getActive().getSheetByName('Расчёт');
  if (!sh) return {};
  const v = sh.getRange(1, 1, sh.getLastRow(), 2).getValues();
  const byLabel = {};
  v.forEach(r => { const k = String(r[0]).trim(); if (k && !(k in byLabel)) byLabel[k] = r[1]; });
  const out = {};
  Object.keys(FACTS).forEach(k => { const x = byLabel[FACTS[k]]; if (x !== undefined && x !== '') out[k] = typeof x === 'number' ? x : String(x); });
  return out;
}

/** Проверить значение поля: вернуть годное значение или undefined (тогда поле не трогаем). */
function field_(k, raw) {
  const f = FIELDS[k];
  if (raw === undefined || raw === null || raw === '') return undefined;
  if (f.list) {
    const hit = f.list.find(x => String(x) === String(raw).trim());
    return hit === undefined ? undefined : hit;
  }
  const n = Number(String(raw).replace(',', '.').replace(/\s/g, ''));
  if (!isFinite(n)) return undefined;
  const v = clamp_(f.int ? Math.round(n) : n, f.min, f.max);
  return Math.round(v * 100) / 100;
}

/** Запустить один раз: создаёт лист «Заявки». */
function setup() {
  const ss = SpreadsheetApp.getActive();
  ['Ввод', 'Смета', 'График'].forEach(n => {
    if (!ss.getSheetByName(n)) throw new Error('Нет листа «' + n + '». Код нужно вставить в таблицу с калькулятором.');
  });
  let sh = ss.getSheetByName(LEADS);
  if (!sh) sh = ss.insertSheet(LEADS, 0);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#D9B05E');
    sh.setFrozenRows(1);
    sh.getRange('D:D').setNumberFormat('@');
    sh.getRange('I:J').setNumberFormat('#,##0');
    [140, 110, 130, 140, 140, 150, 220, 300, 110, 80, 380, 110, 110, 220]
      .forEach((w, i) => sh.setColumnWidth(i + 1, w));
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(['Новая', 'Дозвонился', 'Не берёт трубку', 'Думает', 'Выезд/встреча', 'Договор', 'Отказ'], true).build();
    sh.getRange('M2:M').setDataValidation(rule);
  }
  // Пробный расчёт — проверка, что всё на месте.
  const r = calcAngar_({ L: 30, W: 18, H: 6, vat: '5 %' });
  Logger.log('Пробный расчёт 30×18×6: ' + r.total + ' ₽, строк сметы: ' + r.items.length);
}

// ---------- помощники ----------
function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function num_(v) { const n = Number(String(v).replace(',', '.').replace(/\s/g, '')); return isFinite(n) ? n : 0; }
function clamp_(v, a, b) { return Math.min(b, Math.max(a, v)); }
function safe_(v, max) {
  let s = String(v == null ? '' : v).slice(0, max || 300);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}
function nextTo_(sheetName, label, def) {
  const f = SpreadsheetApp.getActive().getSheetByName(sheetName).createTextFinder(label).matchEntireCell(true).findNext();
  return f ? (num_(f.offset(0, 1).getValue()) || def) : def;
}
function plural_(n, a, b, c) { n = Math.abs(n) % 100; const m = n % 10; return n > 10 && n < 20 ? c : m === 1 ? a : m > 1 && m < 5 ? b : c; }
function rub_(v) { return Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'; }

/** Строки листа «Ввод»: подпись → номер строки. */
function inputRows_(sh) {
  const a = sh.getRange(1, 1, sh.getLastRow(), 1).getValues();
  const map = {};
  a.forEach((r, i) => { const k = String(r[0]).trim(); if (k && !(k in map)) map[k] = i + 1; });
  return map;
}
/** Лист «Смета»: строки с подписями и ценами. */
function smeta_() {
  const sh = SpreadsheetApp.getActive().getSheetByName('Смета');
  const v = sh.getRange(1, 1, sh.getLastRow(), 7).getValues();   // A..G
  return v.map(r => ({ name: String(r[1]).trim(), qty: r[2], unit: String(r[3]).trim(), price: r[4], sum: r[5] }));
}
function findRow_(rows, starts) {
  return rows.find(r => r.name.toLowerCase().indexOf(starts.toLowerCase()) === 0);
}
function smetaTotal_(rows, label) { const r = findRow_(rows, label); return r ? num_(r.sum) : 0; }

/**
 * Подставить значения во «Ввод», пересчитать, выполнить read(), вернуть «Ввод» как был.
 * Работает под блокировкой: два клиента одновременно не перепутают расчёты.
 */
function withInputs_(values, read) {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName('Ввод');
  const rows = inputRows_(sh);
  const backup = [];
  try {
    Object.keys(values).forEach(k => {
      const row = rows[IN[k]];
      if (!row) throw new Error('В листе «Ввод» не найдена строка «' + IN[k] + '»');
      const cell = sh.getRange(row, 2);
      backup.push([cell, cell.getValue()]);
      cell.setValue(values[k]);
    });
    SpreadsheetApp.flush();
    return read(sh, rows);
  } finally {
    backup.forEach(([cell, v]) => cell.setValue(v));
    SpreadsheetApp.flush();
  }
}

function vat_(p) { return ALLOWED.vat.indexOf(p.vat) >= 0 ? p.vat : 'без НДС'; }
/** «Цены с НДС 22 %, в т. ч. НДС 1 234 ₽.» — ставка из «Ввода», как её посчитала таблица. */
function vatInfo_(sh, rows, total) {
  const vat = String(sh.getRange(rows[IN.vat], 2).getValue() || '').trim();
  if (vat !== '22 %') return 'Цены без НДС.';
  const rate = num_(sh.getRange(rows[IN_VAT_RATE], 2).getValue());
  return 'Цены с НДС ' + vat + (rate ? ', в т. ч. НДС ' + rub_(total * rate / (1 + rate)) : '') + '.';
}
function markup_(rows) {
  const sub = smetaTotal_(rows, 'Сумма по разделам'), mk = smetaTotal_(rows, 'Наценка');
  return sub ? mk / sub : 0;
}

// ---------- Ангар: целиком по смете калькулятора ----------
function calcAngar_(p) {
  const v = {};
  Object.keys(FIELDS).forEach(k => { const x = field_(k, p[k]); if (x !== undefined) v[k] = x; });
  ['L', 'W', 'H'].forEach(k => { if (v[k] === undefined) throw new Error('не указан размер: ' + FIELDS[k].name); });
  if (v.vat === undefined) v.vat = 'без НДС';
  return withInputs_(v, (sh, rows) => {
    const sm = smeta_();
    const k = 1 + markup_(sm);
    const start = sm.findIndex(r => r.name === 'Раздел') + 1;
    const end = sm.findIndex(r => r.name === 'Сумма по разделам');
    const items = sm.slice(start, end).filter(r => num_(r.sum) > 0)
      .map(r => [r.name, num_(r.qty), r.unit, num_(r.price) * k, num_(r.sum) * k]);
    const total = smetaTotal_(sm, 'ИТОГО');
    const area = v.L * v.W;
    const days = num_(sh.getRange(rows[IN_DAYS], 2).getValue());
    const vatTotal = smetaTotal_(sm, 'в том числе НДС');
    const missing = sm.slice(start, end).filter(r => num_(r.qty) > 0 && r.price === '').map(r => r.name);
    const params = [['Размеры (Д × Ш × В)', v.L + ' × ' + v.W + ' × ' + v.H + ' м'], ['Площадь', area + ' м²']];
    Object.keys(v).forEach(key => {
      if (['L', 'W', 'H'].indexOf(key) >= 0) return;
      const f = FIELDS[key];
      if (f.hide) return;
      const val = f.show && f.show[v[key]] ? f.show[v[key]] : v[key];
      params.push([f.name, (typeof val === 'number' ? String(val).replace('.', ',') : String(val)) + (f.unit ? (f.unit === '°' ? '' : ' ') + f.unit : '')]);
    });
    if (p.use) params.push(['Назначение', String(p.use).slice(0, 40)]);
    const notes = [v.vat === '22 %' ? 'Цены с НДС 22 %, в т. ч. НДС ' + rub_(vatTotal) + '.' : 'Цены без НДС.'];
    if (days) notes.push('Срок монтажных работ — около ' + days + ' рабочих дней.');
    if (missing.length) notes.push('Стоимость позиций «' + missing.join('», «') + '» в расчёт не вошла — её уточнит инженер.');
    return {
      kind: 'Ангар под ключ', area: area, total: total, items: items, missing: missing,
      facts: facts_(), input: v, vatTotal: v.vat === '22 %' ? vatTotal : 0, days: days,
      title: v.L + ' × ' + v.W + ' м, высота ' + v.H + ' м', params: params, notes: notes,
      excluded: ['топпинг пола, огнезащита, перегородки — по запросу', 'инженерные системы: отопление, вентиляция, электрика, водопровод',
        'подключение к сетям, благоустройство']
    };
  });
}

// ---------- Сэндвич-панели: цена с листа «Панели <город завода>» (калькулятор поставщика) ----------
/** Заводы-поставщики: [город, широта, долгота]. Тот же список — в site/kp/panels.js (PANEL_FACTORIES).
 *  Прайс завода — лист «Панели <город>» (формат как у «Панели МП»). Пока листа нет — берётся «Панели МП». */
const FACTORIES = [
  ['Москва', 55.754, 37.620],               // лист «Панели Москва» — ждём прайс
  ['Санкт-Петербург', 59.939, 30.316, 'Панели МП'],   // «Металл Престиж», СПб
  ['Липецк', 52.603, 39.571],
  ['Новосибирск', 55.028, 82.921]
];
/** Дорожное расстояние ≈ по прямой × 1,25, округлено до 10 км. */
function km_(lat1, lon1, lat2, lon2) {
  const r = Math.PI / 180, dl = (lat2 - lat1) * r, dn = (lon2 - lon1) * r;
  const h = Math.pow(Math.sin(dl / 2), 2) + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.pow(Math.sin(dn / 2), 2);
  return Math.round(6371 * 2 * Math.asin(Math.sqrt(h)) * 1.25 / 10) * 10;
}
/** Ближайший к объекту завод и лист с его прайсом. */
function factory_(geo) {
  const lat = Number(geo && geo.lat), lon = Number(geo && geo.lon);
  if (!isFinite(lat) || !isFinite(lon) || !lat || !lon) return null;
  // Берём ближайший завод, у которого в таблице есть лист с прайсом
  const ss = SpreadsheetApp.getActive();
  const list = FACTORIES.map(x => ({ city: x[0], sheet: x[3] || 'Панели ' + x[0], km: km_(lat, lon, x[1], x[2]) }))
    .filter(x => ss.getSheetByName(x.sheet)).sort((a, b) => a.km - b.km);
  if (!list.length) return null;
  const f = list[0];
  f.to = String(geo.city || '').slice(0, 60);
  return f;
}
/** Таблица поставщика: ключ → [база ₽/м², название цвета], надбавка владельца и наценка за объём. */
function panelTable_(name) {
  const sh = SpreadsheetApp.getActive().getSheetByName(name || 'Панели МП');
  if (!sh) throw new Error('нет листа «' + (name || 'Панели МП') + '»');
  const ft = factoryTable_(sh);
  if (ft) return ft;
  const last = sh.getLastRow();
  const v = sh.getRange(5, 1, last - 4, 11).getValues();     // A..K
  const base = {};
  v.forEach(r => { if (r[0]) base[String(r[0]).trim()] = [num_(r[10]), String(r[8])]; });
  const side = sh.getRange(1, 14, Math.min(last, 40), 2).getValues();   // N..O
  let add = 0, tiers = [], inTiers = false;
  side.forEach(r => {
    const k = String(r[0]).trim();
    if (k.indexOf('Надбавка владельца') === 0) add = num_(r[1]);
    else if (k.indexOf('Объём от') === 0) inTiers = true;
    else if (inTiers && r[0] !== '' && isFinite(Number(r[0]))) tiers.push([num_(r[0]), num_(r[1])]);
    else if (inTiers && r[0] === '') inTiers = tiers.length === 0;
  });
  tiers.sort((x, y) => x[0] - y[0]);
  return { fmt: 'mp', base: base, add: add, tiers: tiers };
}
const RAL_NAMES = { 9003: 'Сигнальный белый', 9002: 'Серо-белый', 9006: 'Серебристый металлик', 1014: 'Слоновая кость',
  1015: 'Светло-слоновая кость', 5005: 'Сигнальный синий', 7004: 'Сигнальный серый', 7035: 'Туманно-серый',
  6005: 'Зелёный мох', 8017: 'Шоколадно-коричневый', 7024: 'Серый графит' };
/** Прайс завода в простом формате (лист «Панели <город>»):
 *  сверху настройки «подпись | значение», ниже шапка «Тип | Утеплитель | Толщина, мм | от 100 м² | от 200 м² | …» и строки цен ₽/м².
 *  Возвращает null, если лист в формате «Панели МП». */
function factoryTable_(sh) {
  const v = sh.getDataRange().getValues();
  const set = {}; let hdr = -1;
  v.forEach((r, i) => {
    const k = String(r[0]).trim();
    if (hdr >= 0 || !k) return;
    if (k === 'Тип') hdr = i; else set[k.toLowerCase()] = r[1];
  });
  if (hdr < 0) return null;
  const g = (s, d) => { const k = Object.keys(set).find(x => x.indexOf(s) === 0); return k === undefined || set[k] === '' ? d : set[k]; };
  // Необязательная колонка D «Ширина, мм»: тогда цены по объёму начинаются с колонки E
  const wCol = /^ширина/i.test(String(v[hdr][3]).trim()), c0 = wCol ? 4 : 3;
  const tiers = v[hdr].slice(c0).map(x => num_(String(x).replace(/[^\d]/g, ''))).filter(x => x > 0);
  const rows = {};
  v.slice(hdr + 1).forEach(r => {
    const t = String(r[0]).trim().toLowerCase(), c = String(r[1]).trim().toLowerCase();
    if (!t || !num_(r[2])) return;
    const core = c.indexOf('пено') === 0 ? 'пенопласт' : c.indexOf('мин') === 0 ? 'минвата' : c.indexOf('комб') === 0 ? 'КОМБИ' : c;
    const w = wCol && num_(r[3]) ? '|' + num_(r[3]) : '';
    rows[(t.indexOf('кров') === 0 ? 'кровля' : 'стена') + '|' + core + '|' + num_(r[2]) + w] = tiers.map((x, j) => num_(r[c0 + j]));
  });
  const metal = String(g('металл', '')).split('/').map(x => num_(String(x).replace(',', '.'))).filter(x => x > 0);
  return { fmt: 'factory', rows: rows, tiers: tiers, withVat: !/^нет/i.test(String(g('цены завода с ндс', 'да'))),
    add: num_(g('надбавка владельца', 0)), small: num_(g('заказ до', 0)), metal: metal.length === 2 ? metal : null,
    colors: String(g('цвета', '')).split(/[^\d]+/).filter(Boolean).map(Number) };
}
/** Цена ₽/м² панели. «Панели МП» — как в «Справочнике»: (база + наценка за объём + надбавка) × (без НДС → ÷ 1,22), до 50 м² — 60 000 ₽ на заказ.
 *  Прайс завода: цена по колонке объёма (по площади этого типа панелей) + надбавка владельца; меньше первой колонки — плюс «Заказ до …» ÷ площадь. */
function panelPrice_(t, x, area, vat) {
  const v22 = vat === '22 %';
  if (t.fmt === 'factory') {
    const k0 = (x.roof ? 'кровля' : 'стена') + '|' + x.core + '|' + x.thk;
    const row = t.rows[k0 + '|' + x.w] || t.rows[k0];
    if (!row || (t.colors.length && t.colors.indexOf(Number(x.ral)) < 0)) return null;
    let j = 0; t.tiers.forEach((m, i) => { if (area >= m) j = i; });
    if (!row[j]) return null;
    const small = t.small && area < t.tiers[0] ? t.small / Math.max(1, area) : 0;
    const f = t.withVat ? (v22 ? 1 : 1 / 1.22) : (v22 ? 1.22 : 1);
    return { price: Math.round((row[j] + small + t.add) * f * 100) / 100, color: RAL_NAMES[x.ral] || '' };
  }
  const b = t.base[[x.roof ? 'кровля' : 'стена', x.core, x.w, x.thk, x.mTop, x.mBot, x.ral].join('|')];
  if (!b) return null;
  let vol = 0;
  if (area <= 50) vol = 60000 / Math.max(1, area);
  else t.tiers.forEach(y => { if (area >= y[0]) vol = y[1]; });
  return { price: Math.round((b[0] + vol + t.add) * (v22 ? 1 : 1 / 1.22) * 100) / 100, color: b[1] };
}
function calcPanel_(p) {
  // Старый формат (один тип): {type, core, thk, width, area}. Новый: {wall:{...}, roof:{...}} — стеновые и кровельные в одном КП.
  if (!p.wall && !p.roof) {
    const one = { on: '1', core: p.core, thk: p.thk, width: p.width, area: p.area };
    if (p.type === 'roof') p.roof = one; else p.wall = one;
  }
  const pick = (k, x, d) => { const v = field_(k, x); return v === undefined ? d : v; };
  const mTop = pick('mTop', p.mTop, 0.45), mBot = pick('mBot', p.mBot, 0.45), ral = pick('ral', p.ral, 7024);
  const mont = p.mont === '1', deliv = p.deliv === '1', vat = vat_(p);
  const fac = factory_(p.geo);
  const t = panelTable_(fac ? fac.sheet : 'Панели МП');
  const panels = [];
  [['wall', 'Стеновые'], ['roof', 'Кровельные']].forEach(([k, name]) => {
    const q = p[k];
    if (!q || q.on === '0' || q.on === false) return;
    const roof = k === 'roof';
    const A = clamp_(num_(q.area), 0, 100000);
    if (A < 10) return;
    const core = pick(roof ? 'roofCore' : 'wallCore', q.core, 'минвата');
    const w = roof ? 1000 : pick('wallW', q.width, 1000);
    const thk = pick(roof ? 'roofThk' : 'wallThk', q.thk, roof ? 150 : 100);
    const pp = panelPrice_(t, { roof: roof, core: core, w: w, thk: thk, mTop: mTop, mBot: mBot, ral: ral }, A, vat);
    if (!pp) throw new Error('нет такой панели: ' + [name, core, w, thk, mTop, mBot, 'RAL ' + ral].join(' | '));
    const mt = t.fmt === 'factory' ? (t.metal || [0, 0]) : [mTop, mBot];
    panels.push({ kind: name, core: core, thk: thk, width: w, mTop: mt[0], mBot: mt[1], ral: ral, color: pp.color, area: A, price: pp.price });
  });
  if (!panels.length) throw new Error('не указана площадь панелей (от 10 м²)');
  const total = panels.reduce((s, x) => s + x.area, 0);
  return withInputs_({ vat: vat }, (sh, rows) => {
    const sm = smeta_(); const k = 1 + markup_(sm);
    const perTruck = nextTo_('График', 'Помещается в одну фуру, м²', 250);
    const pr = n => num_((findRow_(sm, n) || {}).price) * k;
    const items = panels.map(x => [x.kind + ' сэндвич-панели, ' + x.core + ' ' + x.thk + ' мм, RAL ' + x.ral, x.area, 'м²', x.price * k]);
    panels.forEach(x => x.price = Math.round(x.price * k * 100) / 100);
    if (mont) {
      items.push(['Монтаж сэндвич-панелей', total, 'м²', pr('Монтаж сэндвич-панелей')]);
      items.push(['Расходники для монтажа (герметик, саморезы, лента)', total, 'м²', pr('Расходники')]);
    }
    const trips = deliv ? Math.ceil(total / perTruck) : 0;
    const excluded = ['фасонные элементы — по спецификации', 'разгрузка на объекте'];
    // Доставка считается только в черте города завода. Объект в другом городе — доставку считает менеджер.
    let tripPrice = pr('Доставка сэндвич-панелей'), delivNote = '';
    if (deliv && fac && fac.to !== fac.city) {
      tripPrice = 0;
      delivNote = 'доставка до г. ' + fac.to + ' (' + trips + ' ' + plural_(trips, 'рейс', 'рейса', 'рейсов') + ') — рассчитаем отдельно';
    }
    // Фасонные элементы: метры считает сайт по формулам листа «Расчёт», цены — строки «Сметы»
    const flashM = p.flash === '1' ? Math.ceil(clamp_(num_(p.flashM), 0, 50000)) : 0;
    if (flashM) {
      items.push(['Фасонные элементы: отливы, углы, конёк, карнизные и торцевые планки, обрамления (ориентировочно)', flashM, 'м.п.', pr('Фасонные элементы, изготовление')]);
      if (mont) items.push(['Монтаж фасонных элементов', flashM, 'м.п.', pr('Монтаж фасонных элементов')]);
      excluded.splice(excluded.indexOf('фасонные элементы — по спецификации'), 1, 'точный состав фасонных элементов — по спецификации');
    }
    if (deliv && tripPrice) items.push(['Доставка сэндвич-панелей' + (fac && fac.to ? ' по г. ' + fac.to : ''), trips, 'рейс', tripPrice]);
    if (delivNote) excluded.unshift(delivNote);
    const mm = x => String(x).replace('.', ',') + ' мм';
    const params = [];
    panels.forEach(x => params.push([x.kind + ' панели', x.core + ', ' + x.thk + ' мм, ' + x.area + ' м²']));
    const dm = p.dims;
    if (dm && num_(dm.L) && num_(dm.B) && num_(dm.H))
      params.push(['Размеры здания (Д × Ш × В)', [dm.L, dm.B, dm.H].map(x => String(num_(x)).replace('.', ',')).join(' × ') + ' м']);
    params.push(['Металл снаружи / внутри', panels[0].mTop ? mm(panels[0].mTop) + ' / ' + mm(panels[0].mBot) : 'уточним при заказе'], ['Цвет снаружи', 'RAL ' + ral + (panels[0].color ? ' (' + panels[0].color + ')' : '')],
      ['Площадь всего', total + ' м²'], ['Монтаж', mont ? 'нужен' : 'только поставка'], ['Доставка', deliv ? 'нужна' : 'самовывоз'], ['НДС', vat]);
    return finish_({
      kind: 'Сэндвич-панели', area: 0, items: items, panels: panels, mont: mont, trips: trips, panelArea: total, flashM: flashM,
      title: panels.map(x => x.kind.toLowerCase() + ' ' + x.thk + ' мм — ' + x.area + ' м²').join(', ').replace(/^./, c => c.toUpperCase()),
      params: params,
      supplier: fac ? fac.city + ' (' + fac.sheet + '), ~' + fac.km + ' км до объекта' : '',   // только для владельца: в ответ сайту не уходит
      notes: ['Цена панелей — на дату расчёта, с учётом объёма заказа. Цвет изнутри — RAL 9003.'], vatOf: [sh, rows],
      excluded: excluded
    });
  });
}

// ---------- Металлоконструкции: цены из «Сметы» ----------
function calcMk_(p) {
  const T = clamp_(num_(p.t), 0.1, 5000), kmd = p.kmd === '0', paint = p.paint === '1',
        mont = p.mont === '1', deliv = p.deliv === '1';
  const kinds = { karkas: 'Каркас здания', fermy: 'Фермы и балки', kolonny: 'Колонны',
    lestnicy: 'Лестницы, площадки, ограждения', navesy: 'Навесы, козырьки', nestandart: 'Нестандартные конструкции' };
  const kindName = kinds[p.kind] || 'Металлоконструкции';
  return withInputs_({ vat: vat_(p) }, (sh, rows) => {
    const sm = smeta_(); const k = 1 + markup_(sm);
    const perTruck = nextTo_('График', 'Помещается в одну фуру, т', 8.5);
    const pr = n => num_((findRow_(sm, n) || {}).price) * k;
    const items = [[kindName + ': изготовление', T, 'т', pr('Изготовление металлоконструкций')]];
    if (kmd) items.push(['Разработка чертежей КМД', 1, 'компл.', pr('Разработка КМД')]);
    if (paint) items.push(['Окраска металлоконструкций', T, 'т', pr('Окраска металлоконструкций')]);
    if (deliv) items.push(['Доставка металлоконструкций', Math.ceil(T / perTruck), 'рейс', pr('Доставка металлоконструкций')]);
    if (mont) items.push(['Монтаж металлоконструкций', T, 'т', pr('Монтаж металлоконструкций')]);
    return finish_({
      kind: 'Металлоконструкции', area: 0, items: items, title: kindName + ' — ' + T + ' т',
      params: [['Изделие', kindName], ['Масса', T + ' т'], ['Чертежи КМД', kmd ? 'разрабатываем мы' : 'есть'],
        ['Окраска', paint ? 'нужна' : 'не нужна'], ['Доставка', deliv ? 'нужна' : 'самовывоз'], ['Монтаж', mont ? 'нужен' : 'не нужен'], ['НДС', vat_(p)]],
      notes: ['Итоговая масса уточняется по чертежам КМД.'], vatOf: [sh, rows],
      excluded: ['разгрузка на объекте', 'автокран и подъёмник на монтаже — по проекту']
    });
  });
}

function finish_(r) {
  r.items = r.items.map(i => [i[0], i[1], i[2], i[3], Math.round(i[1] * i[3])]);
  r.missing = r.items.filter(i => !i[3]).map(i => i[0]);
  r.items = r.items.filter(i => i[3]);
  r.total = r.items.reduce((s, i) => s + i[4], 0);
  r.notes.unshift(vatInfo_(r.vatOf[0], r.vatOf[1], r.total));
  const vat = String(r.vatOf[0].getRange(r.vatOf[1][IN.vat], 2).getValue() || '').trim();
  const rate = vat === '22 %' ? num_(r.vatOf[0].getRange(r.vatOf[1][IN_VAT_RATE], 2).getValue()) : 0;
  r.vatTotal = rate ? Math.round(r.total * rate / (1 + rate)) : 0;
  delete r.vatOf;
  return r;
}

function kpText_(r) {
  return r.kind + ': ' + r.title + '\n' + r.params.map(p => p[0] + ': ' + p[1]).join('; ') + '\n' +
    r.items.map((i, n) => (n + 1) + '. ' + i[0] + ' — ' + i[1] + ' ' + i[2] + ' × ' + rub_(i[3]) + ' = ' + rub_(i[4])).join('\n') +
    (r.supplier ? '\nЗавод (видно только вам): ' + r.supplier : '') + '\nИТОГО: ' + rub_(r.total) + (r.area ? ' (~' + rub_(r.total / r.area) + '/м²)' : '') + '. ' + r.notes.join(' ');
}
function kpNumber_() {
  return Utilities.formatDate(new Date(), 'Europe/Moscow', 'yyMMdd-HHmm') + '-' + Math.floor(10 + Math.random() * 90);
}

/** Проверка, что скрипт опубликован (откройте ссылку …/exec в браузере). */
function doGet() { return json_({ ok: true, service: 'kp' }); }

/** Приём заявки с сайта: расчёт по калькулятору + запись в «Заявки». */
function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'bad json' }); }
  if (d.hp) return json_({ ok: false, error: 'bad data' });                       // бот
  const phone = String(d.phone || '').replace(/[^\d+]/g, '');
  const name = String(d.name || '').trim();
  if (!/^\+7\d{10}$/.test(phone) || name.length < 2) return json_({ ok: false, error: 'bad data' });

  const lock = LockService.getScriptLock();
  if (!lock.tryLock(45000)) return json_({ ok: false, error: 'busy' });
  let r, no;
  try {
    const p = d.params || {};
    r = d.kind === 'panel' ? calcPanel_(p) : d.kind === 'mk' ? calcMk_(p) : calcAngar_(p);
    no = kpNumber_();
    SpreadsheetApp.getActive().getSheetByName(LEADS).appendRow([
      new Date(), no, safe_(name, 60), "'" + phone, safe_(d.city, 80), r.kind, safe_(r.title, 120),
      safe_(r.params.map(x => x[0] + ': ' + x[1]).join('; '), 500), Math.round(r.total),
      r.area ? Math.round(r.total / r.area) : '', safe_(kpText_(r), 4000) + (r.missing.length ? '\n⚠ Нет цены в «Справочнике»: ' + r.missing.join(', ') : ''),
      safe_(d.src, 40), 'Новая', ''
    ]);
  } catch (err) {
    return json_({ ok: false, error: 'calc', message: String(err && err.message || err).slice(0, 200) });
  } finally { lock.releaseLock(); }

  if (NOTIFY_EMAIL) {
    try {
      MailApp.sendEmail(NOTIFY_EMAIL, 'Заявка с сайта: ' + name + ', ' + phone + ' — ' + rub_(r.total),
        'Имя: ' + name + '\nТелефон: ' + phone + '\nГород: ' + (d.city || '—') + '\nИсточник: ' + (d.src || '—') +
        '\nКП № ' + no + '\n\n' + kpText_(r) + '\n\nТаблица: ' + SpreadsheetApp.getActive().getUrl());
    } catch (err) { /* лимит писем — заявка всё равно в таблице */ }
  }
  r.notes = r.notes.filter(String);
  delete r.missing; delete r.supplier;   // завод-изготовитель клиенту не показываем
  return json_({ ok: true, kp: no, days: KP_DAYS, result: r });
}
