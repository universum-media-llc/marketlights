"""Extra pages for MarketLights: unit converter, About, Contact, Privacy, Terms, 404.

They reuse the exact <style> block of template.html so every page has the same look.
Called from build.py after the main page is written:  pages.write_all(HERE, data)
"""
import json, os, re

COMPANY = "Universum Media LLC"
ADDRESS = "30 N Gould St, STE R, Sheridan, WY 82801, USA"
EMAIL = "contact@marketlights.net"
UPDATED = "26 November 2026"

TOOL_LINKS = [("/gold-price-per-gram/", "Gold Price per Gram")]
NAV = [("/", "Market Lights"), ("/convert/", "Unit Converter"), ("#calculator", "Calculator"), ("/about/", "About"), ("/contact/", "Contact")]

EXTRA_CSS = """
.topnav{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.topnav a{font:800 13px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);text-decoration:none;padding:8px 14px;border:2px solid var(--line);border-radius:10px;background:var(--panel)}
.topnav a:hover{border-color:var(--amb)}
.topnav a.on{border-color:var(--amb);color:var(--amb)}
.top{align-items:center!important}
.prose{max-width:820px}
.prose h1{font-size:clamp(30px,4vw,44px);margin:0 0 6px}
.prose h2{font:700 24px "Barlow Semi Condensed",Inter,sans-serif;margin:0 0 8px;text-transform:uppercase;letter-spacing:.02em}
.prose p,.prose li{font-size:16px;line-height:1.65}
.prose a{color:var(--amb)}
.stack{display:grid;gap:22px;margin-top:22px}
.flinks{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 12px}
.flinks a{color:var(--ink);font-weight:700;text-decoration:none;font-size:14px}
.flinks a:hover{color:var(--amb)}
/* converter */
.convgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;margin-top:22px}
@media(max-width:860px){.convgrid{grid-template-columns:minmax(0,1fr)}}
.cv{border:3px solid var(--cc);border-radius:18px;background:color-mix(in srgb,var(--cc) 4%,var(--bg));padding:clamp(16px,2.4vw,26px);display:grid;gap:16px;align-content:start}
.cv.wide{grid-column:1/-1}
.cv .chead h2{font-size:clamp(22px,2.4vw,30px)}
.cvin{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.cvin input,.cvin select{font:700 18px Inter,sans-serif;background:var(--bg);color:var(--ink);border:2px solid var(--line);border-radius:10px;padding:10px 12px}
.cvin input{width:170px}
.cvin input:focus,.cvin select:focus{outline:none;border-color:var(--cc)}
.res{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.res div{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:10px 12px}
.res b{display:block;font:700 22px "Barlow Semi Condensed",Inter,sans-serif;font-variant-numeric:tabular-nums;word-break:break-all}
.res span{font:800 11px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--mute)}
.res div.src{border-color:var(--cc)}
.val{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.val div{border:2px solid var(--cc,var(--c-gold));border-radius:10px;background:color-mix(in srgb,var(--cc,var(--c-gold)) 10%,var(--panel));padding:12px 14px}
.val b{display:block;font:700 26px "Barlow Semi Condensed",Inter,sans-serif;color:var(--cc,var(--c-gold))}
.val span{font:800 11px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--mute)}
.note2{font-size:13px;color:var(--mute);margin:0}
.cdisp{border:2px solid var(--cc);border-radius:12px;background:var(--bg);padding:10px 14px;text-align:right;min-height:84px;display:grid;align-content:end}
.cexpr{font:600 15px Inter,sans-serif;color:var(--mute);min-height:20px;word-break:break-all}
.cout{display:block;font:700 38px/1.1 "Barlow Semi Condensed",Inter,sans-serif;color:var(--ink);word-break:break-all}
.ckeys{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.ckeys button{font:700 22px Inter,sans-serif;padding:14px 0;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}
.ckeys button:hover{border-color:var(--cc)}
.ckeys .cfn{color:var(--mute)}.ckeys .cop{color:var(--cc);background:color-mix(in srgb,var(--cc) 12%,var(--panel))}
.ckeys .ceq{background:var(--cc);color:#0b1020;border-color:var(--cc)}
.res div{cursor:copy}
.r3g{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:end}
.r3g span{font-weight:800;font-size:20px;padding-bottom:10px;color:var(--amb)}
.r3g label{display:grid;gap:4px;font:800 12px Inter,sans-serif;letter-spacing:.06em;color:var(--mute)}
.r3g input,.pl input{font:700 18px Inter,sans-serif;background:var(--bg);color:var(--ink);border:2px solid var(--line);border-radius:10px;padding:10px 12px;width:100%}
.r3g output{display:block;font:700 24px "Barlow Semi Condensed",Inter,sans-serif;border:2px solid var(--amb);border-radius:10px;padding:7px 12px;background:color-mix(in srgb,var(--amb) 10%,var(--panel));color:var(--amb)}
.pl{display:grid;grid-template-columns:auto 90px auto 90px auto minmax(80px,1fr);gap:8px;align-items:center;padding:10px 0;border-top:1px solid var(--line);font-size:14px;font-weight:600}
.pl:first-of-type{border-top:0}
.pl b{font:700 22px "Barlow Semi Condensed",Inter,sans-serif;color:var(--c-crypto);text-align:right}
@media(max-width:600px){.pl{grid-template-columns:auto 1fr auto 1fr}.pl b{grid-column:1/-1;text-align:left}.pl span:nth-of-type(3){display:none}}
"""

CALC_WIDGET = """
<style>
.fcalc-btn{position:fixed;right:20px;bottom:20px;z-index:60;display:inline-flex;align-items:center;gap:10px;font:800 15px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#0b1020;background:#8fb3ff;border:0;border-radius:999px;padding:13px 20px 13px 16px;box-shadow:0 8px 24px rgba(0,0,0,.45),0 0 0 3px rgba(143,179,255,.25);cursor:pointer}
.fcalc-btn svg{width:22px;height:22px}
.fcalc-btn:hover{transform:translateY(-1px)}
.fcalc{position:fixed;right:20px;bottom:84px;z-index:61;width:min(340px,calc(100vw - 24px));border:3px solid #8fb3ff;border-radius:18px;background:#15181c;padding:14px;display:grid;gap:10px;box-shadow:0 18px 50px rgba(0,0,0,.6)}
.fcalc[hidden]{display:none}
.fcalc header{display:flex;align-items:center;justify-content:space-between;cursor:move;user-select:none}
.fcalc header b{font:700 22px "Barlow Semi Condensed",Inter,sans-serif;color:#8fb3ff;text-transform:uppercase;letter-spacing:.02em}
.fcalc header button{background:none;border:1px solid #2a2e33;color:#eef0f2;border-radius:8px;font:700 14px Inter,sans-serif;padding:5px 10px;cursor:pointer}
.fcalc .fdisp{border:2px solid #8fb3ff;border-radius:12px;background:#0f1113;padding:8px 12px;text-align:right;min-height:76px;display:grid;align-content:end}
.fcalc .fexpr{font:600 14px Inter,sans-serif;color:#a3a9b0;min-height:18px;word-break:break-all}
.fcalc .fout{font:700 34px/1.1 "Barlow Semi Condensed",Inter,sans-serif;color:#eef0f2;word-break:break-all}
.fcalc .fkeys{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
.fcalc .fkeys button{font:700 20px Inter,sans-serif;padding:12px 0;border-radius:10px;border:1px solid #2a2e33;background:#1a1d20;color:#eef0f2;cursor:pointer}
.fcalc .fkeys button:hover{border-color:#8fb3ff}
.fcalc .fkeys .fn{color:#a3a9b0}.fcalc .fkeys .op{color:#8fb3ff;background:#1e2533}
.fcalc .fkeys .eq{background:#8fb3ff;color:#0b1020;border-color:#8fb3ff}
.fcalc .fhint{font-size:12px;color:#a3a9b0;margin:0}
@media(max-width:600px){.fcalc{right:12px;left:12px;width:auto;bottom:78px}.fcalc-btn{right:12px;bottom:12px;padding:12px 16px 12px 14px;font-size:14px}}
.res div,.val div,.tile .v,.lv b,.kr b{cursor:copy}
</style>
<button type="button" class="fcalc-btn" id="fcalcBtn" aria-controls="fcalc" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="4" y="2.5" width="16" height="19" rx="3"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/></svg>Calculator</button>
<section class="fcalc" id="fcalc" hidden aria-label="Calculator">
  <header id="fcalcHead"><b>Calculator</b><button type="button" id="fcalcX" aria-label="Close calculator">✕</button></header>
  <div class="fdisp"><div class="fexpr" id="fexpr">&nbsp;</div><output class="fout" id="fout">0</output></div>
  <div class="fkeys" id="fkeys">
    <button data-k="C" class="fn">C</button><button data-k="B" class="fn" aria-label="Delete">⌫</button><button data-k="%" class="fn">%</button><button data-k="/" class="op">÷</button>
    <button data-k="7">7</button><button data-k="8">8</button><button data-k="9">9</button><button data-k="*" class="op">×</button>
    <button data-k="4">4</button><button data-k="5">5</button><button data-k="6">6</button><button data-k="-" class="op">−</button>
    <button data-k="1">1</button><button data-k="2">2</button><button data-k="3">3</button><button data-k="+" class="op">+</button>
    <button data-k="N" class="fn">±</button><button data-k="0">0</button><button data-k=".">.</button><button data-k="=" class="eq">=</button>
  </div>
  <p class="fhint">Tap any number on the page to bring it in. Keyboard works too: Enter = equals, Esc = clear.</p>
</section>
<script>
{
  const btn = document.getElementById('fcalcBtn'), box = document.getElementById('fcalc'), out = document.getElementById('fout'), exl = document.getElementById('fexpr');
  let ex = '', last = '';
  const open = (v) => { box.hidden = false; btn.setAttribute('aria-expanded', 'true'); if (v != null) { ex = v; exl.innerHTML = '&nbsp;'; show(); } };
  const close = () => { box.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
  btn.addEventListener('click', () => box.hidden ? open() : close());
  document.getElementById('fcalcX').addEventListener('click', close);
  document.querySelectorAll('[data-opencalc]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); open(); }));
  const show = () => { out.textContent = ex === '' ? (last || '0') : ex.replace(/\\*/g, '×').replace(/\\//g, '÷').replace(/-/g, '−'); };
  const calc = (s) => {
    const t = s.match(/\\d*\\.?\\d+(?:e[+-]?\\d+)?|[-+*/%()]/g) || []; let i = 0;
    const peek = () => t[i], take = () => t[i++];
    const prim = () => { const x = take(); if (x === '-') return -prim(); if (x === '+') return prim(); let v; if (x === '(') { v = add(); take(); } else v = parseFloat(x); if (peek() === '%') { take(); v /= 100; } return v; };
    const mul = () => { let v = prim(); while (peek() === '*' || peek() === '/') { const o = take(), r = prim(); v = o === '*' ? v * r : v / r; } return v; };
    const add = () => { let v = mul(); while (peek() === '+' || peek() === '-') { const o = take(), r = mul(); v = o === '+' ? v + r : v - r; } return v; };
    const v = add(); return i === t.length ? v : NaN;
  };
  const nice = (v) => !isFinite(v) ? 'Error' : String(+v.toPrecision(12));
  const press = (k) => {
    if (k === 'C') { ex = ''; last = ''; exl.innerHTML = '&nbsp;'; }
    else if (k === 'B') ex = ex.slice(0, -1);
    else if (k === '=') { if (!ex) return; exl.textContent = ex.replace(/\\*/g, '×').replace(/\\//g, '÷') + ' ='; last = nice(calc(ex)); ex = ''; }
    else if (k === 'N') { if (ex) ex = ex.startsWith('-') ? ex.slice(1) : '-' + ex; else if (last && last !== 'Error') ex = String(-parseFloat(last)); }
    else { if (!ex && last && last !== 'Error' && /[-+*/%]/.test(k)) ex = last; if (!ex && /[*/%]/.test(k)) return; if (/[-+*/]$/.test(ex) && /[-+*/]/.test(k)) ex = ex.slice(0, -1); ex += k; }
    show();
  };
  document.getElementById('fkeys').addEventListener('click', (e) => { const b = e.target.closest('[data-k]'); if (b) press(b.dataset.k); });
  document.addEventListener('keydown', (e) => {
    if (box.hidden || e.target.closest('input,select,textarea') || e.metaKey || e.ctrlKey || e.altKey) return;
    const m = {Enter: '=', '=': '=', Escape: 'C', Backspace: 'B', x: '*', X: '*', ',': '.'}; const k = m[e.key] || e.key;
    if (/^[0-9.+\\-*/%]$/.test(k) || ['=', 'C', 'B'].includes(k)) { e.preventDefault(); press(k); }
  });
  document.addEventListener('click', (e) => {
    if (e.target.closest('#fcalc, #fcalcBtn, button, a, select, input')) return;
    const d = e.target.closest('.res div b, .val div b, .tile .v, .lv b, .kr b, .ppill, .res div, .val div'); if (!d) return;
    const b = d.matches('.res div, .val div') ? d.querySelector('b') : d; if (!b) return;
    const v = b.textContent.replace(/,/g, '').match(/-?\\d+(?:\\.\\d+)?/); if (v) open(v[0]);
  });
  // drag by the header (desktop)
  const head = document.getElementById('fcalcHead'); let dx = 0, dy = 0, drag = false;
  head.addEventListener('pointerdown', (e) => { if (e.target.closest('button') || innerWidth < 600) return; drag = true; const r = box.getBoundingClientRect(); dx = e.clientX - r.left; dy = e.clientY - r.top; head.setPointerCapture(e.pointerId); });
  head.addEventListener('pointermove', (e) => { if (!drag) return; box.style.left = Math.max(4, Math.min(innerWidth - box.offsetWidth - 4, e.clientX - dx)) + 'px'; box.style.top = Math.max(4, Math.min(innerHeight - 60, e.clientY - dy)) + 'px'; box.style.right = 'auto'; box.style.bottom = 'auto'; });
  head.addEventListener('pointerup', () => { drag = false; });
}
</script>
"""


def slot(name, kind, size):
    return '<div class="adwrap"><p class="adlbl">Advertisement</p><div class="adslot {kind}" data-ad="{name}" data-size="{size}"></div></div>'.format(name=name, kind=kind, size=size)


def shell(tpl, title, desc, path, body, script="", data=None):
    style = re.search(r"<style>.*?</style>", tpl, re.S).group(0).replace("</style>", EXTRA_CSS + "</style>")
    head = re.search(r"<head>.*?<style>", tpl, re.S).group(0)
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    head = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{desc}">', head)
    head = head.replace('href="https://marketlights.net/"', f'href="https://marketlights.net{path}"').replace(
        'content="https://marketlights.net/"', f'content="https://marketlights.net{path}"')
    head = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{title}">', head)
    head = head[: -len("<style>")]
    nav = "".join(f'<a href="{h}"{" class=\"on\"" if h == path else ""}{" data-opencalc" if h.startswith("#") else ""}>{t}</a>' for h, t in NAV)
    blob = "" if data is None else '<script id="data" type="application/json">' + json.dumps(data).replace("</", "<\\/") + "</script>"
    return f"""<!DOCTYPE html>
<html lang="en">
{head}{style}
</head>
<body>
<header class="band" style="padding-bottom:0">
  <div class="wrap">
    <div class="top">
      <a href="/" style="text-decoration:none;color:inherit"><div class="brand disp"><i><b style="background:var(--red);box-shadow:0 0 7px var(--red)"></b><b style="background:var(--amb);box-shadow:0 0 7px var(--amb)"></b><b style="background:var(--grn);box-shadow:0 0 7px var(--grn)"></b></i>MarketLights</div></a>
      <nav class="topnav" aria-label="Main">{nav}</nav>
    </div>
  </div>
</header>
<main class="band">
  <div class="wrap">
{body}
  <div style="margin-top:40px">{slot(path.strip('/').replace('/','-') + '-bottom' if path != '/' else 'bottom', 'rect', 'responsive · up to 728×280')}</div>
  </div>
</main>
{footer()}
{blob}
{script}
{CALC_WIDGET}
{tpl[tpl.index('<script>\n/* ads:'):tpl.index('</script>', tpl.index('/* ads:')) + 9]}
</body>
</html>
"""


def footer():
    links = "".join(f'<a href="{h}">{t}</a>' for h, t in [x for x in NAV if not x[0].startswith("#")] + TOOL_LINKS + [("/privacy/", "Privacy Policy"), ("/terms/", "Terms &amp; Disclaimer")])
    return f"""<footer class="band">
  <div class="wrap">
    <nav class="flinks" aria-label="Footer">{links}</nav>
    <p><strong>Information and education only, not financial advice.</strong> Nothing on this site is an instruction to buy, sell or hold. Make your own decisions and, if needed, speak to a licensed adviser.</p>
    <p>© MarketLights · {COMPANY}</p>
  </div>
</footer>"""


def box(title, inner, color="var(--line)"):
    return f'<section class="box" style="border-color:{color}"><div class="bh">{title}</div>{inner}</section>'


# ---------------------------------------------------------------- converter
CONV_BODY = """
<div class="prose" style="max-width:none">
  <h1 class="disp">Unit Converter</h1>
  <p style="margin:0;color:var(--mute)">Gold &amp; silver weights, length, area, weight, volume, temperature, currency exchange, rule of three, percentages and a calculator in one place. Type a number: every result updates at once.</p>
</div>
<div class="box" style="margin-top:22px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;border-color:var(--usd)">
  <div class="bh" style="margin:0">Your Currency</div>
  <select id="cur" aria-label="Currency" style="font:700 15px Inter,sans-serif;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 10px"></select>
  <span id="goldsrc" class="note2"></span>
</div>
""" + slot("conv-top", "lead", "728×90 · phone 320×100") + """
<div class="convgrid" id="conv"></div>
""" + slot("conv-mid", "rect", "responsive · up to 728×280") + """
<div class="convgrid">
  <section class="cv wide" style="--cc:var(--usd)" id="fxbox">
    <header class="chead"><h2 class="disp" style="color:var(--usd)">Currency Exchange</h2></header>
    <div class="cvin"><input type="number" inputmode="decimal" value="100" step="any" id="fxamt" aria-label="Amount">
      <select id="fxfrom" aria-label="From currency"></select><span style="font-weight:800">→</span><select id="fxto" aria-label="To currency"></select></div>
    <div class="val" id="fxmain"></div>
    <div class="bh" style="margin:4px 0 0">In Other Currencies</div>
    <div class="res" id="fxall"></div>
    <p class="note2" id="fxnote"></p>
  </section>
  <div style="display:grid;gap:22px;align-content:start">
  <section class="cv" style="--cc:var(--amb)" id="r3">
    <header class="chead"><h2 class="disp" style="color:var(--amb)">Rule of Three</h2></header>
    <p class="note2" style="font-size:14px">If <b>A</b> gives <b>B</b>, how much does <b>C</b> give? Example: 2 kg cost $300, so 5 kg cost $750.</p>
    <div class="r3g">
      <label>A<input type="number" step="any" value="2" id="r3a"></label><span>→</span><label>B<input type="number" step="any" value="300" id="r3b"></label>
      <label>C<input type="number" step="any" value="5" id="r3c"></label><span>→</span><label>X<output id="r3x">—</output></label>
    </div>
    <div class="seg" role="group" aria-label="Proportion type" style="width:fit-content"><button type="button" class="on" data-r3="d">Direct</button><button type="button" data-r3="i">Inverse</button></div>
    <p class="note2" id="r3n"></p>
  </section>
  <section class="cv" style="--cc:var(--c-crypto)" id="pct">
    <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Percentage</h2></header>
    <div class="pl"><span>What is</span><input type="number" step="any" value="15" id="p1a"><span>% of</span><input type="number" step="any" value="200" id="p1b"><span>=</span><b id="p1x">—</b></div>
    <div class="pl"><span>Change from</span><input type="number" step="any" value="80" id="p2a"><span>to</span><input type="number" step="any" value="100" id="p2b"><span>=</span><b id="p2x">—</b></div>
    <div class="pl"><span></span><input type="number" step="any" value="30" id="p3a"><span>is what % of</span><input type="number" step="any" value="120" id="p3b"><span>=</span><b id="p3x">—</b></div>
  </section>
  </div>
</div>
"""

CONV_JS = r"""<script>
{
const D = JSON.parse(document.getElementById('data').textContent);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = (x) => { if (!isFinite(x)) return '—'; const a = Math.abs(x); const d = a === 0 ? 0 : a >= 1e6 ? 0 : a >= 1000 ? 2 : a >= 1 ? 4 : a >= 0.001 ? 6 : 10;
  return x.toLocaleString('en-US', {maximumFractionDigits: d}); };
// Units: factor to the base unit (grams, metres, square metres, litres).
const G = {
  gold: {title: 'Gold &amp; Silver Weight', cc: 'var(--c-gold)', base: 'g', wide: true, units: [
    ['ozt', 'Troy ounce', 31.1034768], ['g', 'Gram', 1], ['kg', 'Kilogram', 1000],
    ['baht', 'Thai baht (gold)', 15.244], ['tola', 'Tola (India)', 11.6638038], ['tael', 'Tael (Hong Kong)', 37.429]]},
  length: {title: 'Length', cc: '#6f9fd0', units: [
    ['m', 'Metre', 1], ['cm', 'Centimetre', 0.01], ['mm', 'Millimetre', 0.001], ['km', 'Kilometre', 1000],
    ['in', 'Inch', 0.0254], ['ft', 'Foot', 0.3048], ['yd', 'Yard', 0.9144], ['mi', 'Mile', 1609.344], ['wah', 'Thai wah', 2]]},
  area: {title: 'Area', cc: 'var(--grn)', units: [
    ['m2', 'Square metre', 1], ['ft2', 'Square foot', 0.09290304], ['in2', 'Square inch', 0.00064516], ['yd2', 'Square yard', 0.83612736],
    ['acre', 'Acre', 4046.8564224], ['ha', 'Hectare', 10000], ['km2', 'Square kilometre', 1e6],
    ['rai', 'Rai (Thai)', 1600], ['ngan', 'Ngan (Thai)', 400], ['wah2', 'Square wah (Thai)', 4]]},
  weight: {title: 'Weight', cc: 'var(--c-crypto)', units: [
    ['kg', 'Kilogram', 1000], ['g', 'Gram', 1], ['mg', 'Milligram', 0.001], ['t', 'Tonne', 1e6],
    ['lb', 'Pound', 453.59237], ['oz', 'Ounce', 28.349523125], ['st', 'Stone', 6350.29318]]},
  volume: {title: 'Volume', cc: '#a970ff', units: [
    ['l', 'Litre', 1], ['ml', 'Millilitre', 0.001], ['m3', 'Cubic metre', 1000], ['galus', 'US gallon', 3.785411784],
    ['galuk', 'UK gallon', 4.54609], ['floz', 'US fluid ounce', 0.0295735295625], ['cup', 'US cup', 0.2365882365]]},
  temp: {title: 'Temperature', cc: 'var(--red)', units: [['c', 'Celsius °C'], ['f', 'Fahrenheit °F'], ['k', 'Kelvin K']]}
};
const toC = {c: (v) => v, f: (v) => (v - 32) * 5 / 9, k: (v) => v - 273.15};
const fromC = {c: (v) => v, f: (v) => v * 9 / 5 + 32, k: (v) => v + 273.15};
const PURS = {gold: [['9999', '24K · 99.99%', 0.9999], ['965', 'Thai 96.5%', 0.965], ['916', '22K · 91.67%', 0.9167], ['750', '18K · 75%', 0.75], ['585', '14K · 58.5%', 0.585]],
  silver: [['999', 'Fine · 99.9%', 0.999], ['958', 'Britannia · 95.8%', 0.958], ['925', 'Sterling · 92.5%', 0.925], ['900', 'Coin · 90%', 0.9], ['800', '80%', 0.8]]};
let metal = 'gold'; const PUR = () => PURS[metal];
const CURS = [['USD','US dollar'],['EUR','Euro'],['GBP','British pound'],['THB','Thai baht'],['JPY','Japanese yen'],['KRW','Korean won'],['CNY','Chinese yuan'],['INR','Indian rupee'],['RUB','Russian ruble'],['BRL','Brazilian real'],['MXN','Mexican peso'],['CAD','Canadian dollar'],['AUD','Australian dollar'],['CHF','Swiss franc'],['SGD','Singapore dollar']];
const rates = Object.assign({USD: 1}, D.fx || {});
let cur = 'USD'; try { cur = localStorage.getItem('ml_cur') || 'USD'; } catch (e) {}
let goldOz = D.gold_close, goldSrc = 'daily close ' + D.gold_date, silverOz = null, silverSrc = 'loading…';
const money = (usd) => { const c = rates[cur] ? cur : 'USD', x = usd * (rates[c] || 1);
  try { return new Intl.NumberFormat('en-US', {style: 'currency', currency: c, currencyDisplay: 'narrowSymbol', maximumFractionDigits: x >= 100 ? 0 : 2}).format(x); } catch (e) { return c + ' ' + x.toFixed(2); } };

document.getElementById('conv').innerHTML = Object.entries(G).map(([k, g]) => `
  <section class="cv${g.wide ? ' wide' : ''}" style="--cc:${g.cc}" id="cv-${k}">
    <header class="chead"><h2 class="disp" style="color:var(--cc)">${g.title}</h2></header>
    <div class="cvin"><input type="number" inputmode="decimal" value="1" step="any" aria-label="${g.title} amount" data-k="${k}">
      <select aria-label="${g.title} unit" data-k="${k}">${g.units.map((u) => `<option value="${u[0]}">${u[1]}</option>`).join('')}</select>
      ${k === 'gold' ? `<select aria-label="Purity" id="pur">${PUR().map((p) => `<option value="${p[0]}">${p[1]}</option>`).join('')}</select><span class="seg" role="group" aria-label="Metal"><button type="button" class="on" data-metal="gold">Gold</button><button type="button" data-metal="silver">Silver</button></span>` : ''}</div>
    <div class="res" id="res-${k}"></div>
    ${k === 'gold' ? `<div class="bh" style="margin:6px 0 0"><span id="metname">Gold</span> Value <span class="note2" style="text-transform:none;letter-spacing:0;font-weight:500">at this weight and purity</span></div><div class="val" id="val"></div>
    <p class="note2">Thai baht gold weight = 15.244 g (bullion); jewellery baht = 15.16 g. Silver uses the same weights. Precious metals are always weighed in troy ounces (31.10 g), never the regular ounce (28.35 g). Value is for the pure-metal content only, before shop premiums, making charges and taxes. Information only, not an offer to buy or sell.</p>` : ''}
  </section>`).join('');

function update(k) {
  const g = G[k], box = document.getElementById('cv-' + k), v = parseFloat(box.querySelector('input').value), u = box.querySelector('select').value;
  let rows;
  if (k === 'temp') { const c = toC[u](v); rows = g.units.map((x) => [x, fromC[x[0]](c)]); }
  else { const base = v * g.units.find((x) => x[0] === u)[2]; rows = g.units.map((x) => [x, base / x[2]]); }
  document.getElementById('res-' + k).innerHTML = rows.map(([x, r]) => `<div class="${x[0] === u ? 'src' : ''}"><b>${isNaN(v) ? '—' : fmt(r)}</b><span>${esc(x[1])}</span></div>`).join('');
  if (k === 'gold') {
    const grams = v * g.units.find((x) => x[0] === u)[2], pur = (PUR().find((p) => p[0] === document.getElementById('pur').value) || PUR()[0])[2];
    const oz = metal === 'gold' ? goldOz : silverOz, name = metal === 'gold' ? 'Gold' : 'Silver';
    const usd = grams / 31.1034768 * oz * pur;
    document.getElementById('metname').textContent = name;
    document.getElementById('val').innerHTML = isNaN(v) || !oz ? `<div><b>—</b><span>${name} price unavailable right now</span></div>` :
      `<div><b>${money(usd)}</b><span>Value · ${esc(cur)}</span></div><div><b>${money(oz)}</b><span>${name} per troy ounce</span></div>` +
      (metal === 'gold' ? `<div><b>${money(oz / 31.1034768 * 15.244 * 0.965)}</b><span>Thai baht weight · 96.5%</span></div>` : `<div><b>${money(oz / 31.1034768 * 1000)}</b><span>Silver per kilogram · pure</span></div>`);
    document.getElementById('goldsrc').textContent = `Gold price: ${goldSrc} · Silver price: ${silverSrc}` + (cur !== 'USD' && rates[cur] ? ` · 1 USD = ${rates[cur] >= 100 ? rates[cur].toFixed(0) : rates[cur].toFixed(4)} ${cur}` : '');
  }
}
document.getElementById('conv').addEventListener('input', (e) => { const k = e.target.dataset.k || (e.target.id === 'pur' ? 'gold' : null); if (k) update(k); });
Object.keys(G).forEach(update);

const sel = document.getElementById('cur');
const fillCur = () => { sel.innerHTML = CURS.filter(([c]) => rates[c]).map(([c, n]) => `<option value="${c}"${c === cur ? ' selected' : ''}>${c} · ${n}</option>`).join(''); };
fillCur();
sel.addEventListener('change', () => { cur = sel.value; try { localStorage.setItem('ml_cur', cur); } catch (e) {} update('gold'); });
fetch('https://api.coinbase.com/v2/exchange-rates?currency=USD', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject()).then((j) => {
  CURS.forEach(([c]) => { const x = +((j.data || {}).rates || {})[c]; if (x > 0) rates[c] = x; }); fillCur(); update('gold'); }).catch(() => {});
const live = () => fetch('https://api.exchange.coinbase.com/products/PAXG-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject()).then((j) => {
  const p = +j.price; if (p > 0) { goldOz = p; goldSrc = 'LIVE ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'}) + ' (Coinbase, PAX Gold)'; update('gold'); } }).catch(() => {});
live(); setInterval(() => { if (!document.hidden) live(); }, 30000);
const silver = () => fetch('https://api.gold-api.com/price/XAG', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject()).then((j) => {
  const p = +j.price; if (p > 0) { silverOz = p; silverSrc = 'LIVE ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'}) + ' (Gold-API)'; update('gold'); } }).catch(() => { silverSrc = 'unavailable'; update('gold'); });
silver(); setInterval(() => { if (!document.hidden) silver(); }, 60000);
document.getElementById('cv-gold').addEventListener('click', (e) => {
  const b = e.target.closest('[data-metal]'); if (!b) return;
  metal = b.dataset.metal; document.querySelectorAll('[data-metal]').forEach((x) => x.classList.toggle('on', x === b));
  document.getElementById('pur').innerHTML = PUR().map((p) => `<option value="${p[0]}">${p[1]}</option>`).join('');
  document.getElementById('cv-gold').style.setProperty('--cc', metal === 'gold' ? 'var(--c-gold)' : '#c0c7d2');
  update('gold');
});

// ---- currency exchange
const fxSel = (id, def) => { const el = document.getElementById(id); el.innerHTML = CURS.filter(([c]) => rates[c]).map(([c, n]) => `<option value="${c}"${c === def ? ' selected' : ''}>${c} · ${n}</option>`).join(''); return el; };
const fmtCur = (x, c) => { try { return new Intl.NumberFormat('en-US', {style: 'currency', currency: c, currencyDisplay: 'narrowSymbol', maximumFractionDigits: Math.abs(x) >= 1000 ? 0 : 2}).format(x); } catch (e) { return c + ' ' + x.toFixed(2); } };
let fxF = 'USD', fxT = cur === 'USD' ? 'THB' : cur, fxSrc = D.fx_date ? 'Federal Reserve, ' + D.fx_date : '';
function fxUpdate() {
  const a = parseFloat(document.getElementById('fxamt').value), usd = a / rates[fxF];
  document.getElementById('fxmain').innerHTML = isNaN(a) ? '' : `<div style="border-color:var(--usd);background:color-mix(in srgb,var(--usd) 10%,var(--panel))"><b style="color:var(--usd)">${fmtCur(usd * rates[fxT], fxT)}</b><span>${esc(fmtCur(a, fxF))} in ${fxT}</span></div><div style="border-color:var(--line);background:var(--panel)"><b style="color:var(--ink)">${fmt(rates[fxT] / rates[fxF])}</b><span>1 ${fxF} = ? ${fxT}</span></div><div style="border-color:var(--line);background:var(--panel)"><b style="color:var(--ink)">${fmt(rates[fxF] / rates[fxT])}</b><span>1 ${fxT} = ? ${fxF}</span></div>`;
  document.getElementById('fxall').innerHTML = isNaN(a) ? '' : CURS.filter(([c]) => rates[c] && c !== fxF).map(([c, n]) => `<div class="${c === fxT ? 'src' : ''}"><b>${fmtCur(usd * rates[c], c)}</b><span>${n}</span></div>`).join('');
  document.getElementById('fxnote').textContent = 'Rates: ' + fxSrc + '. Mid-market rates for information only; banks and exchange shops add a margin.';
}
const fxInit = () => { fxSel('fxfrom', fxF); fxSel('fxto', fxT); fxUpdate(); };
fxInit();
document.getElementById('fxbox').addEventListener('input', (e) => { if (e.target.id === 'fxfrom') fxF = e.target.value; if (e.target.id === 'fxto') fxT = e.target.value; fxUpdate(); });
fetch('https://api.coinbase.com/v2/exchange-rates?currency=USD', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject()).then((j) => {
  CURS.forEach(([c]) => { const x = +((j.data || {}).rates || {})[c]; if (x > 0) rates[c] = x; });
  fxSrc = 'Coinbase, live ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'}); fxInit(); }).catch(() => {});

// ---- rule of three
let r3m = 'd';
function r3() {
  const [a, b, c] = ['r3a', 'r3b', 'r3c'].map((id) => parseFloat(document.getElementById(id).value));
  const x = r3m === 'd' ? b * c / a : a * b / c, ok = isFinite(x) && !isNaN(x);
  document.getElementById('r3x').textContent = ok ? fmt(x) : '—';
  document.getElementById('r3n').textContent = !ok ? 'Fill in A, B and C (A and C cannot be 0).' : r3m === 'd'
    ? `Direct: more C gives more X. X = B × C ÷ A = ${fmt(b)} × ${fmt(c)} ÷ ${fmt(a)}`
    : `Inverse: more C gives less X (e.g. more workers, fewer days). X = A × B ÷ C = ${fmt(a)} × ${fmt(b)} ÷ ${fmt(c)}`;
}
document.getElementById('r3').addEventListener('input', r3);
document.getElementById('r3').addEventListener('click', (e) => { const bt = e.target.closest('[data-r3]'); if (!bt) return; r3m = bt.dataset.r3; document.querySelectorAll('[data-r3]').forEach((x) => x.classList.toggle('on', x === bt)); r3(); });
r3();

// ---- percentage
function pc() {
  const g = (id) => parseFloat(document.getElementById(id).value);
  const x1 = g('p1a') / 100 * g('p1b'), x2 = (g('p2b') - g('p2a')) / g('p2a') * 100, x3 = g('p3a') / g('p3b') * 100;
  document.getElementById('p1x').textContent = isFinite(x1) ? fmt(x1) : '—';
  document.getElementById('p2x').textContent = isFinite(x2) ? (x2 >= 0 ? '+' : '') + fmt(x2) + '%' : '—';
  document.getElementById('p3x').textContent = isFinite(x3) ? fmt(x3) + '%' : '—';
}
document.getElementById('pct').addEventListener('input', pc); pc();
}
</script>"""


# ---------------------------------------------------------------- text pages
ABOUT = f"""
<div class="prose"><h1 class="disp">About MarketLights</h1></div>
<div class="stack prose">
{box("What It Is", '''<p>MarketLights shows the state of <b>Bitcoin</b>, <b>Ethereum</b>, <b>Gold</b> and <b>Solana</b> in one look, like a traffic light: green when the market is rising, amber for caution, red for danger. Next to each light you find the price, trend, support and resistance, RSI and the crypto fear &amp; greed mood, explained in plain words.</p>''')}
{box("How It Works", '''<p>Every day a fixed set of rules reads public price data and sets each light. The rules look at the 50-day and 200-day moving averages, the 14-day RSI, the crypto fear &amp; greed index, the average-cost line (realized price) and the strength of the US dollar. We tested the rules on past data (2018–2026 for Bitcoin and Ethereum, 2020–2026 for gold); the results are shown on each card. Solana is shown without a light because the rules did not work well for it in testing.</p>
<p>Prices update once a day after the daily close; the LIVE price refreshes every 15 seconds from Coinbase. Data sources: Coin Metrics community data, Alternative.me, the Federal Reserve Bank of St. Louis (FRED) and Coinbase.</p>''')}
{box("What It Is Not", '''<p>MarketLights is information and education only. It is not financial advice and not an instruction to buy, sell or hold anything. Past results, including our backtests, do not guarantee future results. Always make your own decisions and, if needed, speak to a licensed adviser.</p>''')}
{box("Who We Are", f'''<p>MarketLights is published by <b>{COMPANY}</b>, {ADDRESS}. Questions and suggestions are welcome on our <a href="/contact/">contact page</a>.</p>''')}
</div>"""

CONTACT = f"""
<div class="prose"><h1 class="disp">Contact</h1></div>
<div class="stack prose">
{box("Email", f'''<p>Write to us at <a href="mailto:{EMAIL}"><b>{EMAIL}</b></a>. We read every message and usually answer within a few working days.</p>''', "var(--amb)")}
{box("Company", f'''<p><b>{COMPANY}</b><br>{ADDRESS}</p>''')}
{box("Please Note", '''<p>We cannot give personal investment advice or tell you what to buy or sell. For data errors or suggestions for new tools, please include the page and the date you saw.</p>''')}
</div>"""

PRIVACY = f"""
<div class="prose"><h1 class="disp">Privacy Policy</h1><p style="color:var(--mute);margin:0">Last updated: {UPDATED}</p></div>
<div class="stack prose">
{box("Who We Are", f'''<p>This website, marketlights.net, is operated by <b>{COMPANY}</b>, {ADDRESS} ("we", "us"). Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>''')}
{box("What We Collect", '''<p>We do not ask you to sign up and we do not collect your name, email or other personal details through the site. If you email us, we use your message and address only to answer you.</p>
<p><b>Saved settings on your device.</b> Your chosen currency and time zone are stored in your browser (local storage) so they are remembered next time. They never leave your device.</p>''')}
{box("Services We Use", '''<ul>
<li><b>Cloudflare</b> hosts and protects the site. Like any web host it processes technical data such as your IP address and browser type to deliver the page and stop attacks.</li>
<li><b>Coinbase</b>: your browser asks Coinbase's public price service for the LIVE prices and exchange rates, so Coinbase receives your IP address.</li>
<li><b>Gold-API</b>: on the converter page your browser asks gold-api.com for the live silver price, so it receives your IP address.</li>
<li><b>Google Fonts</b>: the page fonts load from Google's servers, so Google receives your IP address.</li>
<li><b>Google AdSense</b> (when ads are shown): Google and its partners may use cookies to show ads based on your visits to this and other websites. You can turn off personalised ads at <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a> and learn more at <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>. Where the law requires it, you will be asked for consent first.</li>
</ul>''')}
{box("Your Rights", '''<p>Depending on where you live (for example the EU, UK or California), you may have the right to access, correct or delete personal data about you and to object to its use. Because we hold almost no personal data, most requests are simple: write to us and we will answer within 30 days.</p>''')}
{box("Children", '''<p>This site is not aimed at children under 16 and we do not knowingly collect their data.</p>''')}
{box("Changes", '''<p>If we change this policy we will update the date at the top of this page.</p>''')}
</div>"""

TERMS = f"""
<div class="prose"><h1 class="disp">Terms &amp; Disclaimer</h1><p style="color:var(--mute);margin:0">Last updated: {UPDATED}</p></div>
<div class="stack prose">
{box("Not Financial Advice", '''<p>Everything on MarketLights, including the traffic lights, levels, readings, outlooks, backtests and converter values, is general information and education. It is not financial, investment, tax or legal advice and not an offer or recommendation to buy, sell or hold any asset. Crypto and gold prices can fall sharply and you can lose money.</p>''', "var(--red)")}
{box("Accuracy", '''<p>We take data from public sources and calculate the readings automatically. Data can be late, incomplete or wrong, and the site can be unavailable. We provide the site "as is" without any guarantee.</p>''')}
{box("Your Responsibility", '''<p>You are responsible for your own decisions. To the extent the law allows, Universum Media LLC is not liable for any loss arising from use of this site.</p>''')}
{box("Use of the Site", '''<p>You may use and share the site for personal purposes. Please do not copy it in bulk or scrape it in a way that overloads it.</p>''')}
{box("Contact", f'''<p>{COMPANY}, {ADDRESS} · <a href="mailto:{EMAIL}">{EMAIL}</a></p>''')}
</div>"""

NOTFOUND = """
<div class="prose"><h1 class="disp">Page Not Found</h1></div>
<div class="stack prose">""" + box("Where To Go", '<p>This page does not exist. Go back to the <a href="/">Market Lights</a> or try the <a href="/convert/">Unit Converter</a>.</p>', "var(--amb)") + "</div>"


def write_all(here, data):
    tpl = open(os.path.join(here, "template.html")).read()
    dist = os.path.join(here, "dist")
    gold = next(a for a in data["assets"] if a["tick"] == "PAXG")
    conv_data = {"fx": data.get("fx", {}), "fx_date": data.get("fx_date", ""), "gold_close": gold["price"], "gold_date": gold["date"]}
    pages = {
        "convert": ("Unit Converter & Calculators · Gold Baht, Troy Ounce, Currency, Rule of Three · MarketLights",
                    "Free tools: gold and silver weights (troy ounce, gram, Thai baht, tola, tael) with live gold value, currency exchange, rule of three, percentage, plus length, area (rai, ngan, square wah), weight, volume and temperature.",
                    CONV_BODY, CONV_JS, conv_data),
        "about": ("About · MarketLights", "What MarketLights is, how the daily traffic lights work and who publishes it.", ABOUT, "", None),
        "contact": ("Contact · MarketLights", "How to contact MarketLights and Universum Media LLC.", CONTACT, "", None),
        "privacy": ("Privacy Policy · MarketLights", "How MarketLights handles data, cookies and third-party services.", PRIVACY, "", None),
        "terms": ("Terms & Disclaimer · MarketLights", "Terms of use and financial disclaimer for MarketLights.", TERMS, "", None),
    }
    import tools
    pages.update(tools.all_pages(conv_data, slot))
    for slug, (title, desc, body, js, d) in pages.items():
        os.makedirs(os.path.join(dist, slug), exist_ok=True)
        open(os.path.join(dist, slug, "index.html"), "w").write(shell(tpl, title, desc, f"/{slug}/", body, js, d))
    open(os.path.join(dist, "404.html"), "w").write(shell(tpl, "Page Not Found · MarketLights", "Page not found.", "/404", NOTFOUND))
    return ["/"] + [f"/{s}/" for s in pages]
