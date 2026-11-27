"""Single-purpose tool pages (one search question per page). Called from pages.write_all."""
import json

# Currencies: major gold-buying countries first. Live rates come from Coinbase in the browser;
# the daily FRED rates in the data blob are the fallback.
CURS = [
    ("USD", "US dollar"), ("EUR", "Euro"), ("GBP", "British pound"), ("INR", "Indian rupee"), ("AED", "UAE dirham"),
    ("SAR", "Saudi riyal"), ("PKR", "Pakistani rupee"), ("TRY", "Turkish lira"), ("CNY", "Chinese yuan"),
    ("HKD", "Hong Kong dollar"), ("JPY", "Japanese yen"), ("KRW", "Korean won"), ("SGD", "Singapore dollar"),
    ("MYR", "Malaysian ringgit"), ("IDR", "Indonesian rupiah"), ("PHP", "Philippine peso"), ("VND", "Vietnamese dong"),
    ("THB", "Thai baht"), ("AUD", "Australian dollar"), ("CAD", "Canadian dollar"), ("CHF", "Swiss franc"),
    ("MXN", "Mexican peso"), ("BRL", "Brazilian real"), ("ZAR", "South African rand"), ("NGN", "Nigerian naira"),
    ("EGP", "Egyptian pound"), ("KWD", "Kuwaiti dinar"), ("QAR", "Qatari riyal"), ("BDT", "Bangladeshi taka"),
]

TOOL_CSS = """
<style>
.thero{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px}
.thero .big{grid-column:1/-1;border:3px solid var(--c-gold);border-radius:16px;padding:18px 20px;background:color-mix(in srgb,var(--c-gold) 10%,var(--panel));display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px}
.thero .big b{font:700 clamp(40px,6vw,64px)/1 "Barlow Semi Condensed",Inter,sans-serif;color:var(--c-gold)}
.thero .big span{font:800 15px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase}
.thero .big em{font-style:normal;font-size:14px;color:var(--mute);flex-basis:100%}
.ttable{width:100%;border-collapse:separate;border-spacing:0;border:2px solid var(--cc);border-radius:14px;overflow:hidden}
.ttable th,.ttable td{padding:12px 14px;text-align:right;border-top:1px solid var(--line);font-variant-numeric:tabular-nums}
.ttable th:first-child,.ttable td:first-child{text-align:left}
.ttable thead th{border-top:0;background:color-mix(in srgb,var(--cc) 14%,var(--panel));font:800 13px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase}
.ttable td{font:700 19px "Barlow Semi Condensed",Inter,sans-serif}
.ttable td:first-child{font:800 15px Inter,sans-serif}
.ttable tr:nth-child(even) td{background:color-mix(in srgb,var(--panel) 60%,transparent)}
.twrap{overflow-x:auto}
.ttable th,.ttable td{white-space:nowrap}
@media(max-width:600px){.ttable th,.ttable td{padding:9px 7px}.ttable td{font-size:15.5px}.ttable td:first-child{font-size:13.5px}.ttable thead th{font-size:12px;letter-spacing:.02em}}
.swipe{display:none;font:800 12.5px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--amb);margin:0 0 6px}
.twrap.more+.swipe,.swipe.on{display:block}
.faq details{border:2px solid var(--gl);border-radius:12px;background:var(--panel);padding:14px 16px;margin-top:10px}
.faq summary{font:700 18px Inter,sans-serif;cursor:pointer}
.faq details[open]{border-color:var(--amb)}
.faq p{margin:10px 0 0;line-height:1.65}
.rel{display:flex;flex-wrap:wrap;gap:10px}
.rel a{font:800 14px Inter,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--ink);text-decoration:none;border:2px solid var(--gl);border-radius:10px;padding:10px 14px;background:var(--panel)}
.rel a:hover{border-color:var(--amb);color:var(--amb)}
.srcline{font-size:14px;color:var(--mute);margin:0}
.srcline b{color:var(--ink)}
@media(max-width:600px){#quick{display:grid;grid-template-columns:1fr 1fr;gap:8px}#quick a{font-size:12px;padding:9px 8px;text-align:center}}
.zg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr));gap:12px}
.zg label{display:grid;gap:6px;font:800 12.5px Inter,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--mute)}
.zg input,.zg select{font:700 18px Inter,sans-serif;background:var(--bg);color:var(--ink);border:2px solid var(--gl);border-radius:10px;padding:10px 12px;width:100%;box-sizing:border-box}
.zg input:focus,.zg select:focus{outline:none;border-color:var(--cc)}
.cv .val{grid-template-columns:repeat(auto-fill,minmax(min(100%,190px),1fr))}
@media(max-width:600px){.cv .val{grid-template-columns:1fr 1fr}.cv .val b{font-size:20px;word-break:break-word}}
.zrow{display:grid;grid-template-columns:1fr 100px;gap:8px}
.dleg{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:8px;font:700 13px Inter,sans-serif;text-transform:uppercase;letter-spacing:.04em}
.dleg i{display:inline-block;width:22px;border-top:3px solid;vertical-align:middle;margin-right:6px}
@media(max-width:600px){.pl .q{display:none}}
@media(max-width:600px){#gunits{grid-template-columns:1fr 1fr}#gunits b{font-size:21px}}
</style>
"""

# shared browser helpers: currency select, live FX, money formatting
SHARED_JS = r"""
const D = JSON.parse(document.getElementById('data').textContent);
const CURS = D.curs;
const rates = Object.assign({USD: 1}, D.fx || {});
let cur = 'USD'; try { cur = localStorage.getItem('ml_cur') || 'USD'; } catch (e) {}
const money = (usd, dp) => { const c = rates[cur] ? cur : 'USD', x = usd * (rates[c] || 1);
  const d = dp != null ? dp : (x >= 1000 ? 0 : 2);
  try { return new Intl.NumberFormat('en-US', {style: 'currency', currency: c, currencyDisplay: 'narrowSymbol', minimumFractionDigits: d, maximumFractionDigits: d}).format(x); } catch (e) { return c + ' ' + x.toFixed(d); } };
const curSel = document.getElementById('cur');
const fillCur = () => { curSel.innerHTML = CURS.filter(([c]) => rates[c]).map(([c, n]) => `<option value="${c}"${c === cur ? ' selected' : ''}>${c} · ${n}</option>`).join(''); };
fillCur();
curSel.addEventListener('change', () => { cur = curSel.value; try { localStorage.setItem('ml_cur', cur); } catch (e) {} render(); });
fetch('https://api.coinbase.com/v2/exchange-rates?currency=USD', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject())
  .then((j) => { const r = j.data && j.data.rates; if (!r) return; CURS.forEach(([c]) => { const v = parseFloat(r[c]); if (v > 0) rates[c] = v; }); fillCur(); render(); }).catch(() => {});
const tnow = () => new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'});
"""

CUR_BOX = """<div class="box" style="margin-top:22px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;border-color:var(--usd)">
  <div class="bh" style="margin:0">Your Currency</div>
  <select id="cur" aria-label="Currency" style="font:700 16px Inter,sans-serif;background:var(--bg);color:var(--ink);border:2px solid var(--gl);border-radius:8px;padding:8px 10px"></select>
  <p class="srcline" id="src"></p>
</div>"""


def faq_html(items):
    det = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return (f'<section class="prose faq" style="max-width:none;margin-top:34px"><h2 class="disp">Questions &amp; Answers</h2>{det}</section>'
            f'<script type="application/ld+json">{json.dumps(ld)}</script>')


def related(links):
    return ('<section style="margin-top:34px"><h2 class="disp" style="font-size:22px;text-transform:uppercase;margin:0 0 12px">More Free Tools</h2>'
            '<div class="rel">' + "".join(f'<a href="{h}">{t}</a>' for h, t in links) + "</div></section>")


RELATED = [("/convert/", "All Unit Converters"), ("/", "Bitcoin, Ethereum &amp; Gold Lights")]

# ---------------------------------------------------------------- gold price per gram
GOLD_FAQ = [
    ("How is the gold price per gram calculated?",
     "Gold is priced worldwide per troy ounce, which is 31.1035 grams. The price per gram of pure (24 karat) gold is the troy-ounce price divided by 31.1035. For lower karats, multiply by the gold content: 22K is 91.67% gold, 18K is 75%, 14K is 58.5%."),
    ("Where does this gold price come from?",
     "The live price is PAX Gold (PAXG) on Coinbase, a token backed one-to-one by a troy ounce of London Good Delivery gold. It tracks the spot gold price closely and updates every minute. If the live feed is unavailable, the page shows the last daily close."),
    ("Why does my jeweller charge more than this?",
     "This is the spot value of the pure metal only. Shops add making charges, design premiums, dealer margins and local taxes, so retail jewellery prices are usually higher. Buy-back prices are usually a little lower."),
    ("What is the difference between 24K, 22K and 18K gold?",
     "Karat measures purity out of 24 parts. 24K is almost pure gold (99.9%). 22K is 91.67% gold and is common for jewellery in India and the Gulf. 18K is 75% gold and is harder, so it is popular for rings and watches."),
    ("What is a tola and a Thai baht of gold?",
     "A tola is a traditional unit used in India, Pakistan and the Gulf, equal to 11.6638 grams. A Thai baht of gold bullion weighs 15.244 grams. Both are shown in the table so you can compare local prices."),
]

GOLD_BODY = TOOL_CSS + """
<div class="prose" style="max-width:none">
  <h1 class="disp">Gold Price per Gram Today</h1>
  <p style="margin:0;color:var(--mute)">Live spot price of gold per gram, ounce, kilo, tola and baht in your currency, for 24K, 22K, 21K, 18K, 14K, 10K and 9K gold. Updates every minute.</p>
</div>
""" + CUR_BOX + """
<section class="cv wide" style="--cc:var(--c-gold);margin-top:22px">
  <div class="thero">
    <div class="big"><span>24K gold · 1 gram</span><b id="g24">—</b><em id="gtime"></em></div>
  </div>
  <div class="val" id="gunits"></div>
</section>
@@AD1@@
<section class="cv wide" style="--cc:var(--c-gold);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-gold)">Gold Price by Karat</h2></header>
  <div class="twrap"><table class="ttable" id="ktable"><thead><tr><th>Karat</th><th>Purity</th><th>Per gram</th><th>Per 10 grams</th><th>Per tola</th><th>Per troy ounce</th></tr></thead><tbody></tbody></table></div>
  <p class="note2">Value of the pure gold content only, before making charges, dealer premiums and taxes.</p>
</section>
<section class="cv wide" style="--cc:var(--amb);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--amb)">What Is My Gold Worth?</h2></header>
  <div class="cvin"><input type="number" inputmode="decimal" value="10" step="any" id="wq" aria-label="Weight">
    <select id="wu" aria-label="Unit"><option value="1">Grams</option><option value="31.1034768">Troy ounces</option><option value="11.6638038">Tola</option><option value="15.244">Thai baht</option><option value="1000">Kilograms</option></select>
    <select id="wk" aria-label="Karat"></select></div>
  <div class="val" id="wout" style="--cc:var(--amb)"></div>
</section>
<section class="prose" style="max-width:none;margin-top:34px">
  <h2 class="disp">How to Read the Gold Price</h2>
  <p>Gold trades around the clock as a world market, priced in US dollars per <b>troy ounce</b> (31.1035 grams). Everything on this page starts from that one number: the price per gram is the ounce price divided by 31.1035, then converted into your currency at today's exchange rate. Lower karats contain less gold, so their value is the 24K price multiplied by their purity.</p>
  <p>Use these figures as a fair reference before you buy or sell. A shop's price will include its margin and local taxes, so ask for the weight, the karat and the making charge separately and compare against the table above.</p>
</section>
@@FAQ@@@@REL@@"""

GOLD_JS = r"""<script>
{
""" + SHARED_JS + r"""
const OZ = 31.1034768;
const KARATS = [['24K', 0.999], ['22K', 0.9167], ['21K', 0.875], ['18K', 0.75], ['14K', 0.585], ['10K', 0.417], ['9K', 0.375]];
let oz = D.gold_close, src = 'Last daily close · ' + D.gold_date;
document.getElementById('wk').innerHTML = KARATS.map(([k, p]) => `<option value="${p}">${k} · ${(p * 100).toFixed(1)}%</option>`).join('');
function render() {
  const g = oz / OZ;
  document.getElementById('g24').textContent = money(g * 0.999, 2);
  document.getElementById('gtime').textContent = src;
  document.getElementById('src').innerHTML = '1 USD = <b>' + (rates[cur] || 1).toLocaleString('en-US', {maximumFractionDigits: 4}) + ' ' + (rates[cur] ? cur : 'USD') + '</b>';
  const U = [['1 troy ounce', OZ], ['10 grams', 10], ['1 tola', 11.6638038], ['1 Thai baht', 15.244], ['1 kilogram', 1000]];
  document.getElementById('gunits').innerHTML = U.map(([n, w]) => `<div><b>${money(g * w * 0.999)}</b><span>24K · ${n}</span></div>`).join('');
  document.querySelector('#ktable tbody').innerHTML = KARATS.map(([k, p]) =>
    `<tr><td>${k}</td><td>${(p * 100).toFixed(1)}%</td><td>${money(g * p, 2)}</td><td>${money(g * p * 10)}</td><td>${money(g * p * 11.6638038)}</td><td>${money(g * p * OZ)}</td></tr>`).join('');
  const w = parseFloat(document.getElementById('wq').value) * parseFloat(document.getElementById('wu').value), p = parseFloat(document.getElementById('wk').value);
  document.getElementById('wout').innerHTML = isFinite(w) ? `<div><b>${money(g * p * w)}</b><span>Gold value</span></div><div><b>${(w * p).toLocaleString('en-US', {maximumFractionDigits: 3})} g</b><span>Pure gold content</span></div>` : '';
}
['wq', 'wu', 'wk'].forEach((id) => document.getElementById(id).addEventListener('input', render));
const live = () => fetch('https://api.exchange.coinbase.com/products/PAXG-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject())
  .then((j) => { const p = +j.price; if (p > 0) { oz = p; src = 'LIVE · ' + tnow() + ' · spot gold via PAX Gold (Coinbase)'; render(); } }).catch(() => {});
render(); live(); setInterval(live, 60000);
}
</script>"""



# ---------------------------------------------------------------- generic page builder
def page(h1, intro, tool, explain, faq, rel, cur=False, ad="mid"):
    return (TOOL_CSS + f'<div class="prose" style="max-width:none"><h1 class="disp">{h1}</h1>'
            f'<p style="margin:0;color:var(--mute)">{intro}</p></div>' + (CUR_BOX if cur else "") + tool
            + "@@AD@@" + f'<section class="prose" style="max-width:none;margin-top:34px">{explain}</section>'
            + faq_html(faq) + related(rel))


SWIPE = "\ndocument.querySelectorAll('.twrap').forEach((w) => { const h = document.createElement('p'); h.className = 'swipe'; h.textContent = 'Swipe the table sideways to see all columns →'; w.before(h); const f = () => h.classList.toggle('on', w.scrollWidth > w.clientWidth + 4); f(); addEventListener('resize', f); });\n"


def js(code, shared=False):
    return "<script>\n{\n" + SWIPE + "}\n{\n" + (SHARED_JS if shared else "const D = JSON.parse(document.getElementById('data').textContent);\n") + code + "\n}\n</script>"


NUMJS = r"""
const nf = (x, d) => !isFinite(x) ? '—' : x.toLocaleString('en-US', {maximumFractionDigits: d == null ? (Math.abs(x) >= 1000 ? 2 : Math.abs(x) >= 1 ? 4 : 6) : d});
const $ = (id) => document.getElementById(id), num = (id) => parseFloat($(id).value);
"""

# ---------------------------------------------------------------- silver
SILVER_TOOL = """
<section class="cv wide" style="--cc:#c0c7d0;margin-top:22px">
  <div class="thero"><div class="big" style="border-color:#c0c7d0;background:color-mix(in srgb,#c0c7d0 8%,var(--panel))"><span>Fine silver · 1 gram</span><b id="s1" style="color:#dfe4ea">—</b><em id="stime">Loading live price…</em></div></div>
  <div class="val" id="sunits" style="--cc:#c0c7d0"></div>
</section>
<section class="cv wide" style="--cc:#c0c7d0;margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:#dfe4ea">Silver Price by Purity</h2></header>
  <div class="twrap"><table class="ttable" id="stable"><thead><tr><th>Silver</th><th>Purity</th><th>Per gram</th><th>Per 100 grams</th><th>Per tola</th><th>Per kilogram</th></tr></thead><tbody></tbody></table></div>
  <p class="note2">Value of the pure silver content only, before making charges, dealer premiums and taxes.</p>
</section>
<section class="cv wide" style="--cc:var(--amb);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--amb)">What Is My Silver Worth?</h2></header>
  <div class="cvin"><input type="number" inputmode="decimal" value="100" step="any" id="wq" aria-label="Weight">
    <select id="wu" aria-label="Unit"><option value="1">Grams</option><option value="31.1034768">Troy ounces</option><option value="11.6638038">Tola</option><option value="1000">Kilograms</option></select>
    <select id="wk" aria-label="Purity"></select></div>
  <div class="val" id="wout" style="--cc:var(--amb)"></div>
</section>"""
SILVER_JS = r"""
const OZ = 31.1034768, P = [['Fine silver', 0.999], ['Britannia', 0.958], ['Sterling', 0.925], ['Coin silver', 0.9], ['800 silver', 0.8]];
let oz = D.silver_close || null, src = D.silver_close ? 'Price at last update (twice a day) · live price loading…' : 'Loading live price…';
$('wk').innerHTML = P.map(([n, p]) => `<option value="${p}">${n} · ${(p * 100).toFixed(1)}%</option>`).join('');
function render() {
  $('src').innerHTML = '1 USD = <b>' + (rates[cur] || 1).toLocaleString('en-US', {maximumFractionDigits: 4}) + ' ' + (rates[cur] ? cur : 'USD') + '</b>';
  $('stime').textContent = src; if (!oz) return;
  const g = oz / OZ;
  $('s1').textContent = money(g * 0.999, 2);
  $('sunits').innerHTML = [['1 troy ounce', OZ], ['100 grams', 100], ['1 tola', 11.6638038], ['1 kilogram', 1000]].map(([n, w]) => `<div><b>${money(g * w * 0.999)}</b><span>Fine silver · ${n}</span></div>`).join('');
  document.querySelector('#stable tbody').innerHTML = P.map(([n, p]) => `<tr><td>${n}</td><td>${(p * 100).toFixed(1)}%</td><td>${money(g * p, 2)}</td><td>${money(g * p * 100)}</td><td>${money(g * p * 11.6638038, 2)}</td><td>${money(g * p * 1000)}</td></tr>`).join('');
  const w = num('wq') * num('wu'), p = num('wk');
  $('wout').innerHTML = isFinite(w) ? `<div><b>${money(g * p * w)}</b><span>Silver value</span></div><div><b>${nf(w * p, 3)} g</b><span>Pure silver content</span></div>` : '';
}
['wq', 'wu', 'wk'].forEach((id) => $(id).addEventListener('input', render));
const live = () => fetch('https://api.gold-api.com/price/XAG', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject())
  .then((j) => { const p = +j.price; if (p > 0) { oz = p; src = 'LIVE · ' + tnow() + ' · spot silver (Gold-API)'; render(); } }).catch(() => { if (!D.silver_close) src = 'Live price unavailable right now. Please try again in a minute.'; else src = 'Price at last update (twice a day) · live feed unavailable'; render(); });
render(); live(); setInterval(live, 60000);
"""
SILVER_FAQ = [
    ("How is the silver price per gram calculated?", "Silver is priced worldwide per troy ounce (31.1035 grams). The price per gram of fine silver is the troy-ounce spot price divided by 31.1035, converted into your currency."),
    ("What is sterling silver worth per gram?", "Sterling silver is 92.5% silver, so its metal value per gram is 92.5% of the fine-silver price shown above. Jewellery and cutlery usually sell for more because of workmanship."),
    ("Why is silver cheaper per gram than gold?", "Silver is far more plentiful and much of it is used up in industry. Gold has usually traded at 60 to 90 times the price of silver per gram."),
    ("Where does this silver price come from?", "The live spot price comes from Gold-API and refreshes every minute. Shop buy and sell prices will differ because of dealer margins and taxes."),
]

# ---------------------------------------------------------------- troy ounce to grams
TROY_TOOL = """
<section class="cv wide" style="--cc:var(--c-gold);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-gold)">Troy Ounce ⇄ Grams</h2></header>
  <div class="r3g" style="grid-template-columns:1fr auto 1fr">
    <label>TROY OUNCES<input type="number" inputmode="decimal" id="oz" value="1" step="any"></label><span>⇄</span>
    <label>GRAMS<input type="number" inputmode="decimal" id="gr" value="31.1035" step="any"></label></div>
  <div class="val" id="tout"></div>
  <p class="note2">1 troy ounce = 31.1034768 grams exactly. 1 gram = 0.0321507 troy ounces.</p>
</section>
<section class="cv wide" style="--cc:var(--c-gold);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-gold)">Conversion Table</h2></header>
  <div class="twrap"><table class="ttable" id="ttab"><thead><tr><th>Troy ounces</th><th>Grams</th><th>Kilograms</th><th>Regular ounces</th><th>24K gold value</th></tr></thead><tbody></tbody></table></div>
</section>"""
TROY_JS = NUMJS + r"""
const OZ = 31.1034768; let gold = D.gold_close;
const usd = (x) => '$' + x.toLocaleString('en-US', {maximumFractionDigits: x >= 100 ? 0 : 2});
function out() { const o = num('oz'); $('tout').innerHTML = `<div><b>${nf(o * OZ)} g</b><span>Grams</span></div><div><b>${nf(o * OZ / 28.349523125)}</b><span>Regular (avoirdupois) ounces</span></div><div><b>${usd(o * gold)}</b><span>24K gold value · US dollars</span></div>`; }
$('oz').addEventListener('input', () => { $('gr').value = +(num('oz') * OZ).toFixed(4); out(); });
$('gr').addEventListener('input', () => { $('oz').value = +(num('gr') / OZ).toFixed(6); out(); });
function table() { $('ttab').querySelector('tbody').innerHTML = [0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 32.15, 50, 100, 400].map((o) =>
  `<tr><td>${o} oz t</td><td>${nf(o * OZ, 2)} g</td><td>${nf(o * OZ / 1000, 4)} kg</td><td>${nf(o * OZ / 28.349523125, 3)} oz</td><td>${usd(o * gold)}</td></tr>`).join(''); }
fetch('https://api.exchange.coinbase.com/products/PAXG-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) { gold = +j.price; out(); table(); } }).catch(() => {});
out(); table();
"""
TROY_FAQ = [
    ("How many grams are in a troy ounce?", "One troy ounce is exactly 31.1034768 grams, usually rounded to 31.1 grams."),
    ("Is a troy ounce the same as a regular ounce?", "No. A regular (avoirdupois) ounce, used for food and parcels, is 28.35 grams. A troy ounce is about 10% heavier at 31.10 grams and is used only for gold, silver, platinum and other precious metals."),
    ("How many troy ounces are in a kilogram?", "One kilogram is 32.1507 troy ounces. A standard 1 kg gold bar therefore holds just over 32 troy ounces."),
    ("Why are precious metals weighed in troy ounces?", "The troy system dates back to medieval trade fairs in Troyes, France, and became the standard for bullion in London. Every international gold and silver price is still quoted per troy ounce."),
]

# ---------------------------------------------------------------- percentage
PCT_TOOL = """
<section class="cv wide" style="--cc:var(--c-crypto);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Percentage Calculator</h2></header>
  <div class="pl"><span>What is</span><input type="number" step="any" id="a1" value="15"><span>% of</span><input type="number" step="any" id="b1" value="200"><span class="q">?</span><b id="r1"></b></div>
  <div class="pl"><input type="number" step="any" id="a2" value="30"><span>is what % of</span><input type="number" step="any" id="b2" value="120"><span class="q">?</span><b id="r2"></b></div>
  <div class="pl"><span>From</span><input type="number" step="any" id="a3" value="80"><span>to</span><input type="number" step="any" id="b3" value="100"><span>= change</span><b id="r3"></b></div>
  <div class="pl"><input type="number" step="any" id="a4" value="250"><span>±</span><input type="number" step="any" id="b4" value="10"><span>%</span><b id="r4"></b></div>
</section>"""
PCT_JS = NUMJS + r"""
function go() {
  $('r1').textContent = nf(num('a1') / 100 * num('b1'));
  $('r2').textContent = nf(num('a2') / num('b2') * 100, 4) + '%';
  const c = (num('b3') - num('a3')) / Math.abs(num('a3')) * 100; $('r3').textContent = (c > 0 ? '+' : '') + nf(c, 4) + '%';
  $('r4').textContent = nf(num('a4') * (1 + num('b4') / 100)) + ' / ' + nf(num('a4') * (1 - num('b4') / 100));
}
document.querySelectorAll('.pl input').forEach((i) => i.addEventListener('input', go)); go();
"""
PCT_FAQ = [
    ("How do I calculate a percentage of a number?", "Divide the percentage by 100 and multiply by the number. For example, 15% of 200 is 0.15 × 200 = 30."),
    ("How do I work out what percent one number is of another?", "Divide the part by the whole and multiply by 100. For example, 30 out of 120 is 30 ÷ 120 × 100 = 25%."),
    ("How do I calculate percentage increase or decrease?", "Subtract the old value from the new value, divide by the old value, and multiply by 100. From 80 to 100 is (100 − 80) ÷ 80 × 100 = +25%."),
    ("How do I add VAT or a discount?", "To add 10%, multiply by 1.10. To take off 10%, multiply by 0.90. The fourth line of the calculator does both at once."),
]

# ---------------------------------------------------------------- rule of three
R3_TOOL = """
<section class="cv wide" style="--cc:var(--amb);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--amb)">Direct Proportion</h2></header>
  <p class="note2" style="font-size:15px">More of one means more of the other. <b>If A gives B, how much does C give?</b> Example: 2 kg cost $300, so 5 kg cost $750.</p>
  <div class="r3g" style="grid-template-columns:repeat(3,minmax(0,1fr)) auto minmax(0,1.2fr)"><label>A<input type="number" step="any" id="da" value="2"></label><label>B<input type="number" step="any" id="db" value="300"></label><label>C<input type="number" step="any" id="dc" value="5"></label><span>=</span><label>RESULT<output id="dr"></output></label></div>
</section>
<section class="cv wide" style="--cc:var(--c-crypto);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Inverse Proportion</h2></header>
  <p class="note2" style="font-size:15px">More of one means less of the other. <b>If A workers need B days, how many days do C workers need?</b> Example: 4 workers take 10 days, so 8 workers take 5 days.</p>
  <div class="r3g" style="grid-template-columns:repeat(3,minmax(0,1fr)) auto minmax(0,1.2fr)"><label>A<input type="number" step="any" id="ia" value="4"></label><label>B<input type="number" step="any" id="ib" value="10"></label><label>C<input type="number" step="any" id="ic" value="8"></label><span>=</span><label>RESULT<output id="ir" style="border-color:var(--c-crypto);color:var(--c-crypto)"></output></label></div>
</section>"""
R3_JS = NUMJS + r"""
function go() { $('dr').textContent = nf(num('db') * num('dc') / num('da')); $('ir').textContent = nf(num('ia') * num('ib') / num('ic')); }
document.querySelectorAll('.r3g input').forEach((i) => i.addEventListener('input', go)); go();
"""
R3_FAQ = [
    ("What is the rule of three?", "The rule of three finds a missing fourth value when three values are known and two quantities are in proportion. It is used every day for prices, recipes, fuel, exchange rates and dosages."),
    ("What is the formula for the direct rule of three?", "If A corresponds to B, then C corresponds to B × C ÷ A. Example: 2 kg cost $300, so 5 kg cost 300 × 5 ÷ 2 = $750."),
    ("When do I use the inverse rule of three?", "Use it when one quantity goes up as the other goes down, such as workers and days, or speed and travel time. The formula is A × B ÷ C."),
    ("Is the rule of three the same as cross multiplication?", "Yes. Both set up two equal ratios, A/B = C/X, and solve for the unknown X by multiplying across."),
]

# ---------------------------------------------------------------- currency converter
FX_TOOL = """
<section class="cv wide" style="--cc:var(--usd);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--usd)">Currency Converter</h2></header>
  <div class="cvin"><input type="number" inputmode="decimal" value="100" step="any" id="amt" aria-label="Amount">
    <select id="from" aria-label="From currency"></select><button type="button" id="swap" style="font:800 20px Inter,sans-serif;background:var(--panel);color:var(--usd);border:2px solid var(--usd);border-radius:10px;padding:8px 14px;cursor:pointer" aria-label="Swap currencies">⇄</button><select id="to" aria-label="To currency"></select></div>
  <div class="thero"><div class="big" style="border-color:var(--usd);background:color-mix(in srgb,var(--usd) 10%,var(--panel))"><span id="lbl"></span><b id="res" style="color:var(--usd)">—</b><em id="rate"></em></div></div>
  <div class="bh" style="margin:4px 0 0">Same Amount in Other Currencies</div>
  <div class="res" id="all"></div>
</section>"""
FX_JS = NUMJS + r"""
const CURS = D.curs, rates = Object.assign({USD: 1}, D.fx || {}); let src = 'daily reference rates · ' + D.fx_date;
const opts = () => CURS.filter(([c]) => rates[c]).map(([c, n]) => `<option value="${c}">${c} · ${n}</option>`).join('');
let f = 'USD', t = 'EUR'; try { t = localStorage.getItem('ml_cur') || 'EUR'; if (t === 'USD') t = 'EUR'; } catch (e) {}
const fill = () => { $('from').innerHTML = opts(); $('to').innerHTML = opts(); $('from').value = f; $('to').value = t; };
const fmt = (x, c) => { try { return new Intl.NumberFormat('en-US', {style: 'currency', currency: c, currencyDisplay: 'narrowSymbol', maximumFractionDigits: x >= 1000 ? 0 : 2}).format(x); } catch (e) { return c + ' ' + nf(x, 2); } };
function go() {
  f = $('from').value; t = $('to').value; const a = num('amt'), x = a / rates[f] * rates[t];
  $('lbl').textContent = fmt(a, f) + ' ' + f + ' ='; $('res').textContent = fmt(x, t) + ' ' + t;
  $('rate').textContent = `1 ${f} = ${nf(rates[t] / rates[f], 6)} ${t} · 1 ${t} = ${nf(rates[f] / rates[t], 6)} ${f} · ${src}`;
  $('all').innerHTML = CURS.filter(([c]) => rates[c] && c !== f).map(([c, n]) => `<div><b>${fmt(a / rates[f] * rates[c], c)}</b><span>${c} · ${n}</span></div>`).join('');
}
fill();
['amt', 'from', 'to'].forEach((id) => $(id).addEventListener('input', go));
$('swap').addEventListener('click', () => { [f, t] = [t, f]; $('from').value = f; $('to').value = t; go(); });
fetch('https://api.coinbase.com/v2/exchange-rates?currency=USD', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject())
  .then((j) => { const r = j.data && j.data.rates; if (!r) return; CURS.forEach(([c]) => { const v = parseFloat(r[c]); if (v > 0) rates[c] = v; }); src = 'LIVE mid-market · ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'}); fill(); go(); }).catch(() => {});
go();
"""
FX_FAQ = [
    ("Which exchange rate does this converter use?", "It uses live mid-market rates, the midpoint between buy and sell prices on world currency markets. If the live feed is unavailable, it falls back to daily reference rates from the US Federal Reserve."),
    ("Why does my bank give me a different rate?", "Banks, cards and exchange booths add a margin to the mid-market rate and sometimes a fixed fee. Compare their rate with the one shown here to see how much you are paying."),
    ("How often are the rates updated?", "The live rate refreshes every time you open the page. Currency markets move all day on weekdays and are mostly closed at weekends."),
    ("Can I convert between any two currencies?", "Yes. Pick any two of the 29 currencies listed. The converter goes through the US dollar, which is how most currency pairs are priced."),
]

# ---------------------------------------------------------------- kg to lbs
KG_TOOL = """
<section class="cv wide" style="--cc:var(--c-crypto);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Kilograms ⇄ Pounds</h2></header>
  <div class="r3g" style="grid-template-columns:1fr auto 1fr">
    <label>KILOGRAMS (KG)<input type="number" inputmode="decimal" id="kg" value="70" step="any"></label><span>⇄</span>
    <label>POUNDS (LB)<input type="number" inputmode="decimal" id="lb" value="154.324" step="any"></label></div>
  <div class="val" id="kout" style="--cc:var(--c-crypto)"></div>
  <p class="note2">1 kg = 2.20462 lb. 1 lb = 0.453592 kg exactly.</p>
</section>
<section class="cv wide" style="--cc:var(--c-crypto);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Kg to Lbs Table</h2></header>
  <div class="twrap"><table class="ttable" id="ktab"><thead><tr><th>Kilograms</th><th>Pounds</th><th>Pounds &amp; ounces</th><th>Stone &amp; pounds</th></tr></thead><tbody></tbody></table></div>
</section>"""
KG_JS = NUMJS + r"""
const LB = 0.45359237;
const lbo = (lb) => { let p = Math.floor(lb), o = Math.round((lb - p) * 16 * 10) / 10; if (o >= 16) { p++; o = 0; } return `${p} lb ${o} oz`; };
const st = (lb) => { const s = Math.floor(lb / 14); return `${s} st ${nf(lb - s * 14, 1)} lb`; };
function out() { const k = num('kg'), l = k / LB; $('kout').innerHTML = `<div><b>${nf(l, 3)} lb</b><span>Pounds</span></div><div><b>${lbo(l)}</b><span>Pounds &amp; ounces</span></div><div><b>${st(l)}</b><span>Stone &amp; pounds</span></div><div><b>${nf(k * 1000, 0)} g</b><span>Grams</span></div>`; }
$('kg').addEventListener('input', () => { $('lb').value = +(num('kg') / LB).toFixed(4); out(); });
$('lb').addEventListener('input', () => { $('kg').value = +(num('lb') * LB).toFixed(4); out(); });
$('ktab').querySelector('tbody').innerHTML = [1, 2, 5, 10, 20, 25, 30, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100, 120, 150].map((k) => { const l = k / LB; return `<tr><td>${k} kg</td><td>${nf(l, 2)} lb</td><td>${lbo(l)}</td><td>${st(l)}</td></tr>`; }).join('');
out();
"""
KG_FAQ = [
    ("How many pounds are in a kilogram?", "One kilogram equals 2.20462 pounds. A quick mental shortcut is to double the kilograms and add 10%: 70 kg × 2 = 140, plus 14 = 154 lb."),
    ("How do I convert pounds to kilograms?", "Multiply the pounds by 0.453592, or divide by 2.20462. For example, 150 lb is 68.04 kg."),
    ("What is a stone in kilograms?", "A stone is 14 pounds, or 6.35 kilograms. It is still used for body weight in the UK and Ireland."),
    ("Is a pound the same everywhere?", "The international avoirdupois pound of 0.45359237 kg is used in the US and UK. Precious metals use the troy pound and troy ounce, which are different."),
]


# ---------------------------------------------------------------- bitcoin signal (static from today's data)
def btc_page(data):
    from html import escape as e
    a = next(x for x in data["assets"] if x["tick"] == "BTC")
    NAME = {"Falling": "Falling", "Bottoming": "Possible bottom", "Consolidating": "Sideways", "Rising": "Rising", "Overheated": "Overheated"}
    ACT = {"Falling": "Danger", "Overheated": "Danger", "Bottoming": "Caution", "Consolidating": "Caution", "Rising": "Favourable"}
    COL = {"Falling": "var(--red)", "Overheated": "var(--red)", "Bottoming": "var(--amb)", "Consolidating": "var(--amb)", "Rising": "var(--grn)"}
    LIGHT = {"Danger": "RED", "Caution": "AMBER", "Favourable": "GREEN"}
    ph = a["phase"]; act = ACT[ph]; col = COL[ph]
    m = lambda x: "$" + f"{x:,.0f}"
    sup = ", ".join(m(x) for x in a["support_d"][:2]) or "none nearby"
    res = ", ".join(m(x) for x in a["resist_d"][:2]) or "none nearby"
    day = __import__("datetime").date.fromisoformat(a["date"]).strftime("%-d %B %Y")
    rows = [("Daily close", m(a["price"])), ("Light", f"{LIGHT[act]} · {act}"), ("Phase", NAME[ph]),
            ("Trend", a["trend"]), ("RSI (14 days)", f'{a["rsi"]:.0f} · {a["rsi_word"]}'), ("50-day average", m(a["sma50"])),
            ("200-day average", m(a["sma200"])), ("Support", sup), ("Resistance", res),
            ("From record high", f'{a["from_ath"]*100:.1f}% (record {m(a["ath"])})'), ("Change over 30 days", f'{a["chg30"]*100:+.1f}%'),
            ("Market mood (fear &amp; greed)", f'{data.get("fng","—")} · {e(str(data.get("fng_word","")))}')]
    table = "".join(f"<tr><td>{k}</td><td style='text-align:right'>{v}</td></tr>" for k, v in rows)
    tool = f"""
<section class="cv wide" style="--cc:var(--c-btc);margin-top:22px">
  <div class="thero"><div class="big" style="border-color:{col};background:color-mix(in srgb,{col} 12%,var(--panel))"><span>Bitcoin · {day}</span><b style="color:{col}">{LIGHT[act]} · {e(NAME[ph]).upper()}</b><em>{e(a["sentence"])}</em></div></div>
  <div class="val" style="--cc:var(--c-btc)"><div><b id="lp">—</b><span id="lpl">Live price</span></div><div><b>{m(a["price"])}</b><span>Daily close · {day}</span></div><div><b>{a["rsi"]:.0f}</b><span>RSI · {e(a["rsi_word"])}</span></div></div>
  <div class="twrap"><table class="ttable" style="--cc:var(--c-btc)"><thead><tr><th>Today's Reading</th><th style="text-align:right">Value</th></tr></thead><tbody>{table}</tbody></table></div>
  <p class="note2">Updated automatically twice a day from the daily close. Information only, not financial advice. <a href="/" style="color:var(--amb)">See the full chart and Ethereum and Gold →</a></p>
</section>"""
    explain = f"""<h2 class="disp">What the Bitcoin Light Means</h2>
<p>MarketLights gives Bitcoin one of three lights every day, based only on price data: <b style="color:var(--grn)">GREEN</b> when the trend is rising and not overheated, <b style="color:var(--amb)">AMBER</b> when the market is moving sideways or may be forming a bottom, and <b style="color:var(--red)">RED</b> when it is falling or overheated. The light combines the trend (price against its 50-day and 200-day averages), momentum (RSI), and how far price sits from its long-run average cost.</p>
<p>In our 2018–2026 test, after "possible bottom" days Bitcoin was higher 90 days later {a.get("bt_bottom_up90",0)*100:.0f}% of the time, against {a.get("bt_all_up90",0)*100:.0f}% for all days. That is a tendency, not a promise. Past results do not guarantee future returns, and you should never invest money you cannot afford to lose.</p>"""
    tool_js = js(r"""
const live = () => fetch('https://api.exchange.coinbase.com/products/BTC-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : Promise.reject()).then((j) => {
  const p = +j.price; if (p > 0) { document.getElementById('lp').textContent = '$' + Math.round(p).toLocaleString('en-US'); document.getElementById('lpl').textContent = 'LIVE price · ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'}); } }).catch(() => {});
live(); setInterval(live, 15000);""")
    faq = [
        ("Is Bitcoin a buy today?", f"Today's MarketLights reading is {LIGHT[act]} ({NAME[ph]}). {a['sentence']} The light describes the market's condition from price data; it is not a recommendation to buy or sell."),
        ("How often is the Bitcoin signal updated?", "Twice a day, automatically, after each daily close. The live price on this page refreshes every 15 seconds."),
        ("What is RSI?", "The Relative Strength Index measures how fast price has moved over the last 14 days on a scale of 0 to 100. Below 30 is called oversold (sold hard, often near a bounce); above 70 is overbought (bought hard, often near a pullback)."),
        ("What are support and resistance?", "Support is a price level where buyers have stepped in before, so falls often pause there. Resistance is a level where sellers have appeared before, so rises often stall there."),
    ]
    return tool, explain, tool_js, faq, day


# ---------------------------------------------------------------- zakat
ZAKAT_TOOL = """
<section class="cv wide" style="--cc:var(--c-gold);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-gold)">Nisab Today</h2></header>
  <div class="seg" role="group" aria-label="Nisab basis" style="margin-left:0;justify-self:start"><button type="button" data-nb="silver" class="on">Silver nisab (595 g)</button><button type="button" data-nb="gold">Gold nisab (85 g)</button></div>
  <div class="val" id="nis"></div>
  <p class="note2" id="nsrc"></p>
</section>
<section class="cv wide" style="--cc:var(--grn);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--grn)">Your Zakatable Wealth</h2></header>
  <div class="zg">
    <label>Cash at home and in bank accounts<input type="number" inputmode="decimal" step="any" min="0" id="z_cash" value="0"></label>
    <label>Gold you own (grams)<span class="zrow"><input type="number" inputmode="decimal" step="any" min="0" id="z_gold" value="0"><select id="z_gk" aria-label="Gold karat"><option value="0.999">24K</option><option value="0.9167">22K</option><option value="0.875">21K</option><option value="0.75">18K</option><option value="0.585">14K</option></select></span></label>
    <label>Silver you own (grams)<input type="number" inputmode="decimal" step="any" min="0" id="z_silver" value="0"></label>
    <label>Shares, funds and crypto (current value)<input type="number" inputmode="decimal" step="any" min="0" id="z_inv" value="0"></label>
    <label>Business stock for sale (value)<input type="number" inputmode="decimal" step="any" min="0" id="z_biz" value="0"></label>
    <label>Money others owe you (expected back)<input type="number" inputmode="decimal" step="any" min="0" id="z_owed" value="0"></label>
    <label>Minus: debts and bills due now<input type="number" inputmode="decimal" step="any" min="0" id="z_debt" value="0"></label>
  </div>
  <div class="thero"><div class="big" id="zbig" style="border-color:var(--grn);background:color-mix(in srgb,var(--grn) 10%,var(--panel))"><span>Zakat due (2.5%)</span><b id="zdue" style="color:var(--grn)">—</b><em id="zmsg"></em></div></div>
  <div class="val" id="zsum" style="--cc:var(--grn)"></div>
</section>"""
ZAKAT_JS = NUMJS + r"""
const OZ = 31.1034768; let goldOz = D.gold_close, silverOz = D.silver_close || null, basis = 'silver';
const ids = ['z_cash', 'z_gold', 'z_gk', 'z_silver', 'z_inv', 'z_biz', 'z_owed', 'z_debt'];
try { const sv = JSON.parse(localStorage.getItem('ml_zakat') || '{}'); ids.forEach((i) => { if (sv[i] != null) $(i).value = sv[i]; }); if (sv.basis) basis = sv.basis; } catch (e) {}
const loc = (usd) => usd * (rates[cur] || 1), fromLoc = (x) => x / (rates[cur] || 1);
function render() {
  $('src').innerHTML = '1 USD = <b>' + (rates[cur] || 1).toLocaleString('en-US', {maximumFractionDigits: 4}) + ' ' + (rates[cur] ? cur : 'USD') + '</b> · enter all amounts in ' + (rates[cur] ? cur : 'USD');
  document.querySelectorAll('[data-nb]').forEach((b) => b.classList.toggle('on', b.dataset.nb === basis));
  const gG = goldOz / OZ, sG = silverOz ? silverOz / OZ : null;
  const nG = 85 * gG, nS = sG ? 595 * sG : null;
  $('nis').innerHTML = `<div><b>${money(nG)}</b><span>Gold nisab · 85 g of gold</span></div><div><b>${nS ? money(nS) : '…'}</b><span>Silver nisab · 595 g of silver</span></div><div><b>${money(gG, 2)}</b><span>Gold · per gram (24K)</span></div><div><b>${sG ? money(sG, 2) : '…'}</b><span>Silver · per gram</span></div>`;
  $('nsrc').textContent = 'Gold: ' + gsrc + ' · Silver: ' + ssrc + '. Many scholars recommend the silver nisab because it is lower, so more people pay and the poor benefit more.';
  const used = basis === 'gold' || !nS ? 'gold' : 'silver', nis = used === 'gold' ? nG : nS;  // USD
  const v = (i) => Math.max(0, num(i) || 0);
  const goldVal = fromLoc(0) + v('z_gold') * num('z_gk') * gG, silVal = sG ? v('z_silver') * 0.999 * sG : 0;
  const assets = fromLoc(v('z_cash') + v('z_inv') + v('z_biz') + v('z_owed')) + goldVal + silVal, net = assets - fromLoc(v('z_debt'));
  const due = net >= nis ? net * 0.025 : 0;
  $('zdue').textContent = money(due, 2);
  $('zmsg').textContent = net >= nis ? 'Your net wealth is above the nisab. If you have held it for one lunar year (hawl), 2.5% is due.' : `Your net wealth is below the nisab (${money(nis)}), so no zakat is due on it.`;
  $('zbig').style.borderColor = net >= nis ? 'var(--grn)' : 'var(--gl)';
  $('zsum').innerHTML = `<div><b>${money(goldVal)}</b><span>Your gold value</span></div><div><b>${money(silVal)}</b><span>Your silver value</span></div><div><b>${money(net)}</b><span>Net zakatable wealth</span></div><div><b>${money(nis)}</b><span>Nisab used (${used})</span></div>`;
  try { const sv = {basis}; ids.forEach((i) => { sv[i] = $(i).value; }); localStorage.setItem('ml_zakat', JSON.stringify(sv)); } catch (e) {}
}
let gsrc = 'daily close ' + D.gold_date, ssrc = D.silver_close ? 'price at last update' : 'loading';
ids.forEach((i) => $(i).addEventListener('input', render));
document.querySelectorAll('[data-nb]').forEach((b) => b.addEventListener('click', () => { basis = b.dataset.nb; render(); }));
fetch('https://api.exchange.coinbase.com/products/PAXG-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) { goldOz = +j.price; gsrc = 'LIVE ' + tnow(); render(); } }).catch(() => {});
fetch('https://api.gold-api.com/price/XAG', {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) { silverOz = +j.price; ssrc = 'LIVE ' + tnow(); render(); } }).catch(() => {});
render();
"""
ZAKAT_FAQ = [
    ("What is the nisab for zakat today?", "The nisab is the minimum wealth on which zakat is due. It equals the value of 85 grams of gold or 595 grams of silver. This page works out both from today's live gold and silver prices in your currency."),
    ("Should I use the gold or the silver nisab?", "Both are accepted. The silver nisab is much lower, so it includes more people, and many scholars and zakat organisations recommend it as the more cautious choice. If you are unsure, ask a scholar you trust."),
    ("How much zakat do I pay?", "Zakat is 2.5% (one-fortieth) of your net zakatable wealth, once it has stayed above the nisab for a full lunar year (hawl)."),
    ("Is zakat due on jewellery I wear?", "Scholars differ. The Hanafi school counts gold and silver jewellery; many others exempt jewellery worn regularly. Include it here if your school counts it."),
    ("What can I deduct?", "Debts and bills that are due now, such as unpaid bills or a loan instalment due, are usually deducted. Long-term debts are treated differently by different schools."),
]

# ---------------------------------------------------------------- crypto profit
PROFIT_TOOL = """
<section class="cv wide" style="--cc:var(--c-crypto);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-crypto)">Crypto Profit Calculator</h2></header>
  <div class="zg">
    <label>Coin<select id="pc_coin"><option value="BTC">Bitcoin (BTC)</option><option value="ETH">Ethereum (ETH)</option><option value="SOL">Solana (SOL)</option></select></label>
    <label>Amount invested<input type="number" inputmode="decimal" step="any" min="0" id="pc_inv" value="1000"></label>
    <label>Buy price (per coin)<input type="number" inputmode="decimal" step="any" min="0" id="pc_buy"></label>
    <label>Sell price (per coin) · live price by default<input type="number" inputmode="decimal" step="any" min="0" id="pc_sell"></label>
    <label>Buy fee %<input type="number" inputmode="decimal" step="any" min="0" id="pc_fb" value="0.5"></label>
    <label>Sell fee %<input type="number" inputmode="decimal" step="any" min="0" id="pc_fs" value="0.5"></label>
  </div>
  <div class="thero"><div class="big" id="pc_big"><span>Profit / loss</span><b id="pc_pl">—</b><em id="pc_note"></em></div></div>
  <div class="val" id="pc_out" style="--cc:var(--c-crypto)"></div>
</section>"""
PROFIT_JS = NUMJS + r"""
const PROD = {BTC: 'BTC-USD', ETH: 'ETH-USD', SOL: 'SOL-USD'}, live = {};
const loc = (usd) => usd * (rates[cur] || 1);
let touched = {buy: false, sell: false};
$('pc_buy').addEventListener('input', () => touched.buy = true); $('pc_sell').addEventListener('input', () => touched.sell = true);
const fill = () => { const c = $('pc_coin').value, p = live[c]; if (!p) return; const x = +loc(p).toPrecision(6);
  if (!touched.sell) $('pc_sell').value = x; if (!touched.buy) $('pc_buy').value = +(x * 0.8).toPrecision(6); };
function render() {
  const c3 = rates[cur] ? cur : 'USD';
  $('src').innerHTML = 'Enter all amounts in <b>' + c3 + '</b>' + (live[$('pc_coin').value] ? ' · live price ' + money(live[$('pc_coin').value]) : '');
  const inv = num('pc_inv'), buy = num('pc_buy'), sell = num('pc_sell'), fb = (num('pc_fb') || 0) / 100, fs = (num('pc_fs') || 0) / 100;
  if (!(inv > 0 && buy > 0 && sell > 0)) { $('pc_pl').textContent = '—'; $('pc_out').innerHTML = ''; return; }
  const coins = inv * (1 - fb) / buy, gross = coins * sell, net = gross * (1 - fs), pl = net - inv, roi = pl / inv * 100, be = buy / ((1 - fb) * (1 - fs));
  const f = (x) => { try { return new Intl.NumberFormat('en-US', {style: 'currency', currency: c3, currencyDisplay: 'narrowSymbol', maximumFractionDigits: Math.abs(x) >= 1000 ? 0 : 2}).format(x); } catch (e) { return c3 + ' ' + nf(x, 2); } };
  const col = pl >= 0 ? 'var(--grn)' : 'var(--red)';
  $('pc_big').style.borderColor = col; $('pc_pl').style.color = col;
  $('pc_pl').textContent = (pl >= 0 ? '+' : '') + f(pl) + '  (' + (roi >= 0 ? '+' : '') + nf(roi, 2) + '%)';
  $('pc_note').textContent = pl >= 0 ? 'After fees, this trade makes a profit.' : 'After fees, this trade makes a loss.';
  $('pc_out').innerHTML = `<div><b>${nf(coins, 8)}</b><span>${$('pc_coin').value} bought</span></div><div><b>${f(net)}</b><span>Value after selling</span></div><div><b>${f(be)}</b><span>Break-even sell price</span></div><div><b>${f(inv * fb + gross * fs)}</b><span>Total fees</span></div>`;
}
['pc_inv', 'pc_buy', 'pc_sell', 'pc_fb', 'pc_fs'].forEach((i) => $(i).addEventListener('input', render));
$('pc_coin').addEventListener('change', () => { touched = {buy: false, sell: false}; fill(); render(); });
const getLive = () => Promise.all(Object.entries(PROD).map(([c, pr]) => fetch(`https://api.exchange.coinbase.com/products/${pr}/ticker`, {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) live[c] = +j.price; }).catch(() => {}))).then(() => { fill(); render(); });
const _r = render; render = () => { fill(); _r(); };
getLive(); setInterval(getLive, 30000);
"""
PROFIT_FAQ = [
    ("How do I calculate crypto profit?", "Divide the amount invested (after the buy fee) by the buy price to get the coins you own. Multiply by the sell price, take off the sell fee, and subtract what you invested. The difference is your profit or loss."),
    ("What is the break-even price?", "It is the sell price at which you get back exactly what you invested once both fees are paid. Selling above it is a profit, below it a loss."),
    ("What fees should I enter?", "Use your exchange's trading fee, often 0.1% to 1.5% per trade. Card purchases and instant-buy buttons are usually more expensive than the exchange's own order book."),
    ("Does this include tax?", "No. Tax on crypto gains depends on your country. Use the profit figure here as the starting point for your own tax calculation."),
]

# ---------------------------------------------------------------- DCA
DCA_TOOL = """
<section class="cv wide" style="--cc:var(--c-btc);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--c-btc)">Dollar-Cost Averaging (DCA) Calculator</h2></header>
  <div class="zg">
    <label>Asset<select id="dc_coin"><option value="BTC">Bitcoin (from 2015)</option><option value="ETH">Ethereum (from 2016)</option><option value="SOL">Solana (from 2020)</option><option value="PAXG">Gold (from 2020)</option></select></label>
    <label>Amount each time (US dollars)<input type="number" inputmode="decimal" step="any" min="1" id="dc_amt" value="100"></label>
    <label>How often<select id="dc_freq"><option value="m">Every month</option><option value="2">Every two weeks</option><option value="1">Every week</option></select></label>
    <label>Start date<input type="month" id="dc_start" value="2020-01"></label>
  </div>
  <div class="thero"><div class="big" id="dc_big"><span id="dc_lbl">Value today</span><b id="dc_val">—</b><em id="dc_note"></em></div></div>
  <div class="val" id="dc_out" style="--cc:var(--c-btc)"></div>
  <div class="tile" style="padding:14px"><div class="dfig" id="dc_chart"></div>
  <div class="dleg"><span style="color:var(--c-btc)"><i style="border-color:var(--c-btc)"></i>Value of your coins</span><span><i style="border-color:#e6e6e6;border-top-style:dashed"></i>Money put in</span></div></div>
  <p class="note2">Uses weekly closing prices. Past results do not predict future returns.</p>
</section>"""
DCA_JS = NUMJS + r"""
const H = D.hist, NAMES = {BTC: 'BTC', ETH: 'ETH', SOL: 'SOL', PAXG: 'oz of gold'};
const usd = (x) => '$' + x.toLocaleString('en-US', {maximumFractionDigits: Math.abs(x) >= 1000 ? 0 : 2});
const addDays = (s, n) => { const d = new Date(s + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
let livePx = {};
function run() {
  const c = $('dc_coin').value, h = H[c]; if (!h) return;
  const amt = num('dc_amt'), fq = $('dc_freq').value, step = +fq, start = ($('dc_start').value || '2020-01') + '-01';
  const i0 = Math.max(0, h.w.findIndex((_, i) => addDays(h.start, 7 * i) >= start));
  if (i0 < 0 || !(amt > 0)) return;
  let coins = 0, put = 0; const pv = [], pp = [], dd = [];
  let lastMo = ''; for (let i = i0; i < h.w.length; i++) { const ds = addDays(h.start, 7 * i), mo = ds.slice(0, 7); if (fq === 'm' ? mo !== lastMo : (i - i0) % step === 0) { coins += amt / h.w[i]; put += amt; lastMo = mo; } pv.push(coins * h.w[i]); pp.push(put); dd.push(addDays(h.start, 7 * i)); }
  const px = livePx[c] || h.w[h.w.length - 1], val = coins * px, pl = val - put, roi = pl / put * 100;
  // lump sum on day one, same total
  const lump = put / h.w[i0] * px;
  const col = pl >= 0 ? 'var(--grn)' : 'var(--red)';
  $('dc_big').style.borderColor = col; $('dc_val').style.color = col;
  $('dc_val').textContent = usd(val);
  $('dc_note').textContent = `${usd(put)} put in since ${new Date(dd[0] + 'T00:00:00Z').toLocaleDateString('en-GB', {month: 'long', year: 'numeric', timeZone: 'UTC'})} · ${pl >= 0 ? 'profit' : 'loss'} ${pl >= 0 ? '+' : ''}${usd(pl)} (${roi >= 0 ? '+' : ''}${nf(roi, 1)}%)` + (livePx[c] ? ' · live price' : '');
  $('dc_out').innerHTML = `<div><b>${usd(put)}</b><span>Total put in</span></div><div><b>${nf(coins, 6)}</b><span>${NAMES[c]} owned</span></div><div><b>${usd(put / coins)}</b><span>Average buy price</span></div><div><b>${usd(lump)}</b><span>Same total, all on day one</span></div>`;
  // chart
  const f = $('dc_chart'), W = f.clientWidth || 800, Ht = Math.max(240, Math.min(380, Math.round(W * 0.42))), m = {l: 64, r: 12, t: 10, b: 26};
  const raw = Math.max(...pv, ...pp), mag = Math.pow(10, Math.floor(Math.log10(raw / 4))), stp = [1, 2, 2.5, 5, 10].map((k) => k * mag).find((k) => k * 4 >= raw), hi = stp * 4, X = (i) => m.l + i / Math.max(1, pv.length - 1) * (W - m.l - m.r), Y = (y) => m.t + (1 - y / hi) * (Ht - m.t - m.b);
  let g = ''; for (let k = 0; k <= 4; k++) { const y = hi * k / 4; g += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(y)}" y2="${Y(y)}" stroke="#2a2e33"/><text x="${m.l - 8}" y="${Y(y) + 4}" text-anchor="end" font-size="12" fill="#a3a9b0">${usd(y)}</text>`; }
  let ly = ''; dd.forEach((d, i) => { if (d.slice(5, 7) === '01' && (i === 0 || dd[i - 1].slice(0, 4) !== d.slice(0, 4))) ly += `<text x="${X(i)}" y="${Ht - 6}" text-anchor="middle" font-size="12" font-weight="700" fill="#a3a9b0">${d.slice(0, 4)}</text>`; });
  const path = (a) => a.map((y, i) => (i ? 'L' : 'M') + X(i).toFixed(1) + ',' + Y(y).toFixed(1)).join('');
  f.innerHTML = `<svg viewBox="0 0 ${W} ${Ht}" width="100%" height="${Ht}" role="img" aria-label="DCA value chart">${g}${ly}<path d="${path(pv)} L${X(pv.length - 1)},${Y(0)} L${X(0)},${Y(0)} Z" fill="color-mix(in srgb, var(--c-btc) 14%, transparent)"/><path d="${path(pp)}" fill="none" stroke="#e6e6e6" stroke-width="2" stroke-dasharray="7 5"/><path d="${path(pv)}" fill="none" stroke="var(--c-btc)" stroke-width="2.4"/></svg>`;
}
['dc_coin', 'dc_amt', 'dc_freq', 'dc_start'].forEach((i) => $(i).addEventListener('input', run));
addEventListener('resize', run);
const PROD = {BTC: 'BTC-USD', ETH: 'ETH-USD', SOL: 'SOL-USD', PAXG: 'PAXG-USD'};
Promise.all(Object.entries(PROD).map(([c, pr]) => fetch(`https://api.exchange.coinbase.com/products/${pr}/ticker`, {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) livePx[c] = +j.price; }).catch(() => {}))).then(run);
run();
"""
DCA_FAQ = [
    ("What is dollar-cost averaging (DCA)?", "DCA means investing the same amount at regular intervals, such as $100 every month, whatever the price. You buy more when prices are low and less when they are high, which smooths out your average buy price."),
    ("Is DCA better than investing a lump sum?", "Not always. When prices rise steadily, investing everything on day one usually wins. DCA reduces the risk of buying everything at a peak and is easier to stick with. This calculator shows both so you can compare."),
    ("Where does the price history come from?", "Weekly closing prices from Coin Metrics for Bitcoin, Ethereum and Solana, and PAX Gold for gold. Today's value uses the live price when it is available."),
    ("Does this include fees?", "No. Exchange fees on small regular purchases are often 0.5% to 1.5%, which lowers the result slightly."),
]


# ---------------------------------------------------------------- bitcoin rainbow chart
RB_NAMES = ["Fire sale", "Very cheap", "Cheap", "Below fair value", "Fair value", "Above fair value", "Expensive", "Very expensive", "Bubble"]
RB_COLS = ["#5b6cf0", "#3d9be0", "#2fb7a3", "#46c164", "#a9d23f", "#ecd43c", "#f4a43a", "#ef6b3b", "#e03b52"]
RAINBOW_TOOL = """
<section class="cv wide" style="--cc:var(--c-btc);margin-top:22px">
  <div class="thero"><div class="big" id="rb_big"><span id="rb_lbl">Bitcoin today</span><b id="rb_band">—</b><em id="rb_note"></em></div></div>
  <div class="val" id="rb_val" style="--cc:var(--c-btc)"></div>
  <div class="tile" style="padding:14px;position:relative">
    <div class="seg" role="group" aria-label="Chart range" style="margin:0 0 8px;justify-self:start"><button type="button" data-rr="all" class="on">2015 to 2030</button><button type="button" data-rr="5">Last 5 years</button></div>
    <div class="dfig" id="rb_chart" style="touch-action:pan-y"></div>
    <div id="rb_tip" class="rbtip" hidden></div>
    <div class="dleg" id="rb_leg"></div>
  </div>
  <p class="note2">Weekly closing prices since 2015 (Coin Metrics), fitted to Bitcoin's full daily history since 2014. The coloured bands after today are where the model puts each band in the future; they are not a price forecast. Information only, not financial advice.</p>
</section>
<section class="cv wide" style="--cc:var(--amb);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--amb)">Today's Band Prices</h2></header>
  <p class="note2" style="font-size:15px">The price range of each band today. The row with the arrow is where Bitcoin is now.</p>
  <div class="twrap"><table class="ttable" id="rb_table" style="--cc:var(--amb)"></table></div>
</section>
<section class="cv wide" style="--cc:#4fa3ff;margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:#4fa3ff">How It Read at Past Tops and Bottoms</h2></header>
  <div class="twrap"><table class="ttable" id="rb_hist" style="--cc:#4fa3ff"></table></div>
</section>
<style>
.rbtip{position:absolute;pointer-events:none;background:var(--panel2,#15181c);border:1px solid var(--gl);border-radius:10px;padding:8px 10px;font:600 13px Inter,sans-serif;line-height:1.4;white-space:nowrap;z-index:3}
.rbtip b{font-weight:800}
#rb_table td:first-child i,#rb_hist td i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px}
#rb_table tr.now td{background:color-mix(in srgb,var(--amb) 14%,transparent);font-weight:800}
</style>"""
RAINBOW_JS = NUMJS + r"""
const R = D.rainbow, H = D.hist.BTC, NM = D.rb_names, CL = D.rb_cols, G = Date.UTC(2009, 0, 3), DAY = 864e5;
const usd = (x) => '$' + (x >= 100 ? Math.round(x).toLocaleString('en-US') : x.toLocaleString('en-US', {maximumFractionDigits: 2}));
const short = (x) => x >= 1e6 ? '$' + nf(x / 1e6, 1) + 'M' : x >= 1e3 ? '$' + nf(x / 1e3, x >= 1e4 ? 0 : 1) + 'k' : '$' + Math.round(x);
const tms = (s) => Date.parse(s + 'T00:00:00Z');
const fair = (t) => Math.pow(10, R.a * Math.log10((t - G) / DAY) + R.b);
const edge = (t, k) => fair(t) * Math.pow(10, R.lo + k * R.step);
const bandOf = (t, p) => Math.max(0, Math.min(R.k - 1, Math.floor((Math.log10(p / fair(t)) - R.lo) / R.step)));
const W0 = tms(H.start), pts = H.w.map((p, i) => [W0 + i * 7 * DAY, p]);
let live = null, range = 'all';
function readout() {
  const t = live ? Date.now() : tms(R.now.date), p = live || R.now.price, b = bandOf(t, p), f = fair(t), col = CL[b];
  $('rb_big').style.borderColor = col; $('rb_big').style.background = `color-mix(in srgb, ${col} 12%, var(--panel))`;
  $('rb_band').textContent = NM[b].toUpperCase(); $('rb_band').style.color = col;
  $('rb_lbl').textContent = 'Bitcoin rainbow band · ' + (live ? 'live price' : 'daily close');
  const vs = p / f - 1;
  $('rb_note').textContent = `At ${usd(p)}, Bitcoin is ${nf(Math.abs(vs) * 100, 0)}% ${vs < 0 ? 'below' : 'above'} its long-term fair value of ${usd(f)}. Band ${b + 1} of 9.`;
  $('rb_val').innerHTML = `<div><b>${usd(p)}</b><span>${live ? 'Live price' : 'Daily close'}</span></div><div><b>${usd(f)}</b><span>Long-term fair value</span></div><div><b>${usd(edge(t, b))}</b><span>Bottom of this band</span></div><div><b>${usd(edge(t, b + 1))}</b><span>Top of this band</span></div>`;
  const tm = innerWidth < 600 ? short : usd;
  let tr = '<thead><tr><th>Band</th><th style="text-align:right">From</th><th style="text-align:right">To</th></tr></thead><tbody>';
  for (let k = R.k - 1; k >= 0; k--) tr += `<tr class="${k === b ? 'now' : ''}"><td><i style="background:${CL[k]}"></i>${k === b ? '➜ ' : ''}${NM[k]}</td><td style="text-align:right">${tm(edge(t, k))}</td><td style="text-align:right">${tm(edge(t, k + 1))}</td></tr>`;
  $('rb_table').innerHTML = tr + '</tbody>';
}
function draw() {
  const f = $('rb_chart'), Wd = f.clientWidth || 800, Ht = Wd < 600 ? 440 : Math.max(340, Math.min(540, Math.round(Wd * 0.55))), m = {l: Wd < 600 ? 46 : 58, r: 10, t: 10, b: 26};
  const end = Date.UTC(2030, 11, 31), start = range === 'all' ? W0 : Date.UTC(new Date().getUTCFullYear() - 5, 0, 1);
  const last = pts[pts.length - 1][0];
  const vis = pts.filter(([t]) => t >= start);
  const lo = Math.log10(Math.min(edge(start, 0), ...vis.map((x) => x[1])) * 0.9), hi = Math.log10(Math.max(edge(end, R.k), ...vis.map((x) => x[1])) * 1.05);
  const X = (t) => m.l + (t - start) / (end - start) * (Wd - m.l - m.r), Y = (v) => m.t + (1 - (Math.log10(v) - lo) / (hi - lo)) * (Ht - m.t - m.b);
  const ts = []; for (let t = start; t <= end; t += 14 * DAY) ts.push(t); ts.push(end);
  let g = '';
  for (let k = 0; k < R.k; k++) {
    const top = ts.map((t) => X(t).toFixed(1) + ',' + Y(edge(t, k + 1)).toFixed(1)), bot = ts.slice().reverse().map((t) => X(t).toFixed(1) + ',' + Y(edge(t, k)).toFixed(1));
    g += `<polygon points="${top.join(' ')} ${bot.join(' ')}" fill="${CL[k]}" fill-opacity="0.72"/>`;
  }
  g += `<rect x="${X(last)}" y="${m.t}" width="${Math.max(0, X(end) - X(last))}" height="${Ht - m.t - m.b}" fill="var(--bg,#0d0f12)" fill-opacity="0.35"/>`;
  const dpx = (Ht - m.t - m.b) / (hi - lo), muls = dpx >= 70 ? [1, 2, 5] : [1];
  for (let e = Math.floor(lo); e <= Math.ceil(hi); e++) for (const mul of muls) { const v = mul * Math.pow(10, e), lv = Math.log10(v); if (lv < lo || lv > hi) continue; const y = Y(v).toFixed(1);
    g += `<line x1="${m.l}" x2="${Wd - m.r}" y1="${y}" y2="${y}" stroke="#000" stroke-opacity="${mul === 1 ? .35 : .15}"/><text x="${m.l - 6}" y="${+y + 4}" text-anchor="end" font-size="12" fill="#a3a9b0">${short(v)}</text>`; }
  for (let yr = new Date(start).getUTCFullYear() + (new Date(start).getUTCMonth() ? 1 : 0); yr <= 2030; yr++) { const x = X(Date.UTC(yr, 0, 1)); if (x < m.l) continue;
    g += `<line x1="${x}" x2="${x}" y1="${m.t}" y2="${Ht - m.b}" stroke="#000" stroke-opacity=".18"/>`; if (yr % Math.max(1, Math.ceil(40 / (X(Date.UTC(2021, 0, 1)) - X(Date.UTC(2020, 0, 1))))) === 0) g += `<text x="${x}" y="${Ht - 6}" text-anchor="middle" font-size="12" font-weight="700" fill="#a3a9b0">${yr}</text>`; }
  const path = vis.map(([t, p], i) => (i ? 'L' : 'M') + X(t).toFixed(1) + ',' + Y(p).toFixed(1)).join('');
  g += `<path d="${path}" fill="none" stroke="#0b0d10" stroke-width="4" stroke-opacity=".55"/><path d="${path}" fill="none" stroke="#fff" stroke-width="2"/>`;
  const nt = live ? Date.now() : last, np = live || pts[pts.length - 1][1];
  g += `<line x1="${X(nt)}" x2="${X(nt)}" y1="${m.t}" y2="${Ht - m.b}" stroke="#fff" stroke-dasharray="4 4" stroke-opacity=".6"/><circle cx="${X(nt)}" cy="${Y(np)}" r="6" fill="var(--c-btc)" stroke="#fff" stroke-width="2"/>`;
  g += `<text x="${X(nt) + 8}" y="${m.t + 14}" font-size="12" font-weight="800" fill="#fff">TODAY</text>`;
  g += `<line id="rb_cur" x1="0" x2="0" y1="${m.t}" y2="${Ht - m.b}" stroke="#fff" stroke-opacity=".8" visibility="hidden"/>`;
  f.innerHTML = `<svg viewBox="0 0 ${Wd} ${Ht}" width="100%" height="${Ht}" role="img" aria-label="Bitcoin rainbow chart, log scale">${g}</svg>`;
  const svg = f.firstChild, tip = $('rb_tip'), cur = svg.getElementById ? svg.querySelector('#rb_cur') : null;
  const move = (ev) => {
    const r = svg.getBoundingClientRect(), cx = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left, x = cx * Wd / r.width;
    const t = start + (x - m.l) / (Wd - m.l - m.r) * (end - start); if (t < start || t > end) { tip.hidden = true; cur.setAttribute('visibility', 'hidden'); return; }
    let s = '<b>' + new Date(t).toLocaleDateString('en-GB', {month: 'short', year: 'numeric', timeZone: 'UTC'}) + '</b>';
    if (t <= last) { const q = vis.reduce((a, c) => Math.abs(c[0] - t) < Math.abs(a[0] - t) ? c : a, vis[0]); const b = bandOf(q[0], q[1]); s += `<br>Price ${usd(q[1])}<br><span style="color:${CL[b]}">■</span> ${NM[b]}`; }
    s += `<br>Fair value ${usd(fair(t))}`;
    tip.innerHTML = s; tip.hidden = false; cur.setAttribute('x1', x); cur.setAttribute('x2', x); cur.setAttribute('visibility', 'visible');
    const tw = tip.offsetWidth; tip.style.left = Math.min(r.width - tw - 4, Math.max(4, cx + 14)) + 14 + 'px'; tip.style.top = '52px';
  };
  svg.addEventListener('mousemove', move); svg.addEventListener('touchstart', move, {passive: true}); svg.addEventListener('touchmove', move, {passive: true});
  svg.addEventListener('mouseleave', () => { tip.hidden = true; cur.setAttribute('visibility', 'hidden'); });
}
$('rb_leg').innerHTML = NM.map((n, k) => `<span style="color:${CL[k]}"><i style="border-color:${CL[k]};border-top-width:8px"></i>${n}</span>`).reverse().join('');
$('rb_hist').innerHTML = '<thead><tr><th>Moment</th><th style="text-align:right">Price</th><th>Band</th></tr></thead><tbody>' + R.events.map((e) => `<tr><td>${e.kind === 'high' ? 'Cycle top' : 'Cycle bottom'} · ${new Date(e.date + 'T00:00:00Z').toLocaleDateString('en-GB', {day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'})}</td><td style="text-align:right">${usd(e.price)}</td><td><i style="background:${CL[e.band]}"></i>${NM[e.band]}</td></tr>`).join('') + '</tbody>';
document.querySelectorAll('[data-rr]').forEach((b) => b.addEventListener('click', () => { range = b.dataset.rr; document.querySelectorAll('[data-rr]').forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
readout(); draw(); addEventListener('resize', draw);
const getLive = () => fetch('https://api.exchange.coinbase.com/products/BTC-USD/ticker', {cache: 'no-store'}).then((r) => r.ok ? r.json() : 0).then((j) => { if (j && +j.price > 0) { live = +j.price; readout(); draw(); } }).catch(() => {});
getLive(); setInterval(getLive, 30000);
"""
RAINBOW_FAQ = [
    ("What is the Bitcoin rainbow chart?", "It is a long-term chart of Bitcoin's price on a logarithmic scale, with coloured bands around a curve fitted to its whole price history. The bands show whether Bitcoin is cheap or expensive compared with its own long-run trend. Blue means far below the trend, red means far above it."),
    ("How is this rainbow chart calculated?", "We fit a power-law curve to every daily Bitcoin close since 2014: the logarithm of the price against the logarithm of the number of days since Bitcoin's first block on 3 January 2009. That curve is the fair value. Nine bands of equal width on the log scale sit around it, wide enough to contain the whole history. The fit is recalculated automatically with every update."),
    ("Is the rainbow chart a price prediction?", "No. The bands after today only show where the model puts each band if the long-term trend continues. The trend can change, and past cycles do not guarantee future ones. Use it as a sense of where price sits against history, not as a forecast."),
    ("Is it accurate?", "Historically, the cycle bottoms of 2015, 2018 and 2022 sat in the lowest bands and the 2017 and 2021 tops in the highest. Each cycle top has been lower in the rainbow than the one before, so the top bands may never be reached again. The table above shows exactly where past tops and bottoms landed."),
    ("Why does this chart differ from other rainbow charts?", "Other versions use different start dates, formulas and band widths, so their bands sit at different prices. This one is fitted to Coin Metrics daily data and updated twice a day, and the method is described above in full."),
]


# ---------------------------------------------------------------- compare / correlation
CMP_NAMES = [("BTC", "Bitcoin", "#f7931a"), ("ETH", "Ethereum", "#aeb8e8"), ("SOL", "Solana", "#b98aff"), ("PAXG", "Gold", "#d4af37"),
             ("USD", "US dollar index", "#85bb65"), ("SPX", "S&P 500", "#4fa3ff"), ("NDQ", "Nasdaq", "#22b5a8"),
             ("DJI", "Dow Jones", "#9aa7b5"), ("US10Y", "US 10-year yield", "#e0a3ff")]
CMP_TOOL = """
<section class="cv wide" style="--cc:var(--amb);margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:var(--amb)">Compare Two Markets</h2></header>
  <div class="zg">
    <label>First<select id="ca"></select></label>
    <label>Second<select id="cb"></select></label>
    <label>Period<select id="cp"><option value="63">3 months</option><option value="126">6 months</option><option value="252" selected>1 year</option><option value="760">3 years</option></select></label>
  </div>
  <div class="rel" id="quick" style="margin:2px 0 4px"></div>
  <div class="thero"><div class="big" id="cbig"><span>Correlation</span><b id="cr">—</b><em id="cwhy"></em></div></div>
  <div class="tile" style="padding:14px"><div class="dfig" id="cchart"></div><div class="dleg" id="cleg"></div></div>
  <div class="tile" style="padding:14px"><div class="bh" style="margin:0 0 6px">How the link changed · rolling 3-month correlation</div><div class="dfig" id="croll"></div></div>
  <p class="note2" id="cnote"></p>
</section>
<section class="cv wide" style="--cc:#4fa3ff;margin-top:22px">
  <header class="chead"><h2 class="disp" style="color:#4fa3ff">Correlation Table</h2></header>
  <p class="note2" style="font-size:15px">Daily moves over the period above. <b style="color:var(--grn)">Green</b> = move together, <b style="color:var(--red)">red</b> = move opposite, grey = little or no link. Tap a box to compare that pair.</p>
  <div class="twrap"><table class="ttable" id="cmat"></table></div>
</section>"""
CMP_JS = r"""
const C = D.cmp, N = D.cmp_names.filter(([k]) => C.series[k]), NM = Object.fromEntries(N.map(([k, n, c]) => [k, {n, c}]));
const $ = (id) => document.getElementById(id);
const opts = N.map(([k, n]) => `<option value="${k}">${n}</option>`).join('');
$('ca').innerHTML = opts; $('cb').innerHTML = opts;
const qs = new URLSearchParams(location.search);
$('ca').value = NM[qs.get('a')] ? qs.get('a') : 'BTC'; $('cb').value = NM[qs.get('b')] ? qs.get('b') : (NM.NDQ ? 'NDQ' : 'PAXG');
const QUICK = [['BTC', 'NDQ'], ['BTC', 'PAXG'], ['PAXG', 'USD'], ['BTC', 'SPX'], ['NDQ', 'PAXG'], ['PAXG', 'US10Y'], ['SPX', 'USD'], ['BTC', 'ETH']].filter(([a, b]) => NM[a] && NM[b]);
$('quick').innerHTML = QUICK.map(([a, b]) => `<a href="#" data-a="${a}" data-b="${b}">${NM[a].n.split(' (')[0]} vs ${NM[b].n.split(' (')[0]}</a>`).join('');
$('quick').querySelectorAll('a').forEach((x) => x.addEventListener('click', (e) => { e.preventDefault(); $('ca').value = x.dataset.a; $('cb').value = x.dataset.b; run(); }));
const rets = (v, i0, diff) => { const r = []; for (let i = i0 + 1; i < v.length; i++) r.push(v[i] != null && v[i - 1] != null && v[i - 1] > 0 ? (diff ? v[i] - v[i - 1] : v[i] / v[i - 1] - 1) : null); return r; };
const RT = (k, i0) => rets(C.series[k], i0, k === 'US10Y');
function corr(x, y) { let n = 0, sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0; for (let i = 0; i < x.length; i++) { const a = x[i], b = y[i]; if (a == null || b == null || (a === 0 && b === 0)) continue; n++; sx += a; sy += b; sxx += a * a; syy += b * b; sxy += a * b; } if (n < 15) return null; const c = (sxy - sx * sy / n) / Math.sqrt((sxx - sx * sx / n) * (syy - sy * sy / n)); return isFinite(c) ? c : null; }
const word = (r) => r == null ? ['Not enough data', 'var(--mute)'] : r >= 0.7 ? ['Strongly move together', 'var(--grn)'] : r >= 0.4 ? ['Tend to move together', 'var(--grn)'] : r >= 0.2 ? ['Weak link, same direction', '#a3a9b0'] : r > -0.2 ? ['No real link', '#a3a9b0'] : r > -0.4 ? ['Weak link, opposite directions', '#a3a9b0'] : r > -0.7 ? ['Tend to move opposite', 'var(--red)'] : ['Strongly move opposite', 'var(--red)'];
const fmtR = (r) => r == null ? '—' : (r > 0 ? '+' : '') + r.toFixed(2);
const mon = (d) => new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', {month: 'short', year: '2-digit', timeZone: 'UTC'});
function lineChart(el, dates, lines, opt = {}) {
  const W = el.clientWidth || 800, H = Math.max(230, Math.min(380, Math.round(W * 0.42))), m = {l: 54, r: 14, t: 10, b: 26};
  const all = lines.flatMap((l) => l.v).filter((x) => x != null);
  let lo = opt.lo != null ? opt.lo : Math.min(...all), hi = opt.hi != null ? opt.hi : Math.max(...all); const pad = (hi - lo) * 0.06 || 1; if (opt.lo == null) lo -= pad; if (opt.hi == null) hi += pad;
  const X = (i) => m.l + i / Math.max(1, dates.length - 1) * (W - m.l - m.r), Y = (y) => m.t + (1 - (y - lo) / (hi - lo)) * (H - m.t - m.b);
  let g = ''; const ticks = opt.ticks || [0, 1, 2, 3, 4].map((k) => lo + (hi - lo) * k / 4);
  ticks.forEach((y) => { g += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(y)}" y2="${Y(y)}" stroke="${opt.zero === y ? '#5a6068' : '#2a2e33'}"/><text x="${m.l - 8}" y="${Y(y) + 4}" text-anchor="end" font-size="12" fill="#a3a9b0">${opt.tf ? opt.tf(y) : y.toFixed(0)}</text>`; });
  let lx = -99; dates.forEach((d, i) => { if (i && d.slice(0, 7) !== dates[i - 1].slice(0, 7) && X(i) - lx > 58) { lx = X(i); g += `<text x="${X(i)}" y="${H - 6}" text-anchor="middle" font-size="12" font-weight="700" fill="#a3a9b0">${mon(d).toUpperCase()}</text>`; } });
  const path = (v) => v.map((y, i) => y == null ? '' : `${i && v[i - 1] != null ? 'L' : 'M'}${X(i).toFixed(1)},${Y(y).toFixed(1)}`).join('');
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" role="img" aria-label="${esc(opt.label || 'chart')}">${g}${lines.map((l) => `<path d="${path(l.v)}" fill="none" stroke="${l.c}" stroke-width="2.4" stroke-linejoin="round"/>`).join('')}</svg>`;
}
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
function run() {
  const A = $('ca').value, B = $('cb').value, n = +$('cp').value, L = C.dates.length, i0 = Math.max(0, L - n);
  history.replaceState(null, '', `?a=${A}&b=${B}`);
  const va = C.series[A], vb = C.series[B], dates = C.dates.slice(i0);
  const base = (v) => { const b0 = v.slice(i0).find((x) => x != null); return v.slice(i0).map((x) => x == null ? null : x / b0 * 100); };
  const ra = base(va), rb = base(vb), r = corr(RT(A, i0), RT(B, i0)), [w, col] = word(r);
  $('cr').textContent = fmtR(r); $('cr').style.color = col; $('cbig').style.borderColor = col;
  $('cwhy').textContent = `${NM[A].n} and ${NM[B].n}: ${w.toLowerCase()} (daily moves, last ${$('cp').selectedOptions[0].text}).`;
  const pct = (v) => { const e = v[v.length - 1]; return (e >= 100 ? '+' : '') + (e - 100).toFixed(1) + '%'; };
  const ca = NM[A].c, cbb = A === B ? '#ffffff' : NM[B].c;
  lineChart($('cchart'), dates, [{v: ra, c: ca}, {v: rb, c: cbb}], {label: 'Performance compared, rebased to 100', tf: (y) => y.toFixed(0)});
  $('cleg').innerHTML = `<span style="color:${ca}"><i style="border-color:${ca}"></i>${NM[A].n} ${pct(ra)}</span><span style="color:${cbb}"><i style="border-color:${cbb}"></i>${NM[B].n} ${pct(rb)}</span><span><i style="border-color:transparent"></i>Both start at 100</span>`;
  // rolling 63-day correlation over the whole history shown (min 1 year window for context)
  const j0 = Math.max(64, L - Math.max(n, 252)), rd = [], rv = [], xa = RT(A, 0), xb = RT(B, 0);
  for (let j = j0; j < L; j++) { rd.push(C.dates[j]); rv.push(corr(xa.slice(j - 64, j - 1), xb.slice(j - 64, j - 1))); }
  lineChart($('croll'), rd, [{v: rv, c: '#ffb000'}], {lo: -1, hi: 1, ticks: [-1, -0.5, 0, 0.5, 1], zero: 0, tf: (y) => (y > 0 ? '+' : '') + y.toFixed(1), label: 'Rolling correlation'});
  $('cnote').textContent = `Correlation runs from −1 (always opposite) through 0 (no link) to +1 (always together). It is measured on daily % moves, not on price levels. Stock markets trade on weekdays only, so weekend crypto moves count on Monday. For the 10-year yield, the daily change in the rate is used. Data to ${C.dates[L - 1]}.`;
  // matrix
  const ks = N.map(([k]) => k), R = {}; ks.forEach((k) => R[k] = RT(k, i0));
  const cell = (a, b) => { const c = a === b ? 1 : corr(R[a], R[b]); const bg = c == null ? 'transparent' : c > 0 ? `rgba(63,191,111,${Math.min(0.85, Math.abs(c))})` : `rgba(232,98,91,${Math.min(0.85, Math.abs(c))})`; return `<td style="background:${bg};text-align:center;cursor:pointer;color:${Math.abs(c || 0) > 0.55 ? '#0b0b0b' : 'var(--ink)'}" data-a="${a}" data-b="${b}">${a === b ? '·' : fmtR(c)}</td>`; };
  $('cmat').innerHTML = `<thead><tr><th></th>${ks.map((k) => `<th style="text-align:center;color:${NM[k].c}">${{PAXG: 'GOLD', NDQ: 'NASDAQ', SPX: 'S&P', DJI: 'DOW', US10Y: '10Y'}[k] || k}</th>`).join('')}</tr></thead><tbody>${ks.map((a) => `<tr><td style="color:${NM[a].c};white-space:nowrap">${NM[a].n.split(' (')[0]}</td>${ks.map((b) => cell(a, b)).join('')}</tr>`).join('')}</tbody>`;
  $('cmat').querySelectorAll('td[data-a]').forEach((td) => td.addEventListener('click', () => { if (td.dataset.a === td.dataset.b) return; $('ca').value = td.dataset.a; $('cb').value = td.dataset.b; run(); scrollTo({top: 0, behavior: 'smooth'}); }));
}
['ca', 'cb', 'cp'].forEach((i) => $(i).addEventListener('input', run));
addEventListener('resize', run);
run();
"""
CMP_FAQ = [
    ("What does correlation mean?", "Correlation measures how two markets move day to day, from −1 to +1. Near +1 they rise and fall together; near −1 one tends to rise when the other falls; near 0 there is no reliable link."),
    ("Is Bitcoin correlated with the Nasdaq?", "Often, yes. Since 2020 Bitcoin has frequently moved with tech stocks, especially in sell-offs, but the link comes and goes. The rolling chart above shows how strong it is right now."),
    ("Is gold a hedge against stocks or crypto?", "Gold usually has a low or slightly negative link to stocks and crypto, which is why investors use it to diversify. It often moves opposite to the US dollar."),
    ("Where does the stock market data come from?", "Daily closing levels of the S&P 500, the Nasdaq Composite and the Dow Jones, and the 10-year US Treasury yield, come from the US Federal Reserve's FRED database. We show only % performance and correlations, not the index levels themselves."),
    ("What does the 10-year yield tell me?", "It is the interest rate on 10-year US government bonds. When it rises quickly, it often weighs on gold, tech stocks and crypto, because safe bonds pay more. A negative correlation with these assets shows that pull."),
    ("Does correlation predict prices?", "No. It describes how markets have moved together in the past. Relationships change, sometimes suddenly. Use it as context, not as a signal to buy or sell."),
]

def gold_conv_data(conv_data):
    d = dict(conv_data)
    d["curs"] = CURS
    return d


def all_pages(conv_data, slot):
    """Return {slug: (title, desc, body, js, data)}."""
    full = conv_data.get("_full", {})
    data = gold_conv_data({k: v for k, v in conv_data.items() if k != "_full"})
    try:  # silver reference price at build time (fallback if the live feed is blocked)
        import urllib.request
        req = urllib.request.Request("https://api.gold-api.com/price/XAG", headers={"User-Agent": "Mozilla/5.0 MarketLights"})
        data["silver_close"] = float(json.load(urllib.request.urlopen(req, timeout=15))["price"])
    except Exception as ex:
        print("silver fail", ex)
    out = {
        "gold-price-per-gram": (
            "Gold Price per Gram Today: 24K, 22K, 18K · MarketLights",
            "Live gold price per gram in USD, INR, AED, EUR and 25 more currencies. 24K, 22K, 18K per gram, tola, ounce and kilo, plus a value calculator.",
            GOLD_BODY.replace("@@AD1@@", slot("gold-mid", "rect", "responsive · up to 728×280")).replace("@@FAQ@@", faq_html(GOLD_FAQ)).replace("@@REL@@", related([("/convert/", "Gold Weight Converter")] + RELATED[1:])),
            GOLD_JS.replace("<script>\n{", "<script>\n{" + SWIPE + "}\n{", 1), data),
    }
    ad = lambda n: slot(n, "rect", "responsive · up to 728×280")
    GOLDREL = [("/gold-price-per-gram/", "Gold Price per Gram"), ("/silver-price-per-gram/", "Silver Price per Gram"), ("/zakat-calculator/", "Zakat Calculator"), ("/troy-ounce-to-grams/", "Troy Ounce to Grams")]
    CRYPTOREL = [("/bitcoin-rainbow-chart/", "Bitcoin Rainbow Chart"), ("/bitcoin-signal-today/", "Bitcoin Signal Today"), ("/bitcoin-dca-calculator/", "Bitcoin DCA Calculator"), ("/crypto-profit-calculator/", "Crypto Profit Calculator"), ("/currency-converter/", "Currency Converter")]
    CALCREL = [("/percentage-calculator/", "Percentage Calculator"), ("/rule-of-three-calculator/", "Rule of Three"), ("/currency-converter/", "Currency Converter"), ("/kg-to-lbs/", "Kg to Lbs")]
    def add(slug, title, desc, h1, intro, tool, explain, faq, rel, code, cur=False, shared=False):
        body = page(h1, intro, tool, explain, faq, [x for x in rel if x[0] != f"/{slug}/"] + [x for x in RELATED if x[0] not in [y[0] for y in rel]], cur).replace("@@AD@@", ad(slug + "-mid"))
        out[slug] = (title, desc, body, code if code.startswith("<script") else js(code, shared), data)
    add("silver-price-per-gram", "Silver Price per Gram Today, Live · MarketLights",
        "Live silver price per gram today in 29 currencies. Fine, Britannia and sterling silver per gram, ounce, tola and kilo, plus a silver value calculator.",
        "Silver Price per Gram Today", "Live spot price of silver per gram, troy ounce, tola and kilogram in your currency, for fine (999), Britannia, sterling (925) and coin silver. Updates every minute.",
        SILVER_TOOL, "<h2 class='disp'>How the Silver Price Works</h2><p>Silver, like gold, is priced worldwide in US dollars per <b>troy ounce</b> (31.1035 grams). The price per gram is the ounce price divided by 31.1035, converted at today's exchange rate. Sterling silver is 92.5% pure, so it is worth 92.5% of the fine-silver price per gram.</p><p>Silver moves more sharply than gold because about half of it is used in industry, from solar panels to electronics. Use these figures as a fair reference, then compare with your dealer's buy and sell prices.</p>",
        SILVER_FAQ, GOLDREL, NUMJS + SILVER_JS, cur=True, shared=True)
    add("troy-ounce-to-grams", "Troy Ounce to Grams Converter · MarketLights",
        "Convert troy ounces to grams and grams to troy ounces instantly, with a conversion table, the difference from a regular ounce, and the live value in gold.",
        "Troy Ounce to Grams", "Convert troy ounces to grams and back. Type in either box. Includes the difference from a regular ounce and the live value of that weight in 24K gold.",
        TROY_TOOL, "<h2 class='disp'>Troy Ounce vs Regular Ounce</h2><p>A <b>troy ounce</b> is 31.1035 grams and is used only for precious metals. A <b>regular ounce</b> (avoirdupois), used for food and post, is 28.3495 grams. So a troy ounce is about 9.7% heavier. Confusing the two is a common and expensive mistake when buying gold or silver online.</p><p>Bullion coins and bars are sold in troy ounces: a 1 oz gold coin holds 31.1 grams of gold, and a 1 kilogram bar holds 32.15 troy ounces.</p>",
        TROY_FAQ, GOLDREL, TROY_JS)
    add("percentage-calculator", "Percentage Calculator: %, Change, Add or Remove · MarketLights",
        "Free percentage calculator: find X% of a number, what percent one number is of another, percentage increase or decrease, and add or subtract a percentage.",
        "Percentage Calculator", "Four everyday percentage sums in one place. Change any number and the answer updates at once.",
        PCT_TOOL, "<h2 class='disp'>Percentages Made Simple</h2><p>A percentage is a number out of 100. To use one in a sum, divide it by 100 first: 15% becomes 0.15. Then multiply to find a share, or compare two numbers and multiply by 100 to turn the ratio back into a percentage.</p><p>Percentage change always compares against the <b>starting</b> value. That is why a 50% fall followed by a 50% rise does not bring you back where you started: 100 falls to 50, and 50 rises only to 75.</p>",
        PCT_FAQ, CALCREL, PCT_JS)
    add("rule-of-three-calculator", "Rule of Three Calculator (Direct & Inverse) · MarketLights",
        "Free rule of three calculator for direct and inverse proportion. Find the missing value for prices, recipes, fuel, workers and days, with worked examples.",
        "Rule of Three Calculator", "Find a missing value from three known ones. Use direct proportion when both go up together, inverse when one goes up as the other goes down.",
        R3_TOOL, "<h2 class='disp'>How the Rule of Three Works</h2><p>Write the two pairs as a ratio: A is to B as C is to X. For <b>direct</b> proportion, X = B × C ÷ A. For <b>inverse</b> proportion, X = A × B ÷ C.</p><p>Everyday examples: a recipe for 4 people scaled to 6, the price of 750 grams when you know the price per kilo, how long a trip takes at a different speed, or how many days a job needs with more workers.</p>",
        R3_FAQ, CALCREL, R3_JS)
    add("currency-converter", "Currency Converter: Live Rates, 29 Currencies · MarketLights",
        "Free currency converter with live mid-market exchange rates for USD, EUR, GBP, INR, AED, JPY, CNY, THB and 21 more currencies. See any amount in every currency at once.",
        "Currency Converter", "Live mid-market exchange rates for 29 world currencies. Type an amount, pick two currencies, and see the same amount in every other currency too.",
        FX_TOOL, "<h2 class='disp'>What Is the Mid-Market Rate?</h2><p>Every currency has a buy price and a sell price. The <b>mid-market rate</b> is the point halfway between them, the fairest reference there is. Banks, cards and money changers add their own margin on top, so the rate they offer is usually worse.</p><p>Before you change money or pay abroad, check the rate here, then compare it with your provider's rate. The difference is the hidden fee you are paying.</p>",
        FX_FAQ, CALCREL, FX_JS)
    add("kg-to-lbs", "Kg to Lbs: Kilograms to Pounds Converter · MarketLights",
        "Convert kilograms to pounds and pounds to kilograms instantly. Shows pounds and ounces, stone and pounds, plus a kg to lbs chart from 1 to 150 kg.",
        "Kg to Lbs Converter", "Convert kilograms to pounds, or pounds to kilograms. Type in either box. Also shows pounds and ounces, and stone and pounds.",
        KG_TOOL, "<h2 class='disp'>Kilograms and Pounds</h2><p>One kilogram is <b>2.20462 pounds</b>, and one pound is <b>0.453592 kilograms</b>. Most of the world weighs in kilograms; the United States uses pounds, and the UK often gives body weight in stone and pounds.</p><p>Quick mental trick: double the kilograms and add 10%. 80 kg × 2 = 160, plus 16 = 176 lb (exact: 176.4 lb).</p>",
        KG_FAQ, CALCREL, KG_JS)
    data["hist"] = full.get("hist", {})
    add("zakat-calculator", "Zakat Calculator 2026 with Live Gold & Silver Nisab · MarketLights",
        "Free zakat calculator with today's gold and silver nisab in 29 currencies. Add cash, gold, silver, investments and debts to see the 2.5% zakat due.",
        "Zakat Calculator", "Work out the zakat due on your wealth, using today's live gold and silver prices for the nisab, in your own currency. Your figures stay on your device.",
        ZAKAT_TOOL, "<h2 class='disp'>How Zakat Is Calculated</h2><p>Add up the wealth you have held for a full lunar year: cash and bank balances, gold and silver, shares, funds and crypto, business stock for sale, and money owed to you that you expect back. Take away debts and bills that are due now. If what is left is at least the <b>nisab</b>, the value of 85 grams of gold or 595 grams of silver, zakat is <b>2.5%</b> of it.</p><p>Schools of thought differ on details such as jewellery that is worn and long-term debts. This calculator follows the common approach; for a ruling on your own situation, ask a scholar you trust.</p>",
        ZAKAT_FAQ, GOLDREL, ZAKAT_JS, cur=True, shared=True)
    add("crypto-profit-calculator", "Crypto Profit Calculator: Bitcoin, Ethereum, Solana · MarketLights",
        "Free crypto profit calculator with live Bitcoin, Ethereum and Solana prices. Enter buy price, sell price and fees to see profit, ROI and break-even price.",
        "Crypto Profit Calculator", "See the profit or loss on a Bitcoin, Ethereum or Solana trade after fees, with the break-even price. The sell price starts at today's live price.",
        PROFIT_TOOL, "<h2 class='disp'>Profit, Fees and Break-Even</h2><p>Fees are taken twice: once when you buy and again when you sell. A trade can look profitable on price alone and still lose money once both fees are paid. The <b>break-even price</b> shows exactly where the line is.</p><p>Crypto prices can fall as fast as they rise. Check the <a href='/bitcoin-signal-today/' style='color:var(--amb)'>Bitcoin Signal Today</a> for the current trend before you decide anything, and never invest money you cannot afford to lose.</p>",
        PROFIT_FAQ, CRYPTOREL, PROFIT_JS, cur=True, shared=True)
    add("bitcoin-dca-calculator", "Bitcoin DCA Calculator: What If I Bought Every Month? · MarketLights",
        "See what regular Bitcoin, Ethereum, Solana or gold purchases since any month from 2015 would be worth today, compared with investing a lump sum.",
        "Bitcoin DCA Calculator", "What if you had bought a fixed amount of Bitcoin every month? Pick an asset, an amount and a start date to see what it would be worth today.",
        DCA_TOOL, "<h2 class='disp'>Why People Use DCA</h2><p>Nobody can reliably buy at the bottom. Dollar-cost averaging removes the guesswork: you invest the same amount on a schedule, so falling prices simply buy you more coins. Over Bitcoin's history, regular buyers have usually ended up with a lower average price than people who bought in one go near a peak.</p><p>It does not remove risk. Bitcoin has fallen more than 70% several times, and a DCA plan started near a peak can stay below water for a long time. The chart above shows that journey, not just the end result.</p>",
        DCA_FAQ, CRYPTOREL, DCA_JS)
    if full.get("rainbow"):
        data["rainbow"] = full["rainbow"]; data["rb_names"] = RB_NAMES; data["rb_cols"] = RB_COLS
        add("bitcoin-rainbow-chart", "Bitcoin Rainbow Chart Today: Live Price Bands · MarketLights",
            "Live Bitcoin rainbow chart: see which price band Bitcoin is in today, its long-term fair value, today's price for every band, and where past tops and bottoms landed.",
            "Bitcoin Rainbow Chart", "Where is Bitcoin today against its long-term trend? The rainbow shows nine price bands around a curve fitted to Bitcoin's whole history, from fire sale in blue to bubble in red. Updated twice a day, with the live price.",
            RAINBOW_TOOL, "<h2 class='disp'>How to Read the Rainbow</h2><p>The middle of the rainbow is Bitcoin's <b>long-term fair value</b>: a curve that rises every year, but more slowly over time. The <b>blue bands</b> below it are where Bitcoin has been cheap compared with its own history, and where past cycle bottoms formed. The <b>red bands</b> above it are where past bubbles peaked.</p><p>The chart uses a <b>log scale</b>: each step up the price axis is ten times the one below. That is why a $100 move in 2015 and a $10,000 move today take up a similar space. Use the rainbow together with today's <a href='/bitcoin-signal-today/' style='color:var(--amb)'>Bitcoin Signal</a>, which reads the shorter-term trend. Neither is advice to buy or sell.</p>",
            RAINBOW_FAQ, CRYPTOREL, RAINBOW_JS)
    if full.get("cmp"):
        body = page("Compare Markets: Crypto, Gold, Dollar and Stocks", "See how Bitcoin, Ethereum, Solana, gold, the US dollar and the stock market move together or apart. Pick any two, compare their performance on one chart, and read the correlation in plain words.", CMP_TOOL,
            "<h2 class='disp'>Why Correlation Matters</h2><p>If two things you own always move together, owning both does not spread your risk. Correlation tells you which markets <b>move together</b>, which <b>move opposite</b>, and which are <b>unrelated</b>, so you can see how diversified you really are.</p><p>Links change with the times. In calm markets Bitcoin can move on its own; in a panic it often falls together with tech stocks. Gold tends to rise when the US dollar weakens. Always look at the rolling chart, not just one number.</p>",
            CMP_FAQ, [("/", "Daily Market Lights"), ("/bitcoin-signal-today/", "Bitcoin Signal Today"), ("/gold-price-per-gram/", "Gold Price per Gram"), ("/bitcoin-dca-calculator/", "Bitcoin DCA Calculator")]).replace("@@AD@@", ad("compare-mid"))
        out["compare"] = ("Compare Markets: Bitcoin vs Nasdaq, Gold vs Dollar Correlation · MarketLights",
            "Compare Bitcoin, Ethereum, gold, the US dollar, the S&P 500, the Nasdaq and the Dow on one chart, with correlation explained in plain words. Free and updated daily.",
            body, js(CMP_JS), {"cmp": full["cmp"], "cmp_names": CMP_NAMES})
    tool, explain, code, faq, day = btc_page(full)
    add("bitcoin-signal-today", f"Bitcoin Signal Today ({day}) · MarketLights",
        "Today's Bitcoin traffic light: trend, RSI, support, resistance, distance from record and market mood, updated twice a day. Plain English, information only.",
        "Bitcoin Signal Today", "One clear daily reading for Bitcoin: a green, amber or red light with the trend, RSI, support and resistance behind it. Updated automatically twice a day.",
        tool, explain, faq, [("/", "Full Dashboard: Bitcoin, Ethereum &amp; Gold"), ("/currency-converter/", "Currency Converter"), ("/percentage-calculator/", "Percentage Calculator")], code)
    return out
