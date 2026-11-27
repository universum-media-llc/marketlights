"""Daily Main Light reading for Bitcoin, Ethereum, Solana and gold (PAX Gold).

Usage: put backtest2.py next to this file, then run:  python3 live_light.py
Downloads fresh data into ./data/ and prints one markdown table row per asset.
Rules are the adopted ones (Falling needs a strong US dollar). Change nothing here without
re-running the backtest.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={a}&metrics={m}&frequency=1d&start_time={s}&page_size=10000&format=csv"
GET = {
    "cm_btc.csv": CM.format(a="btc", m="PriceUSD,CapMVRVCur", s="2014-01-01"),
    "cm_eth.csv": CM.format(a="eth", m="PriceUSD,CapMVRVCur", s="2016-01-01"),
    "cm_sol.csv": CM.format(a="sol", m="PriceUSD", s="2019-01-01"),
    "cm_paxg.csv": CM.format(a="paxg", m="PriceUSD", s="2019-01-01"),
    "fng.csv": "https://api.alternative.me/fng/?limit=0&format=csv",
    "dollar.csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
}
for f, url in GET.items():
    subprocess.run(["curl", "-s", "-m", "90", "-o", os.path.join(DATA, f), url], check=True)

# Stock-market funds for the Compare page (ETFs that track the big indexes). Never fatal.
STOCKS = ["SPY", "QQQ", "DIA", "NVDA", "MSTR", "TLT"]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def _get(url):
    r = subprocess.run(["curl", "-s", "-L", "-m", "60", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")
def fetch_stock(t):
    rows = []
    try:  # 1) Stooq daily CSV
        txt = _get(f"https://stooq.com/q/d/l/?s={t.lower()}.us&i=d")
        if txt.startswith("Date,"):
            for ln in txt.splitlines()[1:]:
                c = ln.split(",")
                if len(c) >= 5 and c[4] not in ("", "null"):
                    rows.append((c[0], float(c[4])))
    except Exception as e:
        print("stooq", t, e)
    if len(rows) < 500:  # 2) Yahoo chart API
        try:
            import json as _j, datetime as _d
            j = _j.loads(_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10y&interval=1d"))
            res = j["chart"]["result"][0]
            closes = res["indicators"]["adjclose"][0]["adjclose"] if "adjclose" in res["indicators"] else res["indicators"]["quote"][0]["close"]
            rows = [(_d.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d"), float(c)) for ts, c in zip(res["timestamp"], closes) if c is not None]
        except Exception as e:
            print("yahoo", t, e)
    if len(rows) >= 500:
        with open(os.path.join(DATA, f"stk_{t}.csv"), "w") as fh:
            fh.write("Date,Close\n" + "".join(f"{d},{v}\n" for d, v in rows))
        print("stock", t, len(rows), rows[-1])
    else:
        print("stock", t, "FAILED")
for t in STOCKS:
    fetch_stock(t)

os.environ["BT_DATA"] = DATA + "/"
sys.path.insert(0, HERE)
import backtest2 as B

assets = [("Bitcoin", "cm_btc.csv", True, "2018-01-01"), ("Ethereum", "cm_eth.csv", True, "2018-01-01"),
          ("Solana", "cm_sol.csv", True, "2021-01-01"), ("Gold (PAX Gold)", "cm_paxg.csv", False, "2020-09-01")]
fng_today = B.FNG[max(B.FNG)] if B.FNG else None
dollar_today = B.DOLLAR_STRONG[max(B.DOLLAR_STRONG)]
for name, f, use_fng, st in assets:
    r = B.run(*B.load_cm(f), use_fng, st, "dollar")
    L = r["latest"]
    rp = f"{L['realized_price']:,.0f}" if L["realized_price"] else "-"
    print(f"| {L['date']} | {name} | {L['phase']} | {L['price']:,.2f} | {L['rsi']:.0f} | {fng_today if use_fng else '-'} | {'strong' if dollar_today else 'weak'} | {rp} |")
