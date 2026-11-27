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
  ['wall','roof'].forEach(type => {
    const box = $('p_'+type+'_core'), core = radio('p_'+type+'_core') || 'минвата';
    box.innerHTML = PANEL_OPTS.cores[type].map(c => '<label><input type="radio" name="p_'+type+'_core" value="'+c+'"'+(c===core?' checked':'')+'><span>'+c+'</span></label>').join('');
    box.querySelectorAll('input').forEach(e => e.addEventListener('change', hints));
    $('p_'+type+'_hint').textContent = PANEL_OPTS.coreNote[core] || '';
    opts($('p_'+type+'_th'), PANEL_OPTS.thk[type+'|'+core], type === 'roof' ? 150 : 100);
  });
  opts($('p_wall_w'), PANEL_OPTS.widths.wall, 1000);
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

// ---------- Город объекта: все города России, ближайший завод панелей ----------
const cityIn = $('c_city'), cityList = $('c_city_list');
const cnorm = x => String(x).toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ').trim();
const cityLabel = c => c[0] + (c[1] ? ', ' + c[1] : '');
let cityPick = null, cityHits = [], cityAct = -1;
// Дорожное расстояние ≈ расстояние по прямой × 1,25
function kmTo(a, b){ const r = Math.PI/180, dl = (b[1]-a[1])*r, dn = (b[2]-a[2])*r;
  const h = Math.sin(dl/2)**2 + Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin(dn/2)**2;
  return Math.round(6371 * 2 * Math.asin(Math.sqrt(h)) * 1.25 / 10) * 10; }
function nearestFactory(c){ return PANEL_FACTORIES.map(f => [f[0], kmTo([0, c[2], c[3]], f)]).sort((x, y) => x[1] - y[1])[0]; }
function cityHint(){
  const h = $('c_city_hint');
  if (!cityPick) { h.textContent = 'Выберите город из списка. Если объект в посёлке, укажите ближайший город.'; return; }
  if (tab !== 'panel') { h.textContent = cityLabel(cityPick); return; }
  const f = nearestFactory(cityPick);
  h.textContent = 'Ближайший завод-поставщик: ' + f[0] + (f[1] >= 30 ? ', около ' + fmt(f[1]) + ' км до объекта' : '') + '.';
}
function cityDraw(){
  cityList.innerHTML = cityHits.map((c, k) => '<li role="option" data-k="'+k+'"'+(k===cityAct?' class="on"':'')+'>'+esc(c[0])+(c[1]?'<small>'+esc(c[1])+'</small>':'')+'</li>').join('');
  cityList.hidden = !cityHits.length; cityIn.setAttribute('aria-expanded', String(!!cityHits.length));
}
function cityFind(){
  const q = cnorm(cityIn.value);
  cityPick = RU_CITIES.find(c => cnorm(cityLabel(c)) === q) || null;
  const same = RU_CITIES.filter(c => cnorm(c[0]) === q);
  if (!cityPick && same.length === 1) cityPick = same[0];
  cityHits = q.length < 2 || (cityPick && same.length <= 1 && cnorm(cityLabel(cityPick)) === q) ? [] :
    RU_CITIES.filter(c => cnorm(c[0]).startsWith(q)).concat(RU_CITIES.filter(c => !cnorm(c[0]).startsWith(q) && cnorm(c[0]).includes(q))).slice(0, 8);
  cityAct = -1; cityDraw(); cityHint();
  if (cityPick) cityIn.classList.remove('bad');
}
function cityChoose(c){ cityIn.value = cityLabel(c); cityPick = c; cityHits = []; cityDraw(); cityHint(); cityIn.classList.remove('bad'); }
cityIn.addEventListener('input', cityFind);
cityIn.addEventListener('focus', () => { if (!cityPick) cityFind(); });
cityIn.addEventListener('blur', () => setTimeout(() => { cityHits = []; cityDraw(); }, 150));
cityIn.addEventListener('keydown', e => {
  if (!cityHits.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); cityAct = (cityAct + (e.key === 'ArrowDown' ? 1 : -1) + cityHits.length) % cityHits.length; cityDraw(); }
  else if (e.key === 'Enter') { e.preventDefault(); cityChoose(cityHits[Math.max(0, cityAct)]); }
  else if (e.key === 'Escape') { cityHits = []; cityDraw(); }
});
cityList.addEventListener('mousedown', e => { const li = e.target.closest('li'); if (li) { e.preventDefault(); cityChoose(cityHits[+li.dataset.k]); } });

// ---------- Вкладки и подсказки ----------
let tab = 'angar';
document.querySelectorAll('.tab').forEach(b => b.addEventListener('click', () => {
  tab = b.dataset.t;
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('[data-pane]').forEach(x => x.classList.toggle('hidden', x.dataset.pane !== tab));
  cityHint();
}));
function hints(){
  const L = num('a_len'), W = num('a_wid');
  $('a_area_hint').textContent = (L && W ? 'Площадь: ' + fmt(L*W) + ' м² · ' : '') + 'ширина (пролёт) 12–36 м, высота до карниза 4–14 м';
  panelOpts();
  $('a_slab_box').classList.toggle('hidden', radio('a_floor') !== 'монолитная плита');
  $('a_piles_box').classList.toggle('hidden', radio('a_fund') !== 'винтовые сваи');
}
document.querySelectorAll('#form input, #form select').forEach(e => e.addEventListener('change', hints));
document.querySelectorAll('input[name=vat]').forEach(e => e.addEventListener('change', () => $('vat_box').classList.remove('bad')));
['a_len','a_wid'].forEach(id => $(id).addEventListener('input', hints));
$('pol_link').addEventListener('click', e => { e.preventDefault(); $('policy').classList.toggle('hidden'); });

function params(){
  if (tab === 'angar') {
    const p = { L: num('a_len'), W: num('a_wid'), H: num('a_h'), use: $('a_use').value,
      wallThk: $('a_wallThk').value, roofThk: $('a_roofThk').value, wallCore: $('a_core').value, roofCore: $('a_core').value, ral: $('a_ral').value,
      fund: radio('a_fund'), floor: radio('a_floor'),
      gates: num('a_gates'), windows: num('a_win'), doors: num('a_doors'),
      flash: 'нет', gutter: 'нет', vat: radio('vat') };
    if (p.fund === 'винтовые сваи' && $('a_piles').value) p.piles = num('a_piles');
    if (p.floor === 'монолитная плита') { p.slabMode = 'вручную'; p.slabT = radio('a_slabT'); p.xps = 'нет'; }
    return p;
  }
  if (tab === 'panel') {
    const blk = k => $('p_'+k+'_on').checked ? { on: '1', core: radio('p_'+k+'_core'), thk: +$('p_'+k+'_th').value, area: num('p_'+k+'_area'), width: k === 'wall' ? +$('p_wall_w').value : 1000 } : { on: '0' };
    const w = blk('wall'), rf = blk('roof'), first = w.on === '1' ? ['wall', w] : ['roof', rf];
    // type/core/thk/width/area — старый формат, на случай если в таблице ещё прежний код
    return { wall: w, roof: rf, type: first[0], core: first[1].core, thk: first[1].thk, width: first[1].width, area: first[1].area,
      mTop: $('p_mt').value, mBot: $('p_mb').value, ral: radio('p_ral'), mont: radio('p_mont'), deliv: radio('p_deliv'), vat: radio('vat'),
      geo: cityPick ? { city: cityPick[0], region: cityPick[1], lat: cityPick[2], lon: cityPick[3] } : null };
  }
  return { kind: $('m_kind').value, t: num('m_t'), kmd: $('m_kmd').value, paint: radio('m_paint'), deliv: radio('m_deliv'), mont: radio('m_mont'), vat: radio('vat') };
}
function check(p){
  if (tab === 'angar') {
    if (p.L < 6 || p.L > 300) return 'Длина — от 6 до 300 м.';
    if (p.W < 12 || p.W > 36) return 'Ширина (пролёт) — от 12 до 36 м. Шире — посчитаем индивидуально.';
    if (p.H < 4 || p.H > 14) return 'Высота до карниза — от 4 до 14 м.';
  }
  if (tab === 'panel') {
    const on = ['wall','roof'].filter(k => p[k].on === '1');
    if (!on.length) return 'Выберите стеновые или кровельные панели.';
    if (on.some(k => !(p[k].area >= 10 && p[k].area <= 100000))) return 'Площадь панелей — от 10 м².';
    if (!p.geo) { cityIn.classList.add('bad'); return 'Выберите город объекта из списка: от него зависят завод-поставщик и доставка.'; }
  }
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
