"""Build MarketLights: compute today's readings and write dist/index.html.

Run after fresh data is in ../data (live_light.py downloads it):  python3 build.py
Uses the adopted Main Light rules from backtest2.py.
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest2 as B

ASSETS = [  # name, file, uses crypto fear & greed, backtest start, show Main Light
    ("Bitcoin", "BTC", "cm_btc.csv", True, "2018-01-01", True),
    ("Ethereum", "ETH", "cm_eth.csv", True, "2018-01-01", True),
    ("Gold", "PAXG", "cm_paxg.csv", False, "2020-09-01", True),
    ("Solana", "SOL", "cm_sol.csv", True, "2021-01-01", False),
]

SENT = {
    "Falling": "Downtrend with a strong US dollar behind it. Risk is high.",
    "Bottoming": "Still in a downtrend, but selling looks exhausted. A bottom may be forming; not confirmed yet.",
    "Consolidating": "Moving sideways. No clear direction for now.",
    "Rising": "Uptrend: price is above its key averages.",
    "Overheated": "Rising too fast. The risk of a pullback is high.",
}

def rsi_series(c):
    out = [None] * len(c); g = l = 0.0
    for i in range(1, len(c)):
        ch = c[i] - c[i - 1]; gg, ll = max(ch, 0), max(-ch, 0)
        if i <= 14:
            g += gg; l += ll
            if i == 14:
                g /= 14; l /= 14; out[i] = 100 - 100 / (1 + g / l) if l else 100
        else:
            g = (g * 13 + gg) / 14; l = (l * 13 + ll) / 14
            out[i] = 100 - 100 / (1 + g / l) if l else 100
    return out

def swings(vals, k):
    lows, highs = [], []
    for i in range(k, len(vals) - k):
        w = vals[i - k:i + k + 1]
        if vals[i] == min(w): lows.append(vals[i])
        if vals[i] == max(w): highs.append(vals[i])
    return lows, highs

def merge(levels_sorted, gap=0.015):
    out = []
    for v in levels_sorted:
        if not out or abs(v / out[-1] - 1) > gap:
            out.append(v)
    return out

def levels(vals, price, k):
    lows, highs = swings(vals, k)
    sup = merge(sorted({v for v in lows if v < price * 0.995}, reverse=True))[:2]
    res = merge(sorted({v for v in highs if v > price * 1.005}))[:2]
    if not sup and min(vals) < price * 0.995:
        sup = [min(vals)]
    return sup, res

def rsi_word(r):
    return "oversold" if r <= 30 else "overbought" if r >= 70 else "neutral"

def fng_word(f):
    return ("Extreme fear" if f <= 24 else "Fear" if f <= 44 else "Neutral" if f <= 55 else "Greed" if f <= 75 else "Extreme greed")


# Exchange rates (units of each currency per 1 US dollar), Federal Reserve FRED daily series.
FX_SERIES = {"EUR": ("DEXUSEU", True), "GBP": ("DEXUSUK", True), "AUD": ("DEXUSAL", True),
             "THB": ("DEXTHUS", False), "JPY": ("DEXJPUS", False), "KRW": ("DEXKOUS", False),
             "CNY": ("DEXCHUS", False), "INR": ("DEXINUS", False), "BRL": ("DEXBZUS", False),
             "MXN": ("DEXMXUS", False), "CAD": ("DEXCAUS", False), "CHF": ("DEXSZUS", False),
             "SGD": ("DEXSIUS", False)}
def fx_rates():
    import urllib.request, csv as _c, io
    cache = os.path.join(HERE, "fx.json")
    rates, last = {}, ""
    for cur, (sid, inverted) in FX_SERIES.items():
        try:
            txt = urllib.request.urlopen(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=" +
                                         (dt.date.today() - dt.timedelta(days=40)).isoformat(), timeout=30).read().decode()
            rows = [r for r in _c.reader(io.StringIO(txt))][1:]
            rows = [r for r in rows if len(r) == 2 and r[1] not in ("", ".")]
            v = float(rows[-1][1]); rates[cur] = 1 / v if inverted else v; last = max(last, rows[-1][0])
        except Exception as e:
            print("fx fail", cur, e)
    if len(rates) == len(FX_SERIES):
        json.dump({"rates": rates, "date": last}, open(cache, "w"))
        return rates, last
    if os.path.exists(cache):
        c = json.load(open(cache)); c["rates"].update(rates); return c["rates"], c["date"]
    return rates, last

def main():
    fng_dates = sorted(B.FNG)
    fng_now = B.FNG[fng_dates[-1]] if fng_dates else None
    fng_week = B.FNG.get(fng_dates[-8]) if len(fng_dates) > 8 else None
    dollar_strong = B.DOLLAR_STRONG[max(B.DOLLAR_STRONG)]
    out = []
    for name, tick, f, use_fng, start, light in ASSETS:
        price, mvrv = B.load_cm(f)
        r = B.run(price, mvrv, use_fng, start, "dollar")
        dates = sorted(price); c = [price[d] for d in dates]
        p = c[-1]; rs = rsi_series(c)[-1]
        s50 = sum(c[-50:]) / 50; s200 = sum(c[-200:]) / 200
        trend = ("Uptrend (above both averages)" if p > s50 and p > s200 else
                 "Downtrend (below both averages)" if p < s50 and p < s200 else "Sideways (between averages)")
        cross = "50-day above 200-day" if s50 > s200 else "50-day below 200-day"
        ath = max(c)
        d_sup, d_res = levels(c[-180:], p, 5)
        weekly = c[::-1][::7][::-1]
        w_sup, w_res = levels(weekly[-104:], p, 2)
        low365 = min(c[-365:]); hi365 = max(c[-365:])
        rp = p / mvrv[dates[-1]] if dates[-1] in mvrv else None
        phases = [s["phase"] for s in r["series"]]
        since = dates[-1]
        for s in reversed(r["series"]):
            if s["phase"] != phases[-1]:
                break
            since = s["date"]
        per = next(iter(r["periods"])); S = r["periods"][per]["stats"]; st = r["periods"][per]["strategy"]
        spark = [round(v, 4) for v in c[-120:]]
        n = len(c)
        avg50 = [round(sum(c[i - 49:i + 1]) / 50, 4) for i in range(n - 120, n)]
        avg200 = [round(sum(c[i - 199:i + 1]) / 200, 4) for i in range(n - 120, n)]
        low2y = min(c[-730:])
        wd = dates[::-1][::7][::-1]; wc = [price[d] for d in wd]; nw = len(wc)
        wspark = [round(v, 4) for v in wc[-104:]]; wdates = wd[-104:]
        wavg50 = [round(sum(wc[i - 49:i + 1]) / 50, 4) if i >= 49 else None for i in range(nw - 104, nw)]
        wavg200 = [round(sum(wc[i - 199:i + 1]) / 200, 4) if i >= 199 else None for i in range(nw - 104, nw)]
        out.append({
            "name": name, "tick": tick, "light": light, "phase": r["latest"]["phase"], "since": since,
            "sentence": SENT[r["latest"]["phase"]], "price": p, "date": dates[-1], "rsi": rs, "rsi_word": rsi_word(rs),
            "trend": trend, "cross": cross, "sma50": s50, "sma200": s200, "ath": ath, "from_ath": p / ath - 1,
            "support_d": d_sup, "resist_d": d_res, "support_w": w_sup, "resist_w": w_res,
            "low365": low365, "high365": hi365, "realized": rp, "spark": spark, "spark_dates": dates[-120:], "avg50": avg50, "avg200": avg200, "wspark": wspark, "wdates": wdates, "wavg50": wavg50, "wavg200": wavg200, "low2y": low2y,
            "chg30": p / c[-31] - 1, "chg7": p / c[-8] - 1,
            "bt_period": per, "bt_bottom_up90": S["Bottoming"].get("up90"), "bt_all_up90": S["All days"].get("up90"),
            "bt_tool": st["tool_growth"], "bt_hold": st["hold_growth"], "bt_tool_dd": st["tool_drawdown"], "bt_hold_dd": st["hold_drawdown"],
        })
    phases = {a["phase"] for a in out if a["light"]}
    COL = {"Falling": "red", "Overheated": "red", "Bottoming": "amber", "Consolidating": "amber", "Rising": "green"}
    WHY = {"Falling": "danger, still falling", "Overheated": "danger, overheated", "Bottoming": "caution, a possible bottom",
           "Consolidating": "caution, moving sideways", "Rising": "favourable, uptrend"}
    lead = (f"All lights on {COL[next(iter(phases))]}: {WHY[next(iter(phases))]}." if len(phases) == 1 else
            "Mixed signals: " + ", ".join(f"{a['name']} {a['phase']}" for a in out if a["light"]) + ".")
    btc = out[0]
    note = (f"Crypto mood is {fng_word(fng_now).lower()} ({fng_now}), "
            f"Bitcoin's RSI is {btc['rsi']:.0f} ({btc['rsi_word']}) and it trades "
            f"{abs(btc['from_ath'])*100:.0f}% below its record. "
            + (f"It is still {(btc['price']/btc['realized']-1)*100:.0f}% above its average-cost line of ${btc['realized']:,.0f}. " if btc['realized'] else "")
            + ("The US dollar is strong, a headwind for crypto and gold." if dollar_strong else "The US dollar is weak, a tailwind for crypto and gold."))
    import base64, csv as _csv
    lp = os.path.join(HERE, "logos.json")  # coin icons supplied by the owner, as data URIs
    logos = json.load(open(lp)) if os.path.exists(lp) else {}
    dol = [float(r["DTWEXBGS"]) for r in _csv.DictReader(open(B.D + "dollar.csv")) if r.get("DTWEXBGS") not in (None, "", ".")]
    dollar_val, dollar_avg = dol[-1], sum(dol[-200:]) / 200
    data = {"logos": logos, "dollar_val": dollar_val, "dollar_avg": dollar_avg, "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "data_date": out[0]["date"],
            "fng": fng_now, "fng_word": fng_word(fng_now), "fng_week": fng_week, "dollar_strong": dollar_strong,
            "lead": lead, "note": note, "assets": out}
    data["fx"], data["fx_date"] = fx_rates()
    tpl = open(os.path.join(HERE, "template.html")).read()
    blob = json.dumps(data).replace("</", "<\\/")
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    open(os.path.join(HERE, "dist", "index.html"), "w").write(tpl.replace("/*DATA*/null", blob))
    json.dump(data, open(os.path.join(HERE, "dist", "data.json"), "w"), indent=1)
    print(note)
    for a in out:
        print(a["name"], a["phase"], "since", a["since"], "S", [round(x) for x in a["support_d"]], "R", [round(x) for x in a["resist_d"]], "wS", [round(x) for x in a["support_w"]], "wR", [round(x) for x in a["resist_w"]])

if __name__ == "__main__":
    main()
