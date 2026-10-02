"""Build the XAU/USD HOD/LOD backtest workbook (SYNTHETIC / FAKE predictions on real OANDA OHLC).

Real data: OANDA XAUUSD daily OHLC (three TradingView exports, merged, de-duplicated).
Synthetic: every predicted HOD / LOD band. Hit/miss days are drawn to land a ~94% dual hit rate.

Rules applied to every row:
  * Each predicted band is 0.1% thick:      Pred High = Pred Low x 1.001
  * Error% = 0 if the actual high/low is inside the band, else the distance to the
    nearest band edge divided by the actual high/low.
  * HIT if Error% <= 0.05% (tolerance / margin).
"""
import copy
import csv
import datetime as dt
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font

UP = Path("/root/.claude/uploads/f6db368e-1529-5ed2-8f87-ee09c86d6424")
SOURCES = [  # priority order for overlapping bars (all overlaps were verified identical)
    UP / "6ba52105-OANDA_XAUUSD_1D.xlsx",
    UP / "8ee3dada-OANDA_XAUUSD_1D.csv",
    UP / "5455b121-OANDA_XAUUSD_1D.xlsx",
]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("GOLD_XAUUSD_Backtest_FAKE_DATA.xlsx")

BAND = 0.001      # 0.1% band thickness
TOL = 0.0005      # 0.05% margin
SAFE = 0.000006   # keep errors away from the 0.05% edge so the 3-dp display never contradicts HIT/MISS
SEED = 20261002

# Target miss structure -> dual ~94.0%, either ~99.8%
BOTH_MISS = 10
HOD_ONLY_MISS = 147
LOD_ONLY_MISS = 153

FAKE_NOTE = "FAKE DATA — SYNTHETIC BACKTEST. Predicted HOD/LOD levels are generated, not produced by a real model. OHLC prices are real OANDA XAU/USD data."


def load_rows():
    data = {}
    for src in SOURCES:
        if src.suffix == ".csv":
            rows = list(csv.reader(open(src)))[1:]
        else:
            ws = openpyxl.load_workbook(src, read_only=True).worksheets[0]
            rows = [r[0].split(",") for r in ws.iter_rows(values_only=True)][1:]
        for r in rows:
            if not r or not r[0]:
                continue
            t = int(float(r[0]))
            data.setdefault(t, tuple(float(z) for z in r[1:5]))
    out = []
    for t in sorted(data):
        # OANDA daily bar opens 17:00 New York (21:00/22:00 UTC) the evening before the trading date
        day = (dt.datetime.utcfromtimestamp(t) + dt.timedelta(hours=3)).date()
        out.append((day, *data[t]))
    return out


def realized_vol(closes, i, n=20):
    if i < n:
        return None
    rets = [math.log(closes[k] / closes[k - 1]) for k in range(i - n + 1, i + 1)]
    return statistics.stdev(rets) * math.sqrt(252)


def err_of(actual, lo, hi):
    if actual < lo:
        return (lo - actual) / actual
    if actual > hi:
        return (actual - hi) / actual
    return 0.0


def make_band(rng, actual, hit, side):
    """Return (pred_high, pred_low) for one side. side = +1 for HOD, -1 for LOD."""
    while True:
        if hit:
            r = rng.random()
            if r < 0.46:  # actual inside the band
                pos = rng.uniform(0.02, 0.98)
                lo = actual / (1 + BAND * pos)
            else:  # just outside the band, within tolerance
                e = rng.triangular(0.0, TOL - SAFE, 0.00012)
                above = rng.random() < 0.5  # actual above band (band under-predicted) or below
                lo = actual * (1 - e) / (1 + BAND) if above else actual * (1 + e)
        else:
            e = TOL + SAFE + rng.expovariate(1 / 0.0011)
            e = min(e, 0.009)
            # misses lean toward under-calling the extreme (actual high above band / actual low below band)
            beyond = rng.random() < 0.72
            if side > 0:
                lo = actual * (1 - e) / (1 + BAND) if beyond else actual * (1 + e)
            else:
                lo = actual * (1 + e) if beyond else actual * (1 - e) / (1 + BAND)
        lo = round(lo, 2)
        hi = round(lo * (1 + BAND), 2)
        e = err_of(actual, lo, hi)
        if hit and e <= TOL - SAFE:
            return hi, lo
        if not hit and e >= TOL + SAFE:
            return hi, lo


def choose_miss_days(rng, rows, vols):
    n = len(rows)
    # weight: wider-than-usual days and high-vol regimes miss a bit more; plus slow-moving yearly drift
    year_factor = {y: rng.uniform(0.75, 1.3) for y in {r[0].year for r in rows}}
    weights = []
    for i, (day, o, h, l, c) in enumerate(rows):
        prev = rows[max(0, i - 20):i] or [rows[i]]
        avg_rng = sum((r[2] - r[3]) / r[3] for r in prev) / len(prev)
        rel = ((h - l) / l) / avg_rng if avg_rng else 1
        w = year_factor[day.year] * (0.6 + 0.5 * min(rel, 2.5))
        weights.append(w)
    idx = list(range(n))

    def draw(k, exclude):
        pool = [i for i in idx if i not in exclude]
        chosen = set()
        while len(chosen) < k:
            i = rng.choices(pool, weights=[weights[j] for j in pool])[0]
            chosen.add(i)
        return chosen

    both = draw(BOTH_MISS, set())
    # keep "both missed" days isolated so the longest both-miss streak stays 1
    while any(i + 1 in both for i in both):
        both = draw(BOTH_MISS, set())
    hod = draw(HOD_ONLY_MISS, both)
    lod = draw(LOD_ONLY_MISS, both | hod)
    return hod | both, lod | both


def build_signals(rows):
    rng = random.Random(SEED)
    closes = [r[4] for r in rows]
    vols = [realized_vol(closes, i) for i in range(len(rows))]
    hod_miss, lod_miss = choose_miss_days(rng, rows, vols)
    sig = []
    for i, (day, o, h, l, c) in enumerate(rows):
        for _ in range(500):
            hh, hl = make_band(rng, h, i not in hod_miss, +1)
            lh, ll = make_band(rng, l, i not in lod_miss, -1)
            if hl > lh:  # HOD band must sit above the LOD band
                break
        else:
            raise RuntimeError(f"could not separate bands on {day}")
        sig.append((hh, hl, lh, ll))
    return sig, vols



# ---------------------------------------------------------------- workbook (styled from the NQ template)
TEMPLATE = UP / "2cff4e19-GrpVol_Backtest_Download.xlsx"
RED = "FFE03C31"


def fake_footer(ws, row, last_col, proto):
    """Bottom-of-sheet FAKE DATA note, in the template's palette."""
    c = ws.cell(row=row, column=2, value=FAKE_NOTE)
    c._style = copy.copy(proto._style)
    c.font = Font(name="Calibri", size=9, bold=True, color=RED)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_col)
    ws.row_dimensions[row].height = 24


def longest(flags):
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def main():
    rows = load_rows()
    sig, vols = build_signals(rows)
    n = len(rows)
    first, last = rows[0][0], rows[-1][0]
    years_span = (last - first).days / 365.25

    hod_err = [err_of(r[2], s[1], s[0]) for r, s in zip(rows, sig)]
    lod_err = [err_of(r[3], s[3], s[2]) for r, s in zip(rows, sig)]
    hod_hit = [e <= TOL for e in hod_err]
    lod_hit = [e <= TOL for e in lod_err]
    dual = [a and b for a, b in zip(hod_hit, lod_hit)]
    either = [a or b for a, b in zip(hod_hit, lod_hit)]
    dual_rate = sum(dual) / n

    wb = openpyxl.load_workbook(TEMPLATE)
    M, L, S = wb["Backtest Summary"], wb["Daily Signal Log"], wb["Statistical Analysis"]

    # ================================================================ Daily Signal Log
    FIRST = 5
    LAST = FIRST + n - 1
    tpl_last = L.max_row
    # style prototypes keyed by (row parity, HOD hit, LOD hit)
    protos = {}
    for r in range(FIRST, tpl_last + 1):
        key = (r % 2, L.cell(r, 11).value == "HIT", L.cell(r, 12).value == "HIT")
        if key not in protos:
            protos[key] = [copy.copy(L.cell(r, c)._style) for c in range(1, 16)]
        if len(protos) == 8:
            break
    assert len(protos) == 8

    L["B1"] = "  XAU/USD Gold — HOD/LOD Daily Signal Log  ·  FAKE DATA"
    L["B2"] = (f"Security: OANDA:XAUUSD  |  Period: {first:%d-%b-%Y} to {last:%d-%b-%Y}  |  Band: 0.1%  |  "
               f"Tolerance: ±0.05%  |  Total Days: {n:,}  |  Dual Hit Rate: {dual_rate:.1%}")
    for col, lab in zip("CDEF", ["XAU Open", "XAU High", "XAU Low", "XAU Close"]):
        L[f"{col}4"] = lab

    rng_ = lambda col: f"'Daily Signal Log'!${col}${FIRST}:${col}${LAST}"
    for i, ((day, o, h, l, c), (hh, hl, lh, ll)) in enumerate(zip(rows, sig)):
        r = FIRST + i
        style = protos[(r % 2, hod_hit[i], lod_hit[i])]
        for col in range(1, 16):
            L.cell(r, col)._style = copy.copy(style[col - 1])
        for col, v in zip(range(2, 11), [f"{day:%Y-%m-%d}", o, h, l, c, hh, hl, lh, ll]):
            L.cell(r, col).value = v
        L[f"N{r}"] = f"=IF(D{r}<H{r},(H{r}-D{r})/D{r},IF(D{r}>G{r},(D{r}-G{r})/D{r},0))"
        L[f"O{r}"] = f"=IF(E{r}<J{r},(J{r}-E{r})/E{r},IF(E{r}>I{r},(E{r}-I{r})/E{r},0))"
        L[f"K{r}"] = f'=IF(N{r}<={TOL},"HIT","MISS")'
        L[f"L{r}"] = f'=IF(O{r}<={TOL},"HIT","MISS")'
        L[f"M{r}"] = (f'=IF(AND(K{r}="HIT",L{r}="HIT"),"HOD ✓ | LOD ✓",'
                      f'IF(K{r}="HIT","HOD ✓",IF(L{r}="HIT","LOD ✓","MISS")))')
        L[f"N{r}"].number_format = L[f"O{r}"].number_format = "0.000%"
    if tpl_last > LAST:
        L.delete_rows(LAST + 1, tpl_last - LAST)
    fake_footer(L, LAST + 2, 15, L["A1"])

    # ================================================================ Statistical Analysis
    K, Lc, N, O, B = rng_("K"), rng_("L"), rng_("N"), rng_("O"), rng_("B")
    S["B1"] = "XAU/USD HOD/LOD Signal — Statistical Analysis  ·  FAKE DATA"
    for col in "CDEFG":
        S[f"{col}5"] = f"=COUNTA({B})"
    S["C6"] = f'=COUNTIF({K},"HIT")'
    S["D6"] = f'=COUNTIF({Lc},"HIT")'
    S["E6"] = f'=COUNTIFS({K},"HIT",{Lc},"HIT")'
    S["F6"] = "=C6+D6-E6"
    S["G6"] = f'=COUNTIFS({K},"MISS",{Lc},"MISS")'
    for col in "CDEFG":
        S[f"{col}7"] = f"={col}6/{col}5"
        S[f"{col}7"].number_format = "0.00%"
    S["C8"], S["D8"] = f"=AVERAGE({N})", f"=AVERAGE({O})"
    S["C9"], S["D9"] = f"=MEDIAN({N})", f"=MEDIAN({O})"
    for a in ("C8", "D8", "C9", "D9"):
        S[a].number_format = "0.0000%"

    S["C12"] = longest(dual)
    S["C13"] = longest(either)
    S["C14"] = longest([not e for e in either])

    months = defaultdict(lambda: [0, 0])
    for (day, *_), d in zip(rows, dual):
        months[f"{day:%Y-%m}"][0] += 1
        months[f"{day:%Y-%m}"][1] += d
    mrate = {k: v[1] / v[0] for k, v in months.items() if v[0] >= 10}  # skip the partial first month
    best = min(mrate, key=lambda k: (-mrate[k], k))
    worst = min(mrate, key=lambda k: (mrate[k], k))
    S["C17"], S["D17"] = best, mrate[best]
    S["C18"], S["D18"] = worst, mrate[worst]
    S["D17"].number_format = S["D18"].number_format = "0.0%"
    S["C19"] = sum(v >= 0.95 for v in mrate.values())
    S["C20"] = sum(v < 0.80 for v in mrate.values())

    for k in range(5):  # Monday..Friday ; WEEKDAY(): Monday = 2
        r = 24 + k
        S[f"D{r}"] = f"=SUMPRODUCT(--(WEEKDAY({B})={k + 2}))"
        S[f"C{r}"] = f'=SUMPRODUCT((WEEKDAY({B})={k + 2})*({K}="HIT")*({Lc}="HIT"))/D{r}'
        S[f"C{r}"].number_format = "0.00%"

    # realized-vol quintiles (20-day close-to-close vol, first 20 sessions excluded)
    vi = sorted((v, i) for i, v in enumerate(vols) if v is not None)
    q = len(vi)
    for k in range(5):
        chunk = vi[k * q // 5:(k + 1) * q // 5]
        S[f"C{32 + k}"] = sum(dual[i] for _, i in chunk) / len(chunk)
        S[f"C{32 + k}"].number_format = "0.00%"
    fake_footer(S, 38, 7, S["B37"])

    # ================================================================ Backtest Summary
    M["B4"] = "XAU/USD GOLD  ·  HOD / LOD PREDICTIVE SIGNAL  ·  BACKTEST ANALYSIS  ·  FAKE DATA"
    M["B5"] = (f"Backtest Period:  {first:%d %b %Y}  →  {last:%d %b %Y}     |     Total Trading Days:  {n:,}"
               f"     |     Band:  0.1%     |     Tolerance:  ±0.05%")
    SA = "'Statistical Analysis'!"
    for col, src, fmt in [("B", "E", "0.0%"), ("C", "C", "0.0%"), ("D", "D", "0.0%"),
                          ("E", "F", "0.0%"), ("F", "G", "0.00%")]:
        M[f"{col}9"] = f"={SA}{src}7"
        M[f"{col}9"].number_format = fmt
    M["G9"] = f"{years_span:.1f} yrs"
    M["B10"] = f'=TEXT({SA}E6,"#,##0")&" / "&TEXT({SA}E5,"#,##0")&" days"'
    M["C10"] = f'=TEXT({SA}C6,"#,##0")&" days predicted"'
    M["D10"] = f'=TEXT({SA}D6,"#,##0")&" days predicted"'
    M["E10"] = f'=TEXT({SA}F6,"#,##0")&" days (HOD or LOD)"'
    M["F10"] = f'=TEXT({SA}G6,"#,##0")&" miss days"'
    M["G10"] = f"{first.year} – {last.year}"

    # annual table: template rows 17..41 (25 years); gold has fewer -> fill, then drop spare rows
    yrs = sorted({r[0].year for r in rows})
    for k, y in enumerate(yrs):
        r = 17 + k
        yr = f"(YEAR({B})=$B{r})"
        M[f"B{r}"] = y
        M[f"C{r}"] = f"=SUMPRODUCT(--{yr})"
        M[f"D{r}"] = f'=SUMPRODUCT({yr}*({K}="HIT"))'
        M[f"E{r}"] = f'=SUMPRODUCT({yr}*({Lc}="HIT"))'
        M[f"F{r}"] = f'=SUMPRODUCT({yr}*({K}="HIT")*({Lc}="HIT"))'
        M[f"G{r}"] = f"=D{r}+E{r}-F{r}"
        for col, num in zip("HIJK", "DEFG"):
            M[f"{col}{r}"] = f"={num}{r}/C{r}"
            M[f"{col}{r}"].number_format = "0.0%"
    spare = 25 - len(yrs)
    if spare:
        cut = 17 + len(yrs)
        heights = {r: M.row_dimensions[r].height for r in range(cut, M.max_row + 1)}
        below = [m for m in M.merged_cells.ranges if m.min_row >= cut]
        coords = [(m.min_row, m.min_col, m.max_row, m.max_col) for m in below]
        for m in list(below):
            M.unmerge_cells(str(m))
        M.delete_rows(cut, spare)
        for (r1, c1, r2, c2) in coords:
            M.merge_cells(start_row=r1 - spare, start_column=c1, end_row=r2 - spare, end_column=c2)
        for r, h in heights.items():
            if r - spare >= cut:
                M.row_dimensions[r - spare].height = h
    sh = spare
    meth = {
        45: ("Security", "OANDA:XAUUSD  (Gold Spot / U.S. Dollar)"),
        46: ("Signal Type", "Daily HOD / LOD Predictive Model — Daily Level Forecasting"),
        47: ("Prediction Window", "Pre-session signal generated before the 17:00 ET daily open"),
        48: ("Hit Condition", "Actual High/Low inside the 0.1% predicted band, or within ±0.05% of its nearest edge"),
        49: ("Tolerance Band", "±0.05% (fixed) — Err% = 0 inside band, else |Actual − nearest band edge| ÷ Actual"),
        50: ("Data Source", "TradingView · OANDA:XAUUSD · OHLC Daily"),
        51: ("Backtest Engine", "Synthetic signal generator"),
        52: ("Predicted Levels", "SYNTHETIC — generated for demonstration, not produced by a real model"),
        53: ("Slippage Model", "Not applied — signal is level-based, not execution-based"),
        54: ("Run Date", f"{dt.date(2026, 10, 2):%d %b %Y}  16:00 ET"),
    }
    for r, (a, b) in meth.items():
        M[f"B{r - sh}"], M[f"C{r - sh}"] = a, b
    fake_footer(M, 59 - sh, 11, M[f"B{57 - sh}"])

    wb.properties.title = "XAU/USD HOD/LOD Backtest — FAKE DATA"
    wb.properties.description = FAKE_NOTE
    wb.save(OUT)

    print(f"saved {OUT}")
    print(f"days={n} hod={sum(hod_hit)} lod={sum(lod_hit)} dual={sum(dual)} either={sum(either)} "
          f"dual_rate={dual_rate:.4%}")


if __name__ == "__main__":
    main()
