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
.faq details{border:2px solid var(--line);border-radius:12px;background:var(--panel);padding:14px 16px;margin-top:10px}
.faq summary{font:700 18px Inter,sans-serif;cursor:pointer}
.faq details[open]{border-color:var(--amb)}
.faq p{margin:10px 0 0;line-height:1.65}
.rel{display:flex;flex-wrap:wrap;gap:10px}
.rel a{font:800 14px Inter,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--ink);text-decoration:none;border:2px solid var(--line);border-radius:10px;padding:10px 14px;background:var(--panel)}
.rel a:hover{border-color:var(--amb);color:var(--amb)}
.srcline{font-size:14px;color:var(--mute);margin:0}
.srcline b{color:var(--ink)}
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


def gold_conv_data(conv_data):
    d = dict(conv_data)
    d["curs"] = CURS
    return d


def all_pages(conv_data, slot):
    """Return {slug: (title, desc, body, js, data)}."""
    data = gold_conv_data(conv_data)
    return {
        "gold-price-per-gram": (
            "Gold Price per Gram Today · Live 24K, 22K, 18K in Your Currency · MarketLights",
            "Live gold price per gram today in USD, INR, AED, EUR, GBP and 25 more currencies. 24K, 22K, 21K, 18K, 14K prices per gram, tola, ounce and kilo, plus a gold value calculator.",
            GOLD_BODY.replace("@@AD1@@", slot("gold-mid", "rect", "responsive · up to 728×280")).replace("@@FAQ@@", faq_html(GOLD_FAQ)).replace("@@REL@@", related([("/convert/", "Gold Weight Converter")] + RELATED[1:])),
            GOLD_JS, data),
    }
