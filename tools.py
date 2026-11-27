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
.faq details{border:2px solid var(--line);border-radius:12px;background:var(--panel);padding:14px 16px;margin-top:10px}
.faq summary{font:700 18px Inter,sans-serif;cursor:pointer}
.faq details[open]{border-color:var(--amb)}
.faq p{margin:10px 0 0;line-height:1.65}
.rel{display:flex;flex-wrap:wrap;gap:10px}
.rel a{font:800 14px Inter,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--ink);text-decoration:none;border:2px solid var(--line);border-radius:10px;padding:10px 14px;background:var(--panel)}
.rel a:hover{border-color:var(--amb);color:var(--amb)}
.srcline{font-size:14px;color:var(--mute);margin:0}
.srcline b{color:var(--ink)}
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
  <select id="cur" aria-label="Currency" style="font:700 16px Inter,sans-serif;background:var(--bg);color:var(--ink);border:2px solid var(--line);border-radius:8px;padding:8px 10px"></select>
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
    GOLDREL = [("/gold-price-per-gram/", "Gold Price per Gram"), ("/silver-price-per-gram/", "Silver Price per Gram"), ("/troy-ounce-to-grams/", "Troy Ounce to Grams")]
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
    tool, explain, code, faq, day = btc_page(full)
    add("bitcoin-signal-today", f"Bitcoin Signal Today ({day}) · MarketLights",
        "Today's Bitcoin traffic light: trend, RSI, support, resistance, distance from record and market mood, updated twice a day. Plain English, information only.",
        "Bitcoin Signal Today", "One clear daily reading for Bitcoin: a green, amber or red light with the trend, RSI, support and resistance behind it. Updated automatically twice a day.",
        tool, explain, faq, [("/", "Full Dashboard: Bitcoin, Ethereum &amp; Gold"), ("/currency-converter/", "Currency Converter"), ("/percentage-calculator/", "Percentage Calculator")], code)
    return out
