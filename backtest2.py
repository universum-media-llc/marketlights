"""Main Light backtest v2: Falling-rule variants on Bitcoin, then the same rules on ETH, SOL and gold (PAX Gold).

Falling variants are declared here before running:
  base      : close < 200d avg and 50d avg < 200d avg
  breakdown : base AND a new 90-day closing low was made in the last 20 days
  dollar    : base AND US dollar index (FRED DTWEXBGS) above its own 200-day average
  either    : base AND (breakdown OR dollar)
A day that fails the Falling test falls through to Consolidating.
Inputs an asset lacks (no MVRV for SOL/gold; crypto fear & greed not used for gold) are skipped;
then Bottoming uses RSI <= 30 and Overheated RSI >= 80 on their own.
"""
import csv, json, os, sys

D = os.environ.get("BT_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data") + "/")
PHASES = ["Falling", "Bottoming", "Consolidating", "Rising", "Overheated"]

def load_cm(f):
    price, mvrv = {}, {}
    for r in csv.DictReader(open(D + f)):
        d = r["time"][:10]
        if r.get("PriceUSD"):
            price[d] = float(r["PriceUSD"])
        if r.get("CapMVRVCur"):
            mvrv[d] = float(r["CapMVRVCur"])
    return price, mvrv

FNG = {}
for line in open(D + "fng.csv"):
    p = line.strip().split(",")
    if len(p) == 3 and p[1].isdigit():
        dd, mm, yy = p[0].split("-")
        FNG[f"{yy}-{mm}-{dd}"] = int(p[1])

# US dollar index, forward-filled to every calendar day, with its 200-observation average
dol = []
for r in csv.DictReader(open(D + "dollar.csv")):
    v = r.get("DTWEXBGS")
    if v and v != ".":
        dol.append((r["observation_date"], float(v)))
DOLLAR_STRONG = {}
for i in range(199, len(dol)):
    avg = sum(v for _, v in dol[i - 199:i + 1]) / 200
    DOLLAR_STRONG[dol[i][0]] = dol[i][1] > avg

def dollar_strong(d, cache={}):
    # last known value on or before d
    if d in DOLLAR_STRONG:
        cache["last"] = DOLLAR_STRONG[d]
        return DOLLAR_STRONG[d]
    return cache.get("last")

def run(price, mvrv, use_fng, start, variant):
    dates = sorted(price); closes = [price[d] for d in dates]; n = len(dates)
    def sma(i, k):
        return None if i + 1 < k else sum(closes[i - k + 1:i + 1]) / k
    rsi = [None] * n; g = l = 0.0
    for i in range(1, n):
        ch = closes[i] - closes[i - 1]; gg, ll = max(ch, 0), max(-ch, 0)
        if i <= 14:
            g += gg; l += ll
            if i == 14:
                g /= 14; l /= 14; rsi[i] = 100 - 100 / (1 + g / l) if l else 100
        else:
            g = (g * 13 + gg) / 14; l = (l * 13 + ll) / 14
            rsi[i] = 100 - 100 / (1 + g / l) if l else 100
    newlow = [False] * n  # new 90-day closing low today
    for i in range(90, n):
        newlow[i] = closes[i] < min(closes[i - 90:i])
    dstrong = {}
    last = None
    for d in dates:
        v = DOLLAR_STRONG.get(d)
        if v is not None:
            last = v
        dstrong[d] = last

    def raw(i):
        d = dates[i]; c, s50, s200 = closes[i], sma(i, 50), sma(i, 200)
        if s200 is None or rsi[i] is None:
            return None
        f = FNG.get(d) if use_fng else None
        m = mvrv.get(d); r = rsi[i]
        hot = (m is not None and m >= 2.8) or c > 2.0 * s200 or (f >= 80 and r >= 75 if f is not None else r >= 80)
        if c > s200 and hot:
            return "Overheated"
        cold = (m is not None and m <= 1.0) or (f <= 20 and r <= 35 if f is not None else r <= 30)
        if c < s200 and cold:
            return "Bottoming"
        if c > s200 and s50 > s200 and c > s50:
            return "Rising"
        if c < s200 and s50 < s200:
            brk = any(newlow[max(0, i - 19):i + 1])
            dol_ = bool(dstrong.get(d))
            ok = {"base": True, "breakdown": brk, "dollar": dol_, "either": brk or dol_}[variant]
            if ok:
                return "Falling"
        return "Consolidating"

    phase = [None] * n; cur = cand = None; cnt = 0
    for i in range(n):
        p = raw(i)
        if p is None:
            continue
        if cur is None:
            cur = p
        elif p != cur:
            if p == cand:
                cnt += 1
            else:
                cand, cnt = p, 1
            if cnt >= 3:
                cur, cand, cnt = p, None, 0
        else:
            cand, cnt = None, 0
        phase[i] = cur

    start = max(start, next(d for i, d in enumerate(dates) if phase[i] is not None))
    i0 = dates.index(start); idx = list(range(i0, n))
    fwd = lambda i, k: closes[i + k] / closes[i] - 1 if i + k < n else None
    def stats(sel):
        out = {}
        for ph in PHASES + ["All days"]:
            rows = sel if ph == "All days" else [i for i in sel if phase[i] == ph]
            o = {"days": len(rows)}
            for k in (30, 90):
                v = [fwd(i, k) for i in rows if fwd(i, k) is not None]
                if v:
                    o[f"avg{k}"] = sum(v) / len(v); o[f"up{k}"] = sum(x > 0 for x in v) / len(v)
            out[ph] = o
        return out
    def strat(sel):
        eq = pk = bh = bpk = 1.0; mdd = bmdd = 0.0
        for i in sel[:-1]:
            r = closes[i + 1] / closes[i] - 1
            if phase[i] not in ("Falling", "Overheated"):
                eq *= 1 + r
            bh *= 1 + r
            pk = max(pk, eq); mdd = min(mdd, eq / pk - 1); bpk = max(bpk, bh); bmdd = min(bmdd, bh / bpk - 1)
        return {"tool_growth": eq, "tool_drawdown": mdd, "hold_growth": bh, "hold_drawdown": bmdd}
    first = [i for i in idx if dates[i] <= "2022-12-31"]; second = [i for i in idx if dates[i] >= "2023-01-01"]
    periods = [(f"{dates[i0][:4]}–2026", idx)]
    if first:
        periods += [(f"{dates[i0][:4]}–2022", first), ("2023–2026", second)]
    res = {"periods": {p: {"stats": stats(s), "strategy": strat(s)} for p, s in periods},
           "latest": {"date": dates[-1], "price": closes[-1], "phase": phase[-1], "rsi": rsi[-1],
                      "realized_price": (closes[-1] / mvrv[dates[-1]]) if dates[-1] in mvrv else None},
           "series": [{"date": dates[i], "price": round(closes[i], 4), "phase": phase[i],
                       "realized_price": round(closes[i] / mvrv[dates[i]], 4) if dates[i] in mvrv else None} for i in idx]}
    return res

def pct(x):
    return "   -  " if x is None else f"{x*100:+6.1f}%"

if __name__ == "__main__":
    btc = load_cm("cm_btc.csv")
    allres = {}
    print("=== Bitcoin: Falling variants ===")
    for v in ("base", "breakdown", "dollar", "either"):
        r = run(*btc, True, "2018-01-01", v)
        allres[("BTC", v)] = r
        for per, o in r["periods"].items():
            f, a, s = o["stats"]["Falling"], o["stats"]["All days"], o["strategy"]
            print(f"{v:9s} {per:10s} Falling days={f['days']:4d} avg90={pct(f.get('avg90'))} up90={pct(f.get('up90'))} | all up90={pct(a['up90'])} | tool {s['tool_growth']:.2f}x dd={pct(s['tool_drawdown'])}  hold {s['hold_growth']:.2f}x dd={pct(s['hold_drawdown'])}")
    json.dump({f"{k[0]}|{k[1]}": v for k, v in allres.items()}, open("/home/claude/bt/variants_btc.json", "w"))

    print("\n=== Other assets ===")
    assets = {"ETH": (load_cm("cm_eth.csv"), True, "2018-01-01"),
              "SOL": (load_cm("cm_sol.csv"), True, "2021-01-01"),
              "GOLD": (load_cm("cm_paxg.csv"), False, "2020-09-01")}
    for a, (pm, f, st) in assets.items():
        for v in ("base", "dollar"):
            r = run(*pm, f, st, v)
            allres[(a, v)] = r
            for per, o in r["periods"].items():
                S, s = o["stats"], o["strategy"]
                line = " ".join(f"{ph[:4]}:{S[ph]['days']}d/{pct(S[ph].get('avg90'))}/{pct(S[ph].get('up90'))}" for ph in PHASES)
                print(f"{a:4s} {v:6s} {per:10s} {line} | all {pct(S['All days'].get('avg90'))}/{pct(S['All days'].get('up90'))} | tool {s['tool_growth']:.2f}x dd={pct(s['tool_drawdown'])} hold {s['hold_growth']:.2f}x dd={pct(s['hold_drawdown'])}")
        print(a, "latest", allres[(a, 'dollar')]["latest"])
    print("BTC latest", allres[("BTC", "dollar")]["latest"])
    json.dump({f"{k[0]}|{k[1]}": v for k, v in allres.items()}, open("/home/claude/bt/variants_all.json", "w"))

    # ---------- export for the dashboard (adopted rule: "dollar") ----------
    CODE = open(__file__).read()
    META = [{"label": "backtest2.py", "value": CODE, "type": "code", "lang": "python"},
            {"label": "Inputs", "value": "Coin Metrics community API (PriceUSD, CapMVRVCur for btc, eth, sol, paxg), Alternative.me Fear & Greed history, FRED DTWEXBGS (US dollar index)"}]
    os.makedirs("/home/claude/bt/out2", exist_ok=True)
    def dump(name, rows):
        json.dump({"rows": rows, "meta": META}, open(f"/home/claude/bt/out2/{name}.json", "w"))
    B = allres[("BTC", "dollar")]
    dump("btc_daily", B["series"])
    score, strat = [], []
    for per, o in B["periods"].items():
        for ph in PHASES + ["All days"]:
            s = o["stats"][ph]
            score.append({"key": f"{per}|{ph}", "period": per, "phase": ph, "days": s["days"],
                          "avg30": s.get("avg30"), "up30": s.get("up30"), "avg90": s.get("avg90"), "up90": s.get("up90")})
        strat.append({"period": per, **o["strategy"]})
    dump("scorecard", score); dump("strategy", strat)
    dump("latest", [B["latest"]])
    labels = {"base": "Below both averages (first test)", "breakdown": "+ new 90-day low in last 20 days",
              "dollar": "+ strong US dollar (adopted)", "either": "+ new low or strong dollar"}
    rules = []
    for v in ("base", "breakdown", "dollar", "either"):
        P = allres[("BTC", v)]["periods"]
        full = P["2018–2026"]
        rules.append({"variant": labels[v], "falling_days": full["stats"]["Falling"]["days"],
                      "falling_up90": full["stats"]["Falling"].get("up90"),
                      "falling_up90_2018_2022": P["2018–2022"]["stats"]["Falling"].get("up90"),
                      "falling_up90_2023_2026": P["2023–2026"]["stats"]["Falling"].get("up90"),
                      "tool_growth": full["strategy"]["tool_growth"], "tool_drawdown": full["strategy"]["tool_drawdown"],
                      "hold_growth": full["strategy"]["hold_growth"], "hold_drawdown": full["strategy"]["hold_drawdown"]})
    dump("rules_btc", rules)
    names = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "GOLD": "Gold (PAX Gold)"}
    arows = []
    for a in ("BTC", "ETH", "SOL", "GOLD"):
        R = allres[(a, "dollar")]; per = next(iter(R["periods"])); o = R["periods"][per]; S = o["stats"]
        arows.append({"asset": names[a], "period": per, "today": R["latest"]["phase"], "price": R["latest"]["price"],
                      "bottoming_up90": S["Bottoming"].get("up90"), "all_up90": S["All days"].get("up90"),
                      "falling_up90": S["Falling"].get("up90"), **o["strategy"]})
    dump("assets", arows)
    print("exported", os.listdir("/home/claude/bt/out2"))
