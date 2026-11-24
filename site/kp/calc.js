(function(){
const $ = id => document.getElementById(id);
const radio = n => (document.querySelector('input[name="'+n+'"]:checked')||{}).value;
const num = id => { const v = parseFloat(String($(id).value).replace(',', '.')); return isFinite(v) ? v : 0; };
const rub = v => Math.round(v).toLocaleString('ru-RU').replace(/[  ,]/g,' ') + ' ₽';
const fmt = (v,d) => Number(Number(v).toFixed(d||0)).toLocaleString('ru-RU');
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const src = (new URLSearchParams(location.search).get('src') || (document.referrer ? 'сайт' : 'прямой заход')).slice(0,40);

document.querySelectorAll('.em').forEach(e => e.textContent = COMPANY.email);
$('tg').href = COMPANY.telegram; $('call').href = COMPANY.phoneHref;
$('call').textContent = 'Позвонить ' + COMPANY.phone;

// ---------- Панели: списки из PANEL_OPTS (без цен) ----------
const opts = (sel, list, def, label) => { const cur = sel.value;
  sel.innerHTML = list.map(v => '<option value="'+v+'">'+(label ? label(v) : String(v).replace('.', ','))+'</option>').join('');
  sel.value = list.map(String).includes(cur) ? cur : String(def); };
const ralName = c => (PANEL_OPTS.colors.find(x => x[0] == c) || [c, ''])[1];
function panelOpts(){
  const type = radio('p_type') || 'wall', box = $('p_core_box');
  const core = radio('p_core') || 'минвата';
  box.innerHTML = PANEL_OPTS.cores[type].map(c => '<label><input type="radio" name="p_core" value="'+c+'"'+(c===core?' checked':'')+'><span>'+c+'</span></label>').join('');
  box.querySelectorAll('input').forEach(e => e.addEventListener('change', hints));
  $('p_core_hint').textContent = PANEL_OPTS.coreNote[core] || '';
  opts($('p_th'), PANEL_OPTS.thk[type+'|'+core], type === 'roof' ? 150 : 100);
  opts($('p_w'), PANEL_OPTS.widths[type], 1000); $('p_w_box').classList.toggle('hidden', type === 'roof');
  opts($('p_mt'), PANEL_OPTS.metals, 0.45); opts($('p_mb'), PANEL_OPTS.metals, 0.45);
  const rb = $('p_ral_box');
  if (!rb.children.length) {
    rb.innerHTML = PANEL_OPTS.colors.map((c,k) => '<label title="RAL '+c[0]+' — '+c[1]+'"><input type="radio" name="p_ral" value="'+c[0]+'"'+(k===0?' checked':'')+'><i style="background:'+c[2]+'"></i></label>').join('');
    rb.querySelectorAll('input').forEach(e => e.addEventListener('change', () => $('p_ral_hint').textContent = 'RAL ' + e.value + ' — ' + ralName(e.value)));
  }
  $('p_ral_hint').textContent = 'RAL ' + radio('p_ral') + ' — ' + ralName(radio('p_ral'));
  // ангар
  const ac = $('a_core').value || 'минвата';
  opts($('a_wallThk'), PANEL_OPTS.thk['wall|'+ac].filter(t => t >= 80), 100);
  opts($('a_roofThk'), PANEL_OPTS.thk['roof|'+ac].filter(t => t >= 80), 150);
  if (!$('a_ral').children.length) opts($('a_ral'), PANEL_OPTS.colors.map(c => c[0]), 7024, v => 'RAL ' + v + ' — ' + ralName(v));
}

// ---------- Вкладки и подсказки ----------
let tab = 'angar';
document.querySelectorAll('.tab').forEach(b => b.addEventListener('click', () => {
  tab = b.dataset.t;
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('[data-pane]').forEach(x => x.classList.toggle('hidden', x.dataset.pane !== tab));
}));
function hints(){
  const L = num('a_len'), W = num('a_wid');
  $('a_area_hint').textContent = (L && W ? 'Площадь: ' + fmt(L*W) + ' м² · ' : '') + 'ширина (пролёт) 12–36 м, высота до карниза 4–14 м';
  panelOpts();
  $('a_load_box').classList.toggle('hidden', radio('a_floor') !== 'монолитная плита');
  $('a_piles_box').classList.toggle('hidden', radio('a_fund') !== 'винтовые сваи');
}
document.querySelectorAll('#form input, #form select').forEach(e => e.addEventListener('change', hints));
document.querySelectorAll('input[name=vat]').forEach(e => e.addEventListener('change', () => $('vat_box').classList.remove('bad')));
['a_len','a_wid'].forEach(id => $(id).addEventListener('input', hints));
$('pol_link').addEventListener('click', e => { e.preventDefault(); $('policy').classList.toggle('hidden'); });

function params(){
  if (tab === 'angar') {
    const p = { L: num('a_len'), W: num('a_wid'), H: num('a_h'), use: $('a_use').value, snowReg: $('a_snowReg').value,
      wallThk: $('a_wallThk').value, roofThk: $('a_roofThk').value, wallCore: $('a_core').value, roofCore: $('a_core').value, ral: $('a_ral').value,
      fund: radio('a_fund'), floor: radio('a_floor'),
      gates: num('a_gates'), windows: num('a_win'), doors: num('a_doors'),
      flash: radio('a_flash'), gutter: radio('a_gutter'), delivery: radio('a_delivery'), vat: radio('vat') };
    if (p.fund === 'винтовые сваи' && $('a_piles').value) p.piles = num('a_piles');
    if (p.floor === 'монолитная плита' && $('a_floorLoad').value) p.floorLoad = num('a_floorLoad');
    // «Для инженеров»: отправляем только то, что клиент заполнил, остальное — как в таблице
    document.querySelectorAll('.more [data-f]').forEach(e => { if (e.value !== '') p[e.id.slice(2)] = e.value.replace(',', '.'); });
    return p;
  }
  if (tab === 'panel') return { type: radio('p_type'), core: radio('p_core'), thk: +$('p_th').value, width: +$('p_w').value,
    mTop: $('p_mt').value, mBot: $('p_mb').value, ral: radio('p_ral'), area: num('p_area'), mont: radio('p_mont'), deliv: radio('p_deliv'), vat: radio('vat') };
  return { kind: $('m_kind').value, t: num('m_t'), kmd: $('m_kmd').value, paint: radio('m_paint'), deliv: radio('m_deliv'), mont: radio('m_mont'), vat: radio('vat') };
}
function check(p){
  if (tab === 'angar') {
    if (p.L < 6 || p.L > 300) return 'Длина — от 6 до 300 м.';
    if (p.W < 12 || p.W > 36) return 'Ширина (пролёт) — от 12 до 36 м. Шире — посчитаем индивидуально.';
    if (p.H < 4 || p.H > 14) return 'Высота до карниза — от 4 до 14 м.';
  }
  if (tab === 'panel' && (p.area < 10 || p.area > 100000)) return 'Площадь панелей — от 10 м².';
  if (tab === 'mk' && (p.t < 0.1 || p.t > 5000)) return 'Масса — от 0,1 т.';
  if (!p.vat) { $('vat_box').classList.add('bad'); return 'Выберите: без НДС или с НДС 22 %.'; }
  return '';
}

// ---------- Телефон ----------
const phone = $('c_phone');
function digits(){ let d = phone.value.replace(/\D/g,''); if (d[0]==='8') d='7'+d.slice(1); if (d && d[0]!=='7') d='7'+d; return d.slice(0,11); }
phone.addEventListener('input', () => {
  const d = digits(); if (!d) { phone.value=''; return; }
  let s = '+7'; const r = d.slice(1);
  if (r.length) s += ' (' + r.slice(0,3); if (r.length>=3) s += ')';
  if (r.length>3) s += ' ' + r.slice(3,6); if (r.length>6) s += '-' + r.slice(6,8); if (r.length>8) s += '-' + r.slice(8,10);
  phone.value = s; phone.classList.remove('bad');
});
$('c_name').addEventListener('input', e => e.target.classList.remove('bad'));

// ---------- КП ----------
function renderDoc(r, c, no, days){
  const d = new Date(), until = new Date(d.getTime() + days*864e5), ds = x => x.toLocaleDateString('ru-RU');
  const rows = r.items.map((i,k) => '<tr><td>'+(k+1)+'. '+esc(i[0])+'</td><td class="n hide-m">'+fmt(i[1], i[1]%1?1:0)+' '+esc(i[2])+'</td><td class="n hide-m">'+rub(i[3])+'</td><td class="n">'+rub(i[4])+'</td></tr>').join('');
  return '<div class="top"><div class="co"><img src="../assets/img/logo.jpg" alt=""><div><b>'+esc(COMPANY.name)+'</b><div>'+esc(COMPANY.phone)+' · '+esc(COMPANY.email)+'</div></div></div>'
   + '<div class="num"><b>КП № '+esc(no)+'</b>от '+ds(d)+'<br>действует до '+ds(until)+'</div></div>'
   + '<h3>Коммерческое предложение</h3><div class="small" style="color:#8a7240;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px">Предварительный расчёт</div>'
   + '<div class="sub">'+esc(r.kind)+': '+esc(r.title)+'. Для: '+esc(c.name)+(c.city?', '+esc(c.city):'')+'</div>'
   + '<table class="params">'+r.params.map(p => '<tr><td>'+esc(p[0])+'</td><td>'+esc(p[1])+'</td></tr>').join('')+'</table>'
   + '<table><thead><tr><th>Состав работ и материалов</th><th class="n hide-m">Кол-во</th><th class="n hide-m">Цена</th><th class="n">Сумма</th></tr></thead><tbody>'+rows+'</tbody></table>'
   + '<div class="total"><span>Итого'+(r.area?' · ~'+rub(r.total/r.area)+' за м²':'')+'</span><b>'+rub(r.total)+'</b></div>'
   + '<div class="small">'+r.notes.map(esc).join(' ')+'</div>'
   + '<p class="small" style="margin-top:12px"><b>Не входит в расчёт:</b></p><ul class="small">'+r.excluded.map(x => '<li>'+esc(x)+'</li>').join('')+'</ul>'
   + '<div class="foot">Расчёт предварительный: сделан автоматически по введённым параметрам. Окончательная цена — в договоре после уточнения ТЗ и участка. Вопросы: '+esc(COMPANY.phone)+', Telegram '+esc(COMPANY.telegram.replace('https://',''))+'.</div>';
}
function fail(msg){
  $('fail').innerHTML = esc(msg) + ' Позвоните нам: <a href="'+COMPANY.phoneHref+'">'+esc(COMPANY.phone)+'</a> или напишите в <a href="'+COMPANY.telegram+'" target="_blank" rel="noopener">Telegram</a>.';
  $('fail').classList.remove('hidden');
}

let busy = false;
$('go').addEventListener('click', async () => {
  if (busy) return;
  $('fail').classList.add('hidden');
  const name = $('c_name').value.trim(), d = digits(), city = $('c_city').value.trim(), p = params();
  let e = check(p);
  if (name.length < 2) $('c_name').classList.add('bad');
  if (d.length !== 11) phone.classList.add('bad');
  if (!e && name.length < 2 && d.length !== 11) e = 'Укажите имя и телефон.';
  if (!e && name.length < 2) e = 'Укажите имя.';
  if (!e && d.length !== 11) e = 'Проверьте номер телефона: нужно 10 цифр после +7.';
  if (!e && !$('c_agree').checked) e = 'Нужно согласие на обработку данных.';
  $('err').textContent = e; if (e) return;
  if (!SCRIPT_URL) { fail('Калькулятор ещё не подключён к смете.'); return; }

  busy = true; $('go').disabled = true; $('load').classList.remove('hidden');
  try {
    const ctrl = new AbortController(), t = setTimeout(() => ctrl.abort(), 60000);
    const res = await fetch(SCRIPT_URL, {method:'POST', body: JSON.stringify({kind: tab, params: p, name, phone: '+'+d, city, src, hp: $('c_site').value}), signal: ctrl.signal});
    clearTimeout(t);
    const j = await res.json();
    if (!j.ok) throw new Error(j.error === 'busy' ? 'busy' : 'calc');
    $('doc').innerHTML = renderDeck(j.result, {name, city}, j.kp, j.days || 10, COMPANY);
    document.title = 'КП ' + j.kp + ' — ' + COMPANY.name;
    $('form').classList.add('hidden'); $('result').classList.remove('hidden');
    window.scrollTo({top:0, behavior:'smooth'});
  } catch (err) {
    fail(err.message === 'busy' ? 'Сейчас много расчётов, попробуйте через минуту.' : 'Не получилось посчитать автоматически.');
  } finally { busy = false; $('go').disabled = false; $('load').classList.add('hidden'); }
});
$('pdf').addEventListener('click', () => window.print());
$('again').addEventListener('click', () => { $('result').classList.add('hidden'); $('form').classList.remove('hidden'); document.title = 'Расчёт стоимости — ' + COMPANY.name; });

// Открыть нужную вкладку по ссылке: kp/?t=panel или kp/?t=mk
const t0 = new URLSearchParams(location.search).get('t');
if (t0) { const b = document.querySelector('.tab[data-t="'+t0+'"]'); if (b) b.click(); }
hints();
})();
