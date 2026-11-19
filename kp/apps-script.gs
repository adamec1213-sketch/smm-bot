/**
 * РСК «Поколения» — КП с сайта по калькулятору владельца.
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

// Подписи строк листа «Ввод» (столбец A), в которые сайт пишет значения (столбец B).
const IN = {
  L: 'Длина здания, м', W: 'Ширина (пролёт), м', H: 'Высота до карниза, м',
  wallThk: 'Толщина стеновых панелей, мм', roofThk: 'Толщина кровельных панелей, мм',
  fund: 'Фундамент', floor: 'Пол', gates: 'Ворота, шт', windows: 'Окна, м²', doors: 'Двери, шт',
  flash: 'Фасонные элементы включить в смету', gutter: 'Водосток и снегозадержание',
  delivery: 'Доставка металла и панелей'
};
const IN_VAT = 'НДС для клиента (выберите 5 % или 22 %)';
const IN_DAYS = 'Срок монтажных работ, дней';

// Допустимые значения (как в выпадающих списках файла).
const ALLOWED = {
  wallThk: [100, 120], roofThk: [120, 150],
  fund: ['монолит', 'винтовые сваи'], floor: ['монолитная плита', 'плиты ПАГ', 'нет'],
  flash: ['да', 'нет'], gutter: ['да', 'нет'], delivery: ['да', 'нет']
};

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
  const r = calcAngar_({ L: 30, W: 18, H: 6 });
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

function vatInfo_(sh, rows) {
  const vat = String(sh.getRange(rows[IN_VAT], 2).getValue() || '').trim();
  return vat ? 'Цены с НДС ' + vat : 'Цены с НДС';
}
function markup_(rows) {
  const sub = smetaTotal_(rows, 'Сумма по разделам'), mk = smetaTotal_(rows, 'Наценка');
  return sub ? mk / sub : 0;
}

// ---------- Ангар: целиком по смете калькулятора ----------
function calcAngar_(p) {
  const v = {
    L: clamp_(num_(p.L), 6, 300), W: clamp_(num_(p.W), 12, 36), H: clamp_(num_(p.H), 4, 14),
    wallThk: ALLOWED.wallThk.indexOf(num_(p.wallThk)) >= 0 ? num_(p.wallThk) : 100,
    roofThk: ALLOWED.roofThk.indexOf(num_(p.roofThk)) >= 0 ? num_(p.roofThk) : 120,
    fund: ALLOWED.fund.indexOf(p.fund) >= 0 ? p.fund : 'винтовые сваи',
    floor: ALLOWED.floor.indexOf(p.floor) >= 0 ? p.floor : 'монолитная плита',
    gates: clamp_(Math.round(num_(p.gates)), 0, 30), windows: clamp_(num_(p.windows), 0, 2000),
    doors: clamp_(Math.round(num_(p.doors)), 0, 30),
    flash: 'да', gutter: p.gutter === 'нет' ? 'нет' : 'да', delivery: p.delivery === 'нет' ? 'нет' : 'да'
  };
  return withInputs_(v, (sh, rows) => {
    const sm = smeta_();
    const k = 1 + markup_(sm);
    const start = sm.findIndex(r => r.name === 'Раздел') + 1;
    const end = sm.findIndex(r => r.name === 'Сумма по разделам');
    const items = sm.slice(start, end).filter(r => num_(r.sum) > 0)
      .map(r => [r.name, num_(r.qty), r.unit, num_(r.price) * k, num_(r.sum) * k]);
    const total = smetaTotal_(sm, 'ИТОГО С НДС');
    const area = v.L * v.W;
    const days = num_(sh.getRange(rows[IN_DAYS], 2).getValue());
    const missing = sm.slice(start, end).filter(r => num_(r.qty) > 0 && r.price === '').map(r => r.name);
    return {
      kind: 'Ангар под ключ', area: area, total: total, items: items, missing: missing,
      title: v.L + ' × ' + v.W + ' м, высота ' + v.H + ' м',
      params: [['Размеры (Д × Ш × В)', v.L + ' × ' + v.W + ' × ' + v.H + ' м'], ['Площадь', area + ' м²'],
        ['Стены / кровля', 'сэндвич-панели ' + v.wallThk + ' / ' + v.roofThk + ' мм'],
        ['Фундамент', v.fund], ['Пол', v.floor === 'нет' ? 'не нужен' : v.floor],
        ['Назначение', String(p.use || '—').slice(0, 40)]],
      notes: [vatInfo_(sh, rows) + '.', days ? 'Срок монтажных работ — около ' + days + ' рабочих дней.' : ''],
      excluded: ['топпинг пола, огнезащита, перегородки — по запросу', 'инженерные системы: отопление, вентиляция, электрика, водопровод',
        'подключение к сетям, благоустройство']
    };
  });
}

// ---------- Сэндвич-панели: цены из «Сметы» ----------
function calcPanel_(p) {
  const roof = p.type === 'roof';
  const thk = roof ? (ALLOWED.roofThk.indexOf(num_(p.thk)) >= 0 ? num_(p.thk) : 120)
                   : (ALLOWED.wallThk.indexOf(num_(p.thk)) >= 0 ? num_(p.thk) : 100);
  const A = clamp_(num_(p.area), 10, 100000), mont = p.mont === '1', deliv = p.deliv === '1';
  const set = roof ? { roofThk: thk } : { wallThk: thk };
  return withInputs_(set, (sh, rows) => {
    const sm = smeta_(); const k = 1 + markup_(sm);
    const perTruck = nextTo_('График', 'Помещается в одну фуру, м²', 250);
    const pr = n => num_((findRow_(sm, n) || {}).price) * k;
    const items = [[(roof ? 'Кровельные' : 'Стеновые') + ' сэндвич-панели, минвата ' + thk + ' мм', A, 'м²', pr(roof ? 'Кровельные сэндвич-панели' : 'Стеновые сэндвич-панели')]];
    if (mont) {
      items.push(['Монтаж сэндвич-панелей', A, 'м²', pr('Монтаж сэндвич-панелей')]);
      items.push(['Расходники для монтажа (герметик, саморезы, лента)', A, 'м²', pr('Расходники')]);
    }
    if (deliv) items.push(['Доставка сэндвич-панелей', Math.ceil(A / perTruck), 'рейс', pr('Доставка сэндвич-панелей')]);
    return finish_({
      kind: 'Сэндвич-панели', area: 0, items: items,
      title: (roof ? 'Кровельные' : 'Стеновые') + ' сэндвич-панели ' + thk + ' мм — ' + A + ' м²',
      params: [['Тип', (roof ? 'кровельные' : 'стеновые') + ', минеральная вата'], ['Толщина', thk + ' мм'], ['Площадь', A + ' м²'],
        ['Монтаж', mont ? 'нужен' : 'только поставка'], ['Доставка', deliv ? 'нужна' : 'самовывоз']],
      notes: [vatInfo_(sh, rows) + '.', 'Другие толщины, PIR и цвет по RAL — по запросу.'],
      excluded: ['фасонные элементы — по спецификации', 'разгрузка на объекте']
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
  return withInputs_({}, (sh, rows) => {
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
        ['Окраска', paint ? 'нужна' : 'не нужна'], ['Доставка', deliv ? 'нужна' : 'самовывоз'], ['Монтаж', mont ? 'нужен' : 'не нужен']],
      notes: [vatInfo_(sh, rows) + '.', 'Итоговая масса уточняется по чертежам КМД.'],
      excluded: ['разгрузка на объекте', 'автокран и подъёмник на монтаже — по проекту']
    });
  });
}

function finish_(r) {
  r.items = r.items.map(i => [i[0], i[1], i[2], i[3], Math.round(i[1] * i[3])]);
  r.missing = r.items.filter(i => !i[3]).map(i => i[0]);
  r.items = r.items.filter(i => i[3]);
  r.total = r.items.reduce((s, i) => s + i[4], 0);
  return r;
}

function kpText_(r) {
  return r.kind + ': ' + r.title + '\n' + r.params.map(p => p[0] + ': ' + p[1]).join('; ') + '\n' +
    r.items.map((i, n) => (n + 1) + '. ' + i[0] + ' — ' + i[1] + ' ' + i[2] + ' × ' + rub_(i[3]) + ' = ' + rub_(i[4])).join('\n') +
    '\nИТОГО: ' + rub_(r.total) + (r.area ? ' (~' + rub_(r.total / r.area) + '/м²)' : '') + '. ' + r.notes.join(' ');
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
  delete r.missing;
  return json_({ ok: true, kp: no, days: KP_DAYS, result: r });
}
