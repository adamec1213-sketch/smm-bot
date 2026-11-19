/**
 * РСК «Поколения» — приём заявок с калькулятора КП в Google Таблицу.
 *
 * Как подключить — см. kp/ИНСТРУКЦИЯ.md. Коротко:
 * 1) Таблица → Расширения → Apps Script → вставить этот код → Сохранить.
 * 2) Выбрать функцию setup → Выполнить → разрешить доступ.
 * 3) Начать развертывание → Новое развертывание → Веб-приложение,
 *    «Запуск от имени: Я», «Доступ: Все» → скопировать ссылку …/exec.
 */

const LEADS = 'Заявки';
const PRICES = 'Цены';
const HEADERS = ['Дата', '№ КП', 'Имя', 'Телефон', 'Город', 'Направление', 'Объект',
  'Параметры', 'Сумма, ₽', '₽/м²', 'Состав КП', 'Источник', 'Статус', 'Комментарий'];

// Стартовые цены. После setup() меняйте их прямо в листе «Цены».
const DEFAULT_PRICES = [
  ['email_uvedomleniy', 'rsk-47@bk.ru', 'Куда присылать письмо о новой заявке (пусто — не присылать)'],
  ['kp_srok_dney', 10, 'Сколько дней действует КП'],
  ['nds_tekst', 'Цены указаны без НДС', 'Строка про НДС в КП'],
  ['angar_proekt_fix', 250000, 'Ангар: проект, фиксированная часть, ₽'],
  ['angar_proekt_m2', 450, 'Ангар: проект, за м², ₽'],
  ['angar_fund_pol_m2', 11600, 'Ангар: фундамент + плита пола 200 мм, ₽/м²'],
  ['angar_metall_t', 175000, 'Ангар: металлокаркас (металл, изготовление, доставка), ₽/т'],
  ['angar_metall_kg_baza', 30, 'Ангар: расход металла, база, кг/м²'],
  ['angar_metall_kg_prolet', 0.8, 'Ангар: + кг/м² за каждый метр ширины'],
  ['angar_metall_kg_vysota', 1.5, 'Ангар: + кг/м² за каждый метр высоты выше 6 м'],
  ['angar_panel_stena_m2', 4100, 'Ангар: стеновые панели 120 мм с фасонкой, ₽/м²'],
  ['angar_panel_krovlya_m2', 4500, 'Ангар: кровельные панели 150 мм, водосток, снегозадержание, ₽/м²'],
  ['angar_proflist_m2', 1600, 'Холодный ангар: профлист с фасонкой, ₽/м²'],
  ['angar_montazh_t', 70000, 'Ангар: монтаж каркаса с техникой, ₽/т'],
  ['angar_montazh_panel_m2', 1700, 'Монтаж сэндвич-панелей, ₽/м²'],
  ['angar_montazh_proflist_m2', 900, 'Монтаж профлиста, ₽/м²'],
  ['angar_vorota_sht', 350000, 'Секционные ворота 3×3,5 м с автоматикой, ₽/шт'],
  ['angar_okna_m2', 18000, 'Окна ПВХ, ₽/м²'],
  ['panel_50', 2700, 'Сэндвич-панель стеновая 50 мм, минвата, ₽/м²'],
  ['panel_80', 2950, 'Сэндвич-панель стеновая 80 мм, ₽/м²'],
  ['panel_100', 3150, 'Сэндвич-панель стеновая 100 мм, ₽/м²'],
  ['panel_120', 3350, 'Сэндвич-панель стеновая 120 мм, ₽/м²'],
  ['panel_150', 3700, 'Сэндвич-панель стеновая 150 мм, ₽/м²'],
  ['panel_200', 4300, 'Сэндвич-панель стеновая 200 мм, ₽/м²'],
  ['panel_250', 4900, 'Сэндвич-панель стеновая 250 мм, ₽/м²'],
  ['panel_krovlya_dop', 350, 'Надбавка за кровельную панель, ₽/м²'],
  ['panel_fason_proc', 12, 'Фасонные элементы, % от стоимости панелей'],
  ['mk_karkas', 165000, 'МК: каркас здания, ₽/т (металл, изготовление, грунт)'],
  ['mk_fermy', 175000, 'МК: фермы и балки, ₽/т'],
  ['mk_kolonny', 160000, 'МК: колонны, ₽/т'],
  ['mk_lestnicy', 230000, 'МК: лестницы, площадки, ограждения, ₽/т'],
  ['mk_navesy', 185000, 'МК: навесы, козырьки, ₽/т'],
  ['mk_nestandart', 200000, 'МК: нестандартные конструкции, ₽/т'],
  ['mk_kmd_t', 9000, 'МК: разработка КМД, ₽/т'],
  ['mk_emal_t', 15000, 'МК: грунт + эмаль, ₽/т'],
  ['mk_cink_t', 45000, 'МК: горячее цинкование, ₽/т'],
  ['mk_montazh_t', 70000, 'МК: монтаж, ₽/т'],
];

/** Запустить один раз: создаёт листы «Заявки» и «Цены». */
function setup() {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(LEADS) || ss.insertSheet(LEADS, 0);
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
  let pr = ss.getSheetByName(PRICES);
  if (!pr) {
    pr = ss.insertSheet(PRICES);
    pr.getRange(1, 1, 1, 3).setValues([['Ключ (не менять)', 'Значение', 'Что это']]).setFontWeight('bold').setBackground('#D9B05E');
    pr.getRange(2, 1, DEFAULT_PRICES.length, 3).setValues(DEFAULT_PRICES);
    pr.setFrozenRows(1); pr.setColumnWidth(1, 210); pr.setColumnWidth(2, 160); pr.setColumnWidth(3, 470);
  }
}

function readPrices_() {
  const pr = SpreadsheetApp.getActive().getSheetByName(PRICES);
  const out = {};
  if (!pr || pr.getLastRow() < 2) return out;
  pr.getRange(2, 1, pr.getLastRow() - 1, 2).getValues().forEach(([k, v]) => { if (k) out[String(k).trim()] = v; });
  return out;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Страница забирает отсюда актуальные цены. */
function doGet() {
  const p = readPrices_();
  delete p.email_uvedomleniy;
  return json_({ ok: true, prices: p });
}

// Защита от «формул» в ячейках: текст, начинающийся с = + - @, делаем обычным текстом.
function safe_(v, max) {
  let s = String(v == null ? '' : v).slice(0, max || 300);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

/** Приём заявки с калькулятора. */
function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'bad json' }); }
  const phone = String(d.phone || '').replace(/[^\d+]/g, '');
  if (!/^\+7\d{10}$/.test(phone) || !d.name) return json_({ ok: false, error: 'bad data' });

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = SpreadsheetApp.getActive().getSheetByName(LEADS);
    sh.appendRow([
      new Date(), safe_(d.kp, 30), safe_(d.name, 60), "'" + phone, safe_(d.city, 80), safe_(d.kind, 40),
      safe_(d.title, 120), safe_(d.params, 500), Number(d.total) || '', Number(d.perM2) || '',
      safe_(d.text, 3000), safe_(d.src, 40), 'Новая', ''
    ]);
  } finally { lock.releaseLock(); }

  const to = readPrices_().email_uvedomleniy;
  if (to) {
    try {
      MailApp.sendEmail(String(to), 'Новая заявка: ' + d.name + ', ' + phone + ' — ' + (d.title || ''),
        'Имя: ' + d.name + '\nТелефон: ' + phone + '\nГород: ' + (d.city || '—') + '\nИсточник: ' + (d.src || '—') +
        '\n\n' + (d.text || '') + '\n\nТаблица: ' + SpreadsheetApp.getActive().getUrl());
    } catch (err) { /* лимит писем исчерпан — заявка всё равно в таблице */ }
  }
  return json_({ ok: true });
}
