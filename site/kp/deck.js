// КП-презентация в стиле «КП склад №1»: слайды 16:9, чертежи строятся по ответу калькулятора владельца.
// renderDeck(r, client, kpNo, days) → HTML. r — ответ Apps Script (result), включая facts из листа «Расчёт».
(function(){
const A = '../assets/img/';
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const nf = (v, d) => Number(Number(v).toFixed(d || 0)).toLocaleString('ru-RU').replace(/[  ]/g, ' ');
const rub = v => nf(Math.round(v)) + ' ₽';
const mln = v => nf(v / 1e6, 2) + ' млн ₽';
const pct = (a, b) => b ? nf(a / b * 100, 1) + ' %' : '';
const mm = v => nf(Math.round(v * 1000));                 // метры → «24 000»
const mark = v => (v >= 0 ? '+' : '') + Number(v).toFixed(3).replace('.', ',');   // +8,000
const LET = 'АБВГДЕЖИКЛМНПРСТУФХЦШЭЮЯ';

// ---------- общие куски слайда ----------
function head(title, accent) {
  return '<div class="d-head"><h2>' + esc(title) + (accent ? ' <em>' + esc(accent) + '</em>' : '') + '</h2>' +
    '<div class="d-logo"><img src="' + A + 'logo-icon.png" alt=""><span>«РСК»<br>ПОКОЛЕНИЯ</span></div></div><i class="d-bar"></i>';
}
function facts(list) {
  return '<div class="d-facts">' + list.filter(Boolean).map(f => '<div><b>' + esc(f[0]) + '</b><span>' + esc(f[1]) + '</span></div>').join('') + '</div>';
}
function card(svg, cls) { return '<div class="d-pic ' + (cls || '') + '">' + svg + '</div>'; }

// ---------- изометрия ----------
const C30 = Math.cos(Math.PI / 6), S30 = 0.5;
function P(x, y, z) { return [(x - y) * C30, (x + y) * S30 - z]; }
function poly(pts, fill, stroke, sw, extra) {
  return '<polygon points="' + pts.map(p => P.apply(null, p).map(n => n.toFixed(2)).join(',')).join(' ') + '" fill="' + fill + '"' +
    (stroke ? ' stroke="' + stroke + '" stroke-width="' + (sw || .08) + '" stroke-linejoin="round"' : '') + (extra || '') + '/>';
}
function line(a, b, stroke, sw, extra) {
  const p = P.apply(null, a), q = P.apply(null, b);
  return '<line x1="' + p[0].toFixed(2) + '" y1="' + p[1].toFixed(2) + '" x2="' + q[0].toFixed(2) + '" y2="' + q[1].toFixed(2) + '" stroke="' + stroke + '" stroke-width="' + (sw || .1) + '"' + (extra || '') + '/>';
}
function box(pts3) {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  pts3.forEach(p => { const q = P.apply(null, p); x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); });
  return [x0, y0, x1, y1];
}
function svgWrap(b, pad, inner) {
  const w = b[2] - b[0] + 2 * pad, h = b[3] - b[1] + 2 * pad;
  return '<svg viewBox="' + (b[0] - pad).toFixed(2) + ' ' + (b[1] - pad).toFixed(2) + ' ' + w.toFixed(2) + ' ' + h.toFixed(2) + '" preserveAspectRatio="xMidYMid meet">' + inner + '</svg>';
}
function tree(x, y, s) {
  const p = P(x, y, 0);
  return '<g transform="translate(' + p[0].toFixed(2) + ' ' + p[1].toFixed(2) + ') scale(' + s + ')"><line x1="0" y1="0" x2="0" y2="-3" stroke="#6b5a3a" stroke-width=".25"/>' +
    '<circle cx="0" cy="-3.6" r="1.5" fill="#7fae62"/><circle cx=".7" cy="-3.1" r="1" fill="#6b9b52"/></g>';
}

function geom(r) {
  const v = r.input || {}, f = r.facts || {};
  const t = String(r.title || '').replace(/,/g, '.').match(/([\d.]+)\s*×\s*([\d.]+)[^\d]+([\d.]+)/) || [];   // «60 × 24 м, высота 8 м»
  const L = +v.L || +t[1] || 30, W = +v.W || +t[2] || 18, H = +v.H || +t[3] || 6;
  const slope = f.slopeRad != null ? +f.slopeRad : Math.atan(0.1);
  const Hr = H + W / 2 * Math.tan(slope);
  const n = Math.max(1, Math.round((f.frames || (Math.round(L / 6) + 1)) - 1));
  const step = L / n;
  const fw = Math.round((f.fachwerkCols || 0) / 2);
  return { L, W, H, Hr, slope, n, step, fw, gates: +v.gates || 0, doors: +v.doors || 0, windows: +v.windows || 0,
    trusses: (v.scheme || 'КП (фермы)') !== 'П³ (балки)', fund: v.fund || 'винтовые сваи', floor: v.floor || 'плиты ПАГ' };
}

// Здание целиком: стены из сэндвич-панелей, двускатная кровля, ворота и окна на длинном фасаде.
function isoBuilding(g) {
  const { L, W, H, Hr } = g, o = [];
  const pad = Math.max(L, W) * 0.08;
  o.push(poly([[-pad, -pad, 0], [L + pad, -pad, 0], [L + pad, W + pad * 1.6, 0], [-pad, W + pad * 1.6, 0]], '#efe6d3', null, 0, ' opacity=".55"'));
  o.push(poly([[0, 0, H], [L, 0, H], [L, W / 2, Hr], [0, W / 2, Hr]], '#c9ced3', '#9aa1a8', .06));
  o.push(poly([[0, W / 2, Hr], [L, W / 2, Hr], [L, W, H], [0, W, H]], '#e3e6e9', '#9aa1a8', .06));
  o.push(poly([[0, W, 0], [L, W, 0], [L, W, H], [0, W, H]], '#3b3f45', '#25282c', .06));
  o.push(poly([[L, 0, 0], [L, W, 0], [L, W, H], [L, W / 2, Hr], [L, 0, H]], '#4a4f56', '#25282c', .06));
  for (let z = 1; z < H; z += 1) o.push(line([0, W, z], [L, W, z], '#33373c', .03));
  for (let x = g.step; x < L - .01; x += g.step) o.push(line([x, W, 0], [x, W, H], '#2a2d31', .07));
  o.push(poly([[0, W, 0], [L, W, 0], [L, W, .45], [0, W, .45]], '#26292d'));
  o.push(poly([[L, 0, 0], [L, W, 0], [L, W, .45], [L, 0, .45]], '#2f3237'));
  // ворота по длинному фасаду, двери и окна
  const gates = Math.min(g.gates, Math.max(0, g.n - 1));
  const bays = []; for (let i = 0; i < g.n; i++) bays.push(i);
  const gateBays = gates ? Array.from({ length: gates }, (_, k) => Math.floor((k + 1) * g.n / (gates + 1))) : [];
  bays.forEach(i => {
    const x0 = i * g.step, xm = x0 + g.step / 2;
    if (gateBays.indexOf(i) >= 0) {
      const gw = Math.min(3, g.step * .6), gh = Math.min(3.5, H * .7);
      o.push(poly([[xm - gw / 2, W, 0], [xm + gw / 2, W, 0], [xm + gw / 2, W, gh], [xm - gw / 2, W, gh]], '#8b9299', '#5d636a', .05));
      for (let z = .45; z < gh; z += .45) o.push(line([xm - gw / 2, W, z], [xm + gw / 2, W, z], '#6e757c', .03));
    } else if (g.windows && H > 3.2) {
      const ww = Math.min(3, g.step * .5), z0 = Math.min(H * .55, H - 1.6);
      o.push(poly([[xm - ww / 2, W, z0], [xm + ww / 2, W, z0], [xm + ww / 2, W, z0 + .9], [xm - ww / 2, W, z0 + .9]], '#5fb0d3', '#2d6f8c', .05));
    }
  });
  if (g.doors) { const x = g.step * .25; o.push(poly([[x, W, 0], [x + 1, W, 0], [x + 1, W, 2.1], [x, W, 2.1]], '#5fb0d3', '#2d6f8c', .05)); }
  if (g.windows && H > 3.2) { const y = W / 2, z0 = Math.min(H * .55, H - 1.6); o.push(poly([[L, y - 1.5, z0], [L, y + 1.5, z0], [L, y + 1.5, z0 + .9], [L, y - 1.5, z0 + .9]], '#5fb0d3', '#2d6f8c', .05)); }
  const s = Math.max(L, W) / 40;
  o.push(tree(-pad * .3, W + pad * .6, s), tree(L + pad * .5, W * .4, s), tree(L * .15, W + pad * 1.2, s * .9), tree(L + pad * .3, W + pad * .9, s));
  return svgWrap(box([[-pad, -pad, 0], [L + pad, -pad, 0], [L + pad, W + pad * 1.6, 0], [-pad, W + pad * 1.6, 0], [0, 0, Hr + 5], [L, 0, Hr + 5], [0, W / 2, Hr + 3]]), 1, o.join(''));
}

// Металлический каркас: рамы с фермами или балками, прогоны, связи.
function isoFrame(g, f) {
  const { L, W, H, Hr } = g, o = [], col = '#22252a', gold = '#d9a43a', br = '#e07a3a';
  o.push(poly([[0, 0, 0], [L, 0, 0], [L, W, 0], [0, W, 0]], '#eceff2', '#c9ced3', .06));
  const d = Math.max(1, W / 14);
  const rows = Math.max(2, Math.round((f.purlinRows || 6) / 2));
  for (let i = 0; i <= g.n; i++) {
    const x = i * g.step;
    o.push(line([x, 0, 0], [x, 0, H], col, .28));
  }
  // прогоны по скатам
  for (let k = 0; k <= rows; k++) {
    const t = k / rows;
    o.push(line([0, t * W / 2, H + t * (Hr - H)], [L, t * W / 2, H + t * (Hr - H)], gold, .09));
    o.push(line([0, W - t * W / 2, H + t * (Hr - H)], [L, W - t * W / 2, H + t * (Hr - H)], gold, .09));
  }
  for (let i = 0; i <= g.n; i++) {
    const x = i * g.step;
    o.push(line([x, 0, H], [x, W / 2, Hr], col, .2), line([x, W / 2, Hr], [x, W, H], col, .2));
    if (g.trusses) {
      o.push(line([x, 0, H - d], [x, W, H - d], col, .14));
      const m = Math.max(4, Math.round(W / 3));
      for (let j = 0; j < m; j++) {
        const y0 = j * W / m, y1 = (j + 1) * W / m;
        const zt = y => H + (y <= W / 2 ? y : W - y) / (W / 2) * (Hr - H);
        o.push(line(j % 2 ? [x, y0, zt(y0)] : [x, y0, H - d], j % 2 ? [x, y1, H - d] : [x, y1, zt(y1)], col, .07));
      }
    }
  }
  // связи в торцевых пролётах по длинным стенам
  [[0, g.step], [L - g.step, L]].forEach(b => {
    [0, W].forEach(y => { o.push(line([b[0], y, 0], [b[1], y, H], br, .08), line([b[1], y, 0], [b[0], y, H], br, .08)); });
  });
  o.push(line([0, 0, H], [L, 0, H], gold, .16), line([0, W, H], [L, W, H], gold, .16));
  for (let i = 0; i <= g.n; i++) { const x = i * g.step; o.push(line([x, W, 0], [x, W, H], col, .28)); }
  // фахверк торцов
  for (let k = 1; k <= g.fw; k++) { const y = k * W / (g.fw + 1); const z = H + (y <= W / 2 ? y : W - y) / (W / 2) * (Hr - H);
    o.push(line([0, y, 0], [0, y, z], '#5a5f66', .16), line([L, y, 0], [L, y, z], '#5a5f66', .16)); }
  return svgWrap(box([[0, 0, 0], [L, 0, 0], [L, W, 0], [0, W, 0], [0, 0, Hr], [L, 0, Hr], [0, W, Hr], [0, W / 2, Hr], [L, W / 2, Hr]]), 1.5, o.join(''));
}

// План с осями и колоннами.
function plan(g, f, mode) {
  const { L, W } = g;
  const VW = 640, k = Math.min((VW - 90) / L, 230 / W), w = L * k, h = W * k, x0 = 48, y0 = 22;
  const o = [];
  const X = x => x0 + x * k, Y = y => y0 + h - y * k;   // ось А — внизу
  const lettersY = [0]; for (let j = 1; j <= g.fw; j++) lettersY.push(j * W / (g.fw + 1)); lettersY.push(W);
  if (mode === 'found' && g.floor === 'монолитная плита') o.push('<rect x="' + X(0) + '" y="' + Y(W) + '" width="' + w + '" height="' + h + '" fill="#e8ebef"/>');
  // сетка осей
  for (let i = 0; i <= g.n; i++) o.push('<line x1="' + X(i * g.step) + '" y1="' + (Y(W) - 6) + '" x2="' + X(i * g.step) + '" y2="' + (Y(0) + 16) + '" stroke="#b9bfc6" stroke-width=".6" stroke-dasharray="3 3"/>');
  lettersY.forEach(y => o.push('<line x1="' + (X(0) - 16) + '" y1="' + Y(y) + '" x2="' + (X(L) + 6) + '" y2="' + Y(y) + '" stroke="#b9bfc6" stroke-width=".6" stroke-dasharray="3 3"/>'));
  o.push('<rect x="' + X(0) + '" y="' + Y(W) + '" width="' + w + '" height="' + h + '" fill="none" stroke="#1d1f23" stroke-width="2.4"/>');
  // колонны
  const cs = 5.5;
  for (let i = 0; i <= g.n; i++) [0, W].forEach(y => {
    const cx = X(i * g.step), cy = Y(y);
    if (mode === 'found') o.push(g.fund === 'монолит' ? '<rect x="' + (cx - 8) + '" y="' + (cy - 8) + '" width="16" height="16" fill="#e7d9b5" stroke="#b89a55" stroke-width=".8"/>'
      : '<circle cx="' + (cx - 4) + '" cy="' + cy + '" r="2.6" fill="#b89a55"/><circle cx="' + (cx + 4) + '" cy="' + cy + '" r="2.6" fill="#b89a55"/>');
    o.push('<rect x="' + (cx - cs / 2) + '" y="' + (cy - cs / 2) + '" width="' + cs + '" height="' + cs + '" fill="#1d1f23"/>');
  });
  lettersY.slice(1, -1).forEach(y => [0, L].forEach(x => o.push('<rect x="' + (X(x) - 2.5) + '" y="' + (Y(y) - 2.5) + '" width="5" height="5" fill="#c99a3d"/>')));
  // ворота по оси А
  if (mode === 'plan' && g.gates) {
    const gates = Math.min(g.gates, Math.max(1, g.n - 1));
    for (let q = 0; q < gates; q++) {
      const b = Math.floor((q + 1) * g.n / (gates + 1)), xm = X((b + .5) * g.step), gw = Math.min(3, g.step * .6) * k;
      o.push('<rect x="' + (xm - gw / 2) + '" y="' + (Y(0) - 3) + '" width="' + gw + '" height="6" fill="#d9b05e"/><text x="' + xm + '" y="' + (Y(0) - 7) + '" class="t-s g">ворота</text>');
    }
  }
  // марки осей
  for (let i = 0; i <= g.n; i++) o.push('<circle cx="' + X(i * g.step) + '" cy="' + (Y(0) + 24) + '" r="7" fill="#fff" stroke="#1d1f23" stroke-width=".8"/><text x="' + X(i * g.step) + '" y="' + (Y(0) + 26.6) + '" class="t-a">' + (i + 1) + '</text>');
  lettersY.forEach((y, j) => o.push('<circle cx="' + (X(0) - 24) + '" cy="' + Y(y) + '" r="7" fill="#fff" stroke="#1d1f23" stroke-width=".8"/><text x="' + (X(0) - 24) + '" y="' + (Y(y) + 2.6) + '" class="t-a">' + LET[j] + '</text>'));
  // размеры
  const yd = Y(0) + 42;
  o.push('<line x1="' + X(0) + '" y1="' + yd + '" x2="' + X(L) + '" y2="' + yd + '" stroke="#1d1f23" stroke-width=".7"/>');
  for (let i = 0; i <= g.n; i++) o.push('<line x1="' + X(i * g.step) + '" y1="' + (yd - 3) + '" x2="' + X(i * g.step) + '" y2="' + (yd + 3) + '" stroke="#1d1f23" stroke-width=".7"/>');
  o.push('<text x="' + X(L / 2) + '" y="' + (yd + 11) + '" class="t-d">' + mm(L) + ' (' + g.n + ' × ' + mm(g.step) + ')</text>');
  const xd = X(L) + 18;
  o.push('<line x1="' + xd + '" y1="' + Y(0) + '" x2="' + xd + '" y2="' + Y(W) + '" stroke="#1d1f23" stroke-width=".7"/><text transform="translate(' + (xd + 10) + ' ' + Y(W / 2) + ') rotate(-90)" class="t-d">' + mm(W) + '</text>');
  if (mode === 'plan') o.push('<text x="' + X(L / 2) + '" y="' + (Y(W / 2) - 2) + '" class="t-b">Помещение ' + nf(L * W) + ' м²</text><text x="' + X(L / 2) + '" y="' + (Y(W / 2) + 10) + '" class="t-s">пролёт ' + nf(W, 1) + ' м без колонн внутри</text>');
  if (mode === 'found') o.push('<text x="' + X(L / 2) + '" y="' + (Y(W / 2) - 2) + '" class="t-b">' + (g.floor === 'монолитная плита' ? 'Монолитная плита пола' : g.floor === 'плиты ПАГ' ? 'Пол из плит ПАГ' : 'Без пола') + '</text>' +
    '<text x="' + X(L / 2) + '" y="' + (Y(W / 2) + 10) + '" class="t-s">' + (g.fund === 'монолит' ? 'столбчатые монолитные фундаменты под колонны' : 'винтовые сваи под колонны') + '</text>');
  return '<svg viewBox="0 0 ' + VW + ' ' + (h + 90) + '">' + o.join('') + '</svg>';
}

// Поперечный разрез.
function section(g, f) {
  const { W, H, Hr } = g, VW = 600, k = Math.min(420 / W, 220 / (Hr + 1.5)), x0 = 70, base = 30 + Hr * k;
  const X = y => x0 + y * k, Z = z => base - z * k, o = [], col = '#1d1f23';
  const d = Math.max(1, W / 14);
  o.push('<rect x="' + (X(0) - 14) + '" y="' + Z(0) + '" width="' + (W * k + 28) + '" height="16" fill="#efe3c4"/>');
  if (g.floor === 'монолитная плита') o.push('<rect x="' + X(0) + '" y="' + (Z(0) - 1) + '" width="' + W * k + '" height="7" fill="#b9c0c8"/>');
  [0, W].forEach(y => {
    if (g.fund === 'монолит') o.push('<polygon points="' + (X(y) - 12) + ',' + (Z(0) + 16) + ' ' + (X(y) + 12) + ',' + (Z(0) + 16) + ' ' + (X(y) + 7) + ',' + Z(0) + ' ' + (X(y) - 7) + ',' + Z(0) + '" fill="#9aa3ad"/>');
    else o.push('<line x1="' + X(y) + '" y1="' + Z(0) + '" x2="' + X(y) + '" y2="' + (Z(0) + 34) + '" stroke="#8a6d33" stroke-width="3"/>');
    o.push('<rect x="' + (X(y) - 4) + '" y="' + Z(H) + '" width="8" height="' + H * k + '" fill="' + col + '"/>');
  });
  o.push('<polyline points="' + X(0) + ',' + Z(H) + ' ' + X(W / 2) + ',' + Z(Hr) + ' ' + X(W) + ',' + Z(H) + '" fill="none" stroke="#c99a3d" stroke-width="5"/>');
  o.push('<polyline points="' + X(0) + ',' + Z(H) + ' ' + X(W / 2) + ',' + Z(Hr) + ' ' + X(W) + ',' + Z(H) + '" fill="none" stroke="' + col + '" stroke-width="1.6"/>');
  if (g.trusses) {
    o.push('<line x1="' + X(0) + '" y1="' + Z(H - d) + '" x2="' + X(W) + '" y2="' + Z(H - d) + '" stroke="' + col + '" stroke-width="1.4"/>');
    const m = Math.max(4, Math.round(W / 3)), zt = y => H + (y <= W / 2 ? y : W - y) / (W / 2) * (Hr - H);
    for (let j = 0; j < m; j++) { const a = j * W / m, b = (j + 1) * W / m;
      o.push('<line x1="' + X(a) + '" y1="' + Z(j % 2 ? zt(a) : H - d) + '" x2="' + X(b) + '" y2="' + Z(j % 2 ? H - d : zt(b)) + '" stroke="' + col + '" stroke-width=".9"/>'); }
  }
  const marks = [[0, '±0,000'], [H, mark(H)], [Hr, mark(Hr)]];
  if (g.trusses) marks.push([H - d, mark(H - d)]);
  marks.forEach(m => o.push('<line x1="' + (X(W) + 6) + '" y1="' + Z(m[0]) + '" x2="' + (X(W) + 22) + '" y2="' + Z(m[0]) + '" stroke="' + col + '" stroke-width=".7"/><text x="' + (X(W) + 25) + '" y="' + (Z(m[0]) + 3) + '" class="t-m">' + m[1] + '</text>'));
  o.push('<text x="' + X(W / 2) + '" y="' + (Z(Hr) - 8) + '" class="t-s">кровля — сэндвич-панели, уклон ' + nf(Math.tan(g.slope) * 100) + ' %</text>');
  o.push('<line x1="' + X(0) + '" y1="' + (Z(0) + 28) + '" x2="' + X(W) + '" y2="' + (Z(0) + 28) + '" stroke="' + col + '" stroke-width=".7"/><text x="' + X(W / 2) + '" y="' + (Z(0) + 40) + '" class="t-d">' + mm(W) + '</text>');
  o.push('<text x="' + X(0) + '" y="' + (Z(0) + 40) + '" class="t-d">А</text><text x="' + X(W) + '" y="' + (Z(0) + 40) + '" class="t-d">' + LET[g.fw + 1] + '</text>');
  return '<svg viewBox="0 0 ' + VW + ' ' + (base + 50) + '">' + o.join('') + '</svg>';
}

// Сэндвич-панель в разрезе.
function panelPie(wall, roof) {
  return '<svg viewBox="0 0 760 260">' +
    '<polygon points="40,70 330,70 370,45 80,45" fill="#5b6067"/><rect x="40" y="70" width="290" height="10" fill="#6b7178"/>' +
    '<polygon points="330,70 370,45 370,55 330,80" fill="#4a4f55"/>' +
    '<rect x="40" y="80" width="290" height="90" fill="#f2c94c"/><polygon points="330,80 370,55 370,145 330,170" fill="#e0b53c"/>' +
    '<rect x="40" y="170" width="290" height="10" fill="#c7ccd2"/><polygon points="330,170 370,145 370,155 330,180" fill="#b5bbc2"/>' +
    '<g stroke="#1d1f23" stroke-width="1"><line x1="372" y1="50" x2="400" y2="50"/><line x1="372" y1="110" x2="400" y2="110"/><line x1="372" y1="152" x2="400" y2="152"/></g>' +
    '<text x="405" y="54" class="t-l">Стальной лист с полимерным покрытием</text>' +
    '<text x="405" y="114" class="t-l">Минеральная вата: стены ' + esc(wall) + ' мм, кровля ' + esc(roof) + ' мм</text>' +
    '<text x="405" y="156" class="t-l">Внутренний стальной лист</text>' +
    '<text x="40" y="215" class="t-s" style="text-anchor:start">Негорючий утеплитель — для склада и производства</text></svg>';
}

// ---------- группы сметы ----------
const GROUPS = [
  ['Проектирование', /^Проектирование|^Разработка КМД/],
  ['Металлокаркас', /металлоконструкц|^Автокран на монтаже|^Подъёмник|подъёмника/i],
  ['Стены и кровля', /сэндвич|^Расходники|асонных|^Фасонные|^Водосток|^Снегозадерж|кровля/i],
  ['Фундамент и пол', /сва[ия]|фундамент|грунта|цокол|ПАГ|плита|^Профнастил|отмостк/i],
  ['Ворота, окна, двери', /^Ворота|^Окна|^Двер/],
  ['Доставка и разгрузка', /^Доставка|^Разгрузка/],
  ['Прочее', /./]
];
function grouped(items) {
  const g = GROUPS.map(x => ({ name: x[0], re: x[1], rows: [], sum: 0 }));
  items.forEach(it => {
    const name = it[0];
    let t = g.find(x => x.name === 'Доставка и разгрузка' && x.re.test(name)) || g.find(x => x.re.test(name));
    t.rows.push(it); t.sum += it[4];
  });
  return g.filter(x => x.rows.length);
}

// ---------- слайды ----------
function renderDeck(r, client, no, days, C) {
  const ang = r.kind === 'Ангар под ключ', g = ang ? geom(r) : null, f = r.facts || {}, v = r.input || {};
  const vat = (r.params.find(p => p[0] === 'НДС') || [0, ''])[1];
  const vatSum = r.vatTotal || 0;
  const withVat = vat === '22 %' || vat === '5 %';
  const vl = withVat ? 'с НДС ' + vat : 'без НДС', VL = vl.toUpperCase();
  const d0 = new Date(), until = new Date(d0.getTime() + days * 864e5), ds = x => x.toLocaleDateString('ru-RU');
  const title = ang ? 'Ангар ' + nf(g.L, 1) + ' × ' + nf(g.W, 1) + ' м' : r.kind;
  const sub = ang ? (v.use || 'Склад') + (client.city ? ' · ' + client.city : '') : (client.city || '');
  const S = [];

  // 1. Обложка
  function coverTitle() {
    let t1, t2 = '';
    if (ang) { t1 = (v.use || 'Склад').replace('Производство / цех', 'Производство'); t2 = nf(g.L, 1) + ' × ' + nf(g.W, 1) + ' м'; }
    else if (r.kind === 'Сэндвич-панели') { t1 = 'Сэндвич-\u200bпанели'; t2 = (r.params.find(p => p[0] === 'Площадь') || [0, ''])[1]; }
    else { t1 = 'Металло-\u200bконструкции'; t2 = (r.params.find(p => p[0] === 'Масса') || [0, ''])[1]; }
    const longest = Math.max.apply(null, t1.split(/[\s\u200b]+/).map(w => w.length));
    return '<h1 class="' + (longest > 11 ? 'long' : '') + '">' + esc(t1.toUpperCase()).replace(/\u200b/g, '<br>') + (t2 ? '<br><em>' + esc(String(t2).toUpperCase()) + '</em>' : '') + '</h1>';
  }
  const desc = ang ? 'Металлокаркас, сэндвич-панели ' + (v.wallThk || '') + '/' + (v.roofThk || '') + ' мм, высота до карниза ' + nf(g.H, 1) + ' м, ' +
    (g.fund === 'монолит' ? 'монолитный фундамент' : 'винтовые сваи') + (g.floor === 'нет' ? '' : ', ' + (g.floor === 'плиты ПАГ' ? 'пол из плит ПАГ' : 'монолитная плита пола')) : r.title;
  S.push('<div class="d-cover"><div class="d-cl">' +
    '<div class="d-brand"><img src="' + A + 'logo-icon.png" alt=""><span>«РСК»<br>ПОКОЛЕНИЯ</span><i></i><small>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ<br>ПРЕДВАРИТЕЛЬНЫЙ РАСЧЁТ · № ' + esc(no) + '</small></div>' +
    '<div class="d-kick">' + esc(sub.toUpperCase()) + '</div>' + coverTitle() + '<i class="d-bar"></i>' +
    '<p class="d-desc">' + esc(desc) + '</p><p class="d-meta">Для: ' + esc(client.name) + (client.city ? ', ' + esc(client.city) : '') + '<br>от ' + ds(d0) + ', действует до ' + ds(until) + '</p>' +
    '<div class="d-stats"><div class="gold"><b>15+ лет</b><span>успешной реализации объектов с 2011 года</span></div><div><b>200+</b><span>завершённых объектов промышленного и коммерческого строительства</span></div></div></div>' +
    '<div class="d-cr">' + (ang ? '<div class="d-iso">' + isoBuilding(g) + '</div>' : '<img class="d-ph" src="' + A + (r.kind === 'Сэндвич-панели' ? 'bc-fasad' : 'bc-montazh') + '-s.jpg" alt="">') +
    '<div class="d-contact"><div><b>РСК «ПОКОЛЕНИЯ»</b><span>Строительная компания</span></div><div class="r"><b>' + esc(C.phone) + '</b><span>' + esc(C.email) + '</span></div></div></div></div>');

  // 2. Предложение в цифрах
  const steel = f.steelT || (r.items.find(i => /^Изготовление металлоконструкций/.test(i[0])) || [])[1];
  const nums = ang ? [
    [nf(g.L * g.W) + ' м²', 'площадь застройки ' + nf(g.L, 1) + ' × ' + nf(g.W, 1) + ' м в осях'],
    steel ? [nf(steel, 1) + ' т', 'металлоконструкций каркаса, ' + nf(f.steelKgM2 || 0) + ' кг/м²'] : null,
    f.slabV ? [nf(f.slabV, 1) + ' м³', 'бетона в плите пола ' + nf(f.slabT) + ' мм'] : f.piles ? [nf(f.piles) + ' шт', 'винтовых свай под колонны'] : f.footings ? [nf(f.footings) + ' шт', 'монолитных фундаментов под колонны'] : null,
    f.wallM2 ? [nf(f.wallM2) + ' м²', 'стеновых сэндвич-панелей; кровля ' + nf(f.roofM2 || 0) + ' м²'] : null
  ].filter(Boolean) : r.params.slice(0, 4).map(p => [p[1], p[0]]);
  S.push(head('Предложение в цифрах') + '<div class="d-kpis">' + (withVat ? '<div><small>В ТОМ ЧИСЛЕ НДС ' + esc(vat) + '</small><b>' + rub(vatSum || 0) + '</b></div>' : '<div><small>НДС</small><b>не включён</b></div>') +
    '<div class="dark"><small>ИТОГО ' + esc(VL) + '</small><b>' + (r.total >= 1e6 ? mln(r.total) : rub(r.total)) + '</b></div>' +
    (ang ? '<div><small>ЦЕНА ЗА М² ЗАСТРОЙКИ</small><b>' + rub(r.total / g.L / g.W) + '</b></div>' : '<div><small>ПОЗИЦИЙ В РАСЧЁТЕ</small><b>' + r.items.length + '</b></div>') + '</div>' +
    '<div class="d-nums">' + nums.map(n => '<div><b>' + esc(n[0]) + '</b><span>' + esc(n[1]) + '</span></div>').join('') + '</div>' +
    '<p class="d-p">Расчёт сделан автоматически по калькулятору стоимости РСК «Поколения» по введённым параметрам. Окончательная цена — в договоре после уточнения ТЗ, геологии и участка.</p>' +
    (ang ? '<div class="d-row2"><div class="d-pic">' + isoBuilding(g) + '</div><div class="d-term"><small>СРОК МОНТАЖА</small><b>≈ ' + nf(r.days || 0) + ' дней</b><span>каркас, стены и кровля — по графику калькулятора; полы и отделка — по графику после договора</span></div></div>' : ''));

  if (ang) {
    // 3. Общий вид
    S.push(head('Проект: общий вид') + '<div class="d-split">' + card(isoBuilding(g), 'tall') + facts([
      [nf(g.L, 1) + ' × ' + nf(g.W, 1) + ' м', 'размеры в осях, ' + nf(g.L * g.W) + ' м²'],
      ['до ' + mark(g.Hr) + ' м', 'высота в коньке; до карниза ' + mark(g.H)],
      ['Кровля из сэндвич-панелей', nf(v.roofThk || 0) + ' мм, двускатная, уклон ' + nf(Math.tan(g.slope) * 100) + ' %'],
      ['Стены ' + nf(v.wallThk || 0) + ' мм', 'сэндвич-панели на минвате' + (v.layout ? ', ' + v.layout + ' раскладка' : '')]]) + '</div>');
    // 4. Каркас
    S.push(head('Металлический каркас') + '<div class="d-split">' + card(isoFrame(g, f), 'tall') + facts([
      ['Рамы — ' + nf(g.n + 1) + ' шт.', 'шаг ' + nf(g.step, 2) + ' м, колонн по осям А и ' + LET[g.fw + 1] + ' — ' + nf((g.n + 1) * 2) + ' шт.'],
      [(g.trusses ? 'Фермы' : 'Стропильные балки') + ' пролётом ' + nf(g.W, 1) + ' м', g.trusses ? 'рамы с фермами' : 'рамы из балок'],
      ['Прогоны — ' + nf(f.purlinRows || 0) + ' рядов', 'по скатам кровли, под кровельные панели'],
      [f.fachwerkCols ? 'Фахверк — ' + nf(f.fachwerkCols) + ' стоек' : 'Связи', 'вертикальные связи в торцевых пролётах' + (f.fachwerkCols ? ', стойки фахверка на торцах' : '')]]) + '</div>');
    // 5. План
    S.push(head('План и схема колонн') + '<div class="d-split w">' + card(plan(g, f, 'plan')) + facts([
      ['Помещение ' + nf(g.L * g.W) + ' м²', 'единое пространство, пролёт ' + nf(g.W, 1) + ' м'],
      ['Оси 1–' + (g.n + 1) + ' / А–' + LET[g.fw + 1], 'шаг рам ' + nf(g.step, 2) + ' м'],
      g.gates ? ['Ворота — ' + g.gates + ' шт.', 'секционные с автоматикой, по оси А'] : null,
      ['Колонн всего — ' + nf(f.colsAll || (g.n + 1) * 2), 'рамные и фахверковые (золотые на схеме)']]) + '</div>');
    // 6. Разрез
    S.push(head('Поперечный разрез') + '<div class="d-split w">' + card(section(g, f)) + facts([
      ['Пролёт ' + nf(g.W, 1) + ' м', (g.trusses ? 'фермы' : 'балки') + ' опираются на колонны рам'],
      ['Высота ' + mark(g.H) + ' / ' + mark(g.Hr), 'до карниза / в коньке'],
      ['Снеговая нагрузка ' + nf(f.snow || 0, 1) + ' кПа', v.snowReg ? 'снеговой район ' + v.snowReg : 'по СП 20.13330'],
      [g.floor === 'монолитная плита' ? 'Плита ' + nf(f.slabT || 0) + ' мм' : g.floor === 'плиты ПАГ' ? 'Пол из плит ПАГ' : 'Без пола', g.floor === 'монолитная плита' ? 'армированная плита по песчано-щебёночной подушке' : '']]) + '</div>');
    // 7. Фундамент
    S.push(head('Фундамент и пол') + '<div class="d-split w">' + card(plan(g, f, 'found')) + facts([
      g.fund === 'монолит' ? [nf(f.footings || 0) + ' фундаментов', 'столбчатые монолитные, бетон ' + nf(f.footV || 0, 1) + ' м³, арматура ' + nf((f.footRebar || 0) / 1000, 1) + ' т'] : [nf(f.piles || 0) + ' винтовых свай', 'Ø133 с оголовками, длина ' + nf(f.pileLen || 0, 1) + ' м'],
      f.bored ? [nf(f.bored) + ' буронабивных свай', 'требуются по грунту'] : null,
      g.floor === 'монолитная плита' ? [nf(f.slabV || 0, 1) + ' м³ бетона', 'плита ' + nf(f.slabT || 0) + ' мм, арматура ' + nf((f.slabRebar || 0) / 1000, 1) + ' т'] : g.floor === 'плиты ПАГ' ? [nf(f.pag || 0) + ' плит ПАГ', '6 × 2 м по щебню'] : null,
      g.floor === 'монолитная плита' ? ['Подушка', 'песок ' + nf(f.sand || 0) + ' м³, щебень ' + nf(f.gravel || 0) + ' м³'] : null,
      f.anchors ? [nf(f.anchors) + ' анкерных болтов', 'крепление баз колонн'] : null]) + '</div>');
    // 8. Ведомость металла
    const steelRows = [['Колонны рам', f.colsKg], [(g.trusses ? 'Фермы' : 'Стропильные балки'), f.raftersKg], ['Карнизные балки', f.eaveKg], ['Прогоны', f.purlinsKg],
      ['Связи и укосины', (f.wallBrKg || 0) + (f.roofBrKg || 0) + (f.kneeKg || 0)], ['Фахверк торцов', f.fachwerkKg], ['Ригели стен', f.girtsKg],
      ['Нижний прогон-швеллер', f.channelKg], ['Узлы, пластины, болты', f.nodesKg]].filter(x => x[1] > 0);
    if (steelRows.length) S.push(head('Ведомость металлоконструкций') + '<div class="d-split"><table class="d-tbl"><thead><tr><th>Группа элементов</th><th class="n">Масса, т</th></tr></thead><tbody>' +
      steelRows.map(x => '<tr><td>' + esc(x[0]) + '</td><td class="n">' + nf(x[1] / 1000, 1) + '</td></tr>').join('') +
      '</tbody><tfoot><tr><td>Итого металла</td><td class="n">' + nf(f.steelT || 0, 1) + '</td></tr></tfoot></table>' + facts([
        [nf(f.steelKgM2 || 0) + ' кг/м²', 'металлоёмкость каркаса'],
        ['Сталь ' + (v.steel || 'С255'), 'окраска грунт-эмалью входит в смету'],
        [nf(f.tripsSteel || 0) + ' рейсов', 'доставка металлоконструкций на объект']]) + '</div><p class="d-note">Массы — по калькулятору стоимости, уточняются в проекте КМ и чертежах КМД.</p>');
    // 9. Стены и кровля
    S.push(head('Стены и кровля') + '<div class="d-split">' + card(panelPie(v.wallThk || 100, v.roofThk || 120), 'tall') + facts([
      [nf(f.wallM2 || 0) + ' м²', 'стеновых сэндвич-панелей ' + (v.wallThk || '') + ' мм'],
      [nf(f.roofM2 || 0) + ' м²', 'кровельных сэндвич-панелей ' + (v.roofThk || '') + ' мм'],
      f.flashing && v.flash !== 'нет' ? [nf(f.flashing) + ' м.п.', 'фасонных элементов: углы, карнизы, конёк, обрамления'] : null,
      v.gutter !== 'нет' ? ['Водосток и снегозадержатели', 'по обоим скатам кровли'] : null]) + '</div>');
  }

  // Из чего складывается цена
  const gr = grouped(r.items), tot = r.total || 1;
  S.push(head('Из чего складывается цена') + '<div class="d-groups">' + gr.map((x, i) => {
    const top = x.rows.slice().sort((a, b) => b[4] - a[4]).slice(0, 2);
    const max = gr.reduce((m, y) => Math.max(m, y.sum), 0);
    return '<div class="' + (x.sum === max ? 'dark' : '') + '"><small>' + esc(x.name.toUpperCase()) + '</small><b>' + rub(x.sum) + ' <em>' + pct(x.sum, tot) + '</em></b><ul>' +
      top.map(t => '<li>' + esc(t[0].replace(/\s*\(.*?\)\s*/g, ' ').trim()) + ': ' + rub(t[4]) + '</li>').join('') + '</ul></div>';
  }).join('') + '</div><div class="d-total"><span>Итого ' + esc(vl) + '</span><b>' + rub(r.total) + '</b>' + (withVat ? '<span>в том числе НДС: <b>' + rub(vatSum) + '</b></span>' : '') + '</div>');

  // Стоимость по разделам (таблицы по ~13 строк)
  const rows = []; let n = 0;
  gr.forEach(x => { rows.push({ h: x.name, sum: x.sum }); x.rows.forEach(it => rows.push({ n: ++n, it: it })); });
  const per = 15, pages = Math.max(1, Math.ceil(rows.length / per));
  for (let p = 0; p < pages; p++) {
    const part = rows.slice(p * per, (p + 1) * per), last = p === pages - 1;
    S.push(head('Стоимость по разделам' + (pages > 1 ? ' (' + (p + 1) + '/' + pages + ')' : '')) + '<table class="d-tbl wide"><thead><tr><th>№</th><th>Позиция</th><th class="n">Объём</th><th class="n">Цена' + (withVat ? ' с НДС' : '') + ', ₽</th><th class="n">Сумма' + (withVat ? ' с НДС' : '') + ', ₽</th></tr></thead><tbody>' +
      part.map(x => x.h ? '<tr class="grp"><td></td><td>' + esc(x.h.toUpperCase()) + '</td><td></td><td></td><td class="n">' + nf(Math.round(x.sum)) + '</td></tr>'
        : '<tr><td>' + x.n + '</td><td>' + esc(x.it[0]) + '</td><td class="n">' + nf(x.it[1], x.it[1] % 1 ? 1 : 0) + ' ' + esc(x.it[2]) + '</td><td class="n">' + nf(x.it[3], 2) + '</td><td class="n">' + nf(Math.round(x.it[4])) + '</td></tr>').join('') +
      '</tbody>' + (last ? '<tfoot>' + (withVat ? '<tr class="vat"><td></td><td>В том числе НДС ' + esc(vat) + '</td><td></td><td></td><td class="n">' + nf(Math.round(vatSum)) + '</td></tr>' : '') + '<tr><td></td><td>Итого ' + esc(vl) + '</td><td></td><td class="n">' + (ang ? nf(Math.round(r.total / g.L / g.W)) + ' за м²' : '') + '</td><td class="n">' + nf(Math.round(r.total)) + '</td></tr></tfoot>' : '') +
      '</table>' + (last && r.notes.length ? '<p class="d-note">' + r.notes.map(esc).join(' ') + '</p>' : ''));
  }

  // Состав предложения
  const low = t => /^[А-ЯЁ][а-яё]/.test(t) ? t[0].toLowerCase() + t.slice(1) : t;
  const inc = gr.map(x => x.name + ': ' + x.rows.map(i => low(i[0].replace(/\s*\(.*?\)\s*/g, ' ').replace(new RegExp('^' + x.name + ':\\s*', 'i'), '').trim())).slice(0, 4).join(', '));
  S.push(head('Состав предложения') + '<div class="d-two"><div><h3>Входит в стоимость</h3><ul>' + inc.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div>' +
    '<div><h3>Не входит</h3><ul>' + r.excluded.concat(['разрешение на строительство, экспертиза, ввод в эксплуатацию — по отдельному договору']).map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div></div>');

  // Полный цикл
  const st = ['Анализ и ТЗ', 'Эскиз и бюджет', 'Рабочий проект, экспертиза', 'Разрешительная документация', 'Фиксированная смета и график', 'Строительство и надзор', 'Подключение к сетям', 'Ввод в эксплуатацию', 'Гарантия'];
  const qc = [['Нулевой цикл', 'геодезическая разбивка, грунты и основание, бетонные работы'], ['Несущий каркас и ограждения', 'монтаж, узлы, антикор; опалубка, армирование; примыкания и плоскостность'],
    ['Инженерные системы и тепловой контур', 'герметичность и изоляция, узлы примыканий и проходки, инженерные вводы'], ['Фасад, кровля и безопасность', 'кровельный пирог и водосток, крепления и стыки фасада, противопожарные конструкции'],
    ['Финиш и подготовка к эксплуатации', 'исполнительная документация, комплексное опробование систем']];
  S.push(head('Полный цикл', 'генподряда') + '<div class="d-cycle"><ol>' + st.map((x, i) => '<li class="' + (i % 2 ? '' : 'a') + '"><b>' + String(i + 1).padStart(2, '0') + '</b>' + esc(x) + '</li>').join('') + '</ol>' +
    '<div class="d-qc"><h3>КОНТРОЛЬ КАЧЕСТВА НА КАЖДОМ ЭТАПЕ</h3>' + qc.map(q => '<div><i>✓</i><b>' + esc(q[0]) + '</b><span>' + esc(q[1]) + '</span></div>').join('') + '</div></div>');

  // Объекты
  const ob = [['bc-fasad', 'Бизнес-центр', 'г. Москва, ул. Новопетровская, д. 1, стр. 1', '1 720 м² · февраль 2025 — апрель 2026'],
    ['inkub-1', 'Бизнес-инкубатор, 3 корпуса', 'г. Санкт-Петербург, ул. Евграфова, д. 27', 'декабрь 2024 — декабрь 2026'],
    ['hram-1', 'Строительство храма', 'г. Санкт-Петербург', 'башенный кран TGM RGT 13-40 · 2022–2026'],
    ['bc-karkas', 'Бизнес-центр: каркас и фасад', 'г. Москва, ул. Новопетровская', 'металлокаркас, сэндвич-панели']];
  S.push(head('Действующие', 'объекты') + '<div class="d-objs">' + ob.map((o, i) => '<div class="o' + i + '"><img src="' + A + o[0] + '-s.jpg" alt=""><p><b>' + esc(o[1]) + '</b><span>' + esc(o[2]) + '</span><em>' + esc(o[3]) + '</em></p></div>').join('') +
    '<div class="o4"><b>200+</b><span>завершённых объектов: склады, ангары, производственные здания, автосервисы, ФОКи</span></div></div>');

  // Почему мы
  S.push(head('Не теряете деньги на чужих ошибках:', 'риски снимаем на этапе ТЗ') + '<p class="d-p">Для собственников и инвесторов, которым нужен предсказуемый объект — по срокам, бюджету и качеству. Ваша задача — получать доход от объекта, а не управлять строительными рисками.</p>' +
    '<div class="d-why"><div class="dark"><b>Прозрачная смета</b><span>Полный контроль над бюджетом и никакого стресса от внезапных счетов.</span></div><div><b>Инженерная проработка</b><span>Проработка ТЗ и узлов до монтажа: риски снимаем на этапе ТЗ.</span></div>' +
    '<div class="gold"><b>Управление сроками</b><span>Календарный план, контрольные точки, отчётность.</span></div><div><b>Генподряд под ключ</b><span>Один контур ответственности — от проекта до ввода и гарантии.</span></div></div>' +
    '<div class="d-why2"><img src="' + A + 'bc-zal-s.jpg" alt=""><img src="' + A + 'inkub-4-s.jpg" alt=""><div><b>15+ лет</b><span>строим коммерческую недвижимость под ключ с 2011 года</span></div></div>');

  // Финал
  S.push(head('Строим так, чтобы ваш бизнес', 'начал зарабатывать раньше') + '<div class="d-final"><div class="d-cond"><h3>УСЛОВИЯ</h3><ul>' +
    '<li>Расчёт предварительный: сделан автоматически по введённым параметрам, уточняется после ТЗ, геологии и чертежей КМД.</li>' +
    (withVat ? '<li>Все цены с НДС ' + esc(vat) + ': итог <b>' + rub(r.total) + '</b>, в том числе НДС ' + rub(vatSum) + '.</li>' : '<li>Все цены без НДС: итог <b>' + rub(r.total) + '</b>.</li>') +
    (r.days ? '<li>Монтаж каркаса, стен и кровли — около ' + nf(r.days) + ' дней; полы и отделка — по графику после договора.</li>' : '') +
    '<li>КП № ' + esc(no) + ' действует до ' + ds(until) + '. Оплату и сроки согласуем в договоре.</li></ul></div>' +
    '<div class="d-cards"><div class="dark"><b>РСК «ПОКОЛЕНИЯ»</b><span>Строительная компания</span><em>' + esc(C.phone) + '</em><em>' + esc(C.email) + '</em></div>' +
    '<div class="gold">Отправьте вводные — подготовим расчёт, проконсультируем и предложим оптимальное решение.</div></div>' +
    '<div class="d-qr"><img src="' + A + 'qr-telegram.svg" alt="QR Telegram"><b>Telegram-канал</b><span>@spbpokoleniya</span><small>стройка изнутри, цены и объекты</small></div></div>' +
    '<div class="d-band"><img src="' + A + 'kaska-s.jpg" alt=""><div><b>ОДИН ПОДРЯДЧИК НА ВЕСЬ ЦИКЛ</b><span>меньше рисков, быстрее запуск, предсказуемый результат</span></div></div>');

  const foot = 'РСК ПОКОЛЕНИЯ · ПРЕДВАРИТЕЛЬНОЕ КП № ' + esc(no) + ' · ' + esc(title.toUpperCase());
  const fixSvg = h => h.replace(/<svg viewBox="([-\d. ]+)"/g, (m, vb) => { const q = vb.trim().split(/\s+/); return m + ' style="aspect-ratio:' + q[2] + '/' + q[3] + '"'; });
  return S.map(fixSvg).map((s, i) => '<section class="slide' + (i === 0 ? ' first' : '') + '">' + s + (i ? '<footer class="d-foot"><span>' + foot + '</span><span>' + (i + 1) + ' / ' + S.length + '</span></footer>' : '') + '</section>').join('');
}
window.renderDeck = renderDeck;
})();
