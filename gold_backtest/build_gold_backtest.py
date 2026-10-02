"""Build the XAU/USD HOD/LOD backtest workbook (SYNTHETIC / FAKE predictions on real OANDA OHLC).

Real data: OANDA XAUUSD daily OHLC (three TradingView exports, merged, de-duplicated).
Synthetic: every predicted HOD / LOD band. Hit/miss days are drawn to land a ~94% dual hit rate.

Rules applied to every row:
  * Each predicted band is 0.1% thick:      Pred High = Pred Low x 1.001
  * Error% = 0 if the actual high/low is inside the band, else the distance to the
    nearest band edge divided by the actual high/low.
  * HIT if Error% <= 0.05% (tolerance / margin).
"""
import csv
import datetime as dt
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

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


# ---------------------------------------------------------------- styles
NAVY = "1F2A44"
GOLD = "B8860B"
LIGHT = "F3F0E6"
F_TITLE = Font(name="Arial", size=16, bold=True, color="FFFFFF")
F_SUB = Font(name="Arial", size=10, color="FFFFFF")
F_HEAD = Font(name="Arial", size=10, bold=True, color="FFFFFF")
F_BODY = Font(name="Arial", size=10)
F_BOLD = Font(name="Arial", size=10, bold=True)
F_KPI = Font(name="Arial", size=20, bold=True, color=NAVY)
F_KPI_SUB = Font(name="Arial", size=9, color="555555")
F_SECTION = Font(name="Arial", size=12, bold=True, color=NAVY)
F_FAKE = Font(name="Arial", size=11, bold=True, color="C00000")
F_DISC = Font(name="Arial", size=9, italic=True, color="555555")
FILL_NAVY = PatternFill("solid", fgColor=NAVY)
FILL_GOLD = PatternFill("solid", fgColor=GOLD)
FILL_LIGHT = PatternFill("solid", fgColor=LIGHT)
FILL_HIT = PatternFill("solid", fgColor="E2F0D9")
FILL_MISS = PatternFill("solid", fgColor="FBE2E2")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center")


def banner(ws, row, text, last_col, font=F_TITLE, fill=FILL_NAVY, height=30):
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=2, value=text)
    c.font, c.fill, c.alignment = font, fill, LEFT
    for col in range(2, last_col + 1):
        ws.cell(row=row, column=col).fill = fill
    ws.row_dimensions[row].height = height


def header_row(ws, row, labels, start_col=2):
    for j, lab in enumerate(labels):
        c = ws.cell(row=row, column=start_col + j, value=lab)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_NAVY, CENTER, BOX


def fake_footer(ws, row, last_col):
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=2, value=FAKE_NOTE)
    c.font, c.alignment = F_FAKE, Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30


def main():
    rows = load_rows()
    sig, vols = build_signals(rows)
    n = len(rows)
    first, last = rows[0][0], rows[-1][0]
    years_span = (last - first).days / 365.25

    # ---- Python-side truth (used for the non-formula stats and to cross-check formulas)
    hod_err = [err_of(r[2], s[1], s[0]) for r, s in zip(rows, sig)]
    lod_err = [err_of(r[3], s[3], s[2]) for r, s in zip(rows, sig)]
    hod_hit = [e <= TOL for e in hod_err]
    lod_hit = [e <= TOL for e in lod_err]
    dual = [a and b for a, b in zip(hod_hit, lod_hit)]
    either = [a or b for a, b in zip(hod_hit, lod_hit)]
    dual_rate = sum(dual) / n

    wb = openpyxl.Workbook()
    ws_sum = wb.active
    ws_sum.title = "Backtest Summary"
    ws_log = wb.create_sheet("Daily Signal Log")
    ws_st = wb.create_sheet("Statistical Analysis")
    for ws in (ws_sum, ws_log, ws_st):
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2

    # ================================================================ Daily Signal Log
    L = ws_log
    first_data = 6
    last_data = first_data + n - 1
    rng_ = lambda col: f"'Daily Signal Log'!${col}${first_data}:${col}${last_data}"
    banner(L, 1, "  XAU/USD Gold Spot — HOD/LOD Daily Signal Log  ·  FAKE DATA (SYNTHETIC)", 20)
    banner(
        L, 2,
        f"Security: OANDA:XAUUSD  |  Period: {first:%d-%b-%Y} to {last:%d-%b-%Y}  |  Band: 0.1%  |  "
        f"Tolerance: ±0.05%  |  Total Days: {n:,}  |  Dual Hit Rate: {dual_rate:.1%}",
        20, font=F_SUB, height=20,
    )
    L["B3"], L["C3"] = "Band Thickness", BAND
    L["E3"], L["F3"] = "Tolerance (±)", TOL
    for a in ("B3", "E3"):
        L[a].font = F_BOLD
    for a in ("C3", "F3"):
        L[a].font = Font(name="Arial", size=10, bold=True, color="0000FF")
        L[a].number_format = "0.00%"
        L[a].fill = PatternFill("solid", fgColor="FFFF00")
    L["H3"] = "Error% = 0 inside band, else distance to nearest band edge ÷ actual price. HIT when Error% ≤ Tolerance."
    L["H3"].font = F_DISC
    heads = ["Date", "Open", "High", "Low", "Close", "Pred HOD High", "Pred HOD Low",
             "Pred LOD High", "Pred LOD Low", "HOD Hit", "LOD Hit", "Result", "HOD Err%",
             "LOD Err%", "Log Return", "RVol 20D (ann.)", "Band Width%", "Year", "Weekday"]
    header_row(L, 5, heads)
    widths = [12, 11, 11, 11, 11, 13, 13, 13, 13, 9, 9, 15, 10, 10, 11, 14, 11, 7, 9]
    for j, w in enumerate(widths):
        L.column_dimensions[get_column_letter(2 + j)].width = w
    L.freeze_panes = "C6"

    for i, ((day, o, h, l, c), (hh, hl, lh, ll)) in enumerate(zip(rows, sig)):
        r = first_data + i
        vals = [day, o, h, l, c, hh, hl, lh, ll]
        for j, v in enumerate(vals):
            cell = L.cell(row=r, column=2 + j, value=v)
            cell.font = F_BODY
            cell.number_format = "yyyy-mm-dd" if j == 0 else "#,##0.000" if j < 5 else "#,##0.00"
        L[f"N{r}"] = f"=IF(D{r}<H{r},(H{r}-D{r})/D{r},IF(D{r}>G{r},(D{r}-G{r})/D{r},0))"
        L[f"O{r}"] = f"=IF(E{r}<J{r},(J{r}-E{r})/E{r},IF(E{r}>I{r},(E{r}-I{r})/E{r},0))"
        L[f"K{r}"] = f'=IF(N{r}<=$F$3,"HIT","MISS")'
        L[f"L{r}"] = f'=IF(O{r}<=$F$3,"HIT","MISS")'
        L[f"M{r}"] = (f'=IF(AND(K{r}="HIT",L{r}="HIT"),"HOD ✓ | LOD ✓",IF(K{r}="HIT","HOD ✓",'
                      f'IF(L{r}="HIT","LOD ✓","✗ MISS")))')
        if i > 0:
            L[f"P{r}"] = f"=LN(F{r}/F{r-1})"
        if i >= 20:
            L[f"Q{r}"] = f"=STDEV(P{r-19}:P{r})*SQRT(252)"
        L[f"R{r}"] = f"=(G{r}-H{r})/H{r}"
        L[f"S{r}"] = f"=YEAR(B{r})"
        L[f"T{r}"] = f"=WEEKDAY(B{r})"
        for col in "KLMNOPQRST":
            L[f"{col}{r}"].font = F_BODY
        for col in "NOR":
            L[f"{col}{r}"].number_format = "0.000%"
        L[f"P{r}"].number_format = "0.00%"
        L[f"Q{r}"].number_format = "0.0%"
        for col in "KL":
            L[f"{col}{r}"].alignment = CENTER
        if not dual[i]:
            for col in "KLM":
                L[f"{col}{r}"].fill = FILL_MISS
    fake_footer(L, last_data + 2, 20)

    # ================================================================ Statistical Analysis
    S = ws_st
    for col, w in zip("BCDEFG", [36, 14, 14, 14, 14, 12]):
        S.column_dimensions[col].width = w
    banner(S, 1, "XAU/USD HOD/LOD Signal — Statistical Analysis  ·  FAKE DATA (SYNTHETIC)", 7)
    S["B3"] = "▸  OVERALL HIT RATE SUMMARY"
    S["B3"].font = F_SECTION
    header_row(S, 4, ["Metric", "HOD", "LOD", "Dual (Both)", "Either (OR)", "Miss"])
    K, Lc, N, O = rng_("K"), rng_("L"), rng_("N"), rng_("O")
    S["B5"] = "Total Trading Days"
    for col in "CDEFG":
        S[f"{col}5"] = f"=COUNTA({rng_('B')})"
    S["B6"] = "Signal Hits"
    S["C6"] = f'=COUNTIF({K},"HIT")'
    S["D6"] = f'=COUNTIF({Lc},"HIT")'
    S["E6"] = f'=COUNTIFS({K},"HIT",{Lc},"HIT")'
    S["F6"] = f"=C6+D6-E6"
    S["G6"] = f'=COUNTIFS({K},"MISS",{Lc},"MISS")'
    S["B7"] = "Accuracy Rate"
    for col in "CDEFG":
        S[f"{col}7"] = f"={col}6/{col}5"
        S[f"{col}7"].number_format = "0.00%"
    S["B8"] = "Avg Prediction Error"
    S["C8"], S["D8"] = f"=AVERAGE({N})", f"=AVERAGE({O})"
    S["B9"] = "Median Prediction Error"
    S["C9"], S["D9"] = f"=MEDIAN({N})", f"=MEDIAN({O})"
    S["B10"] = "Avg Error on HIT days"
    S["C10"] = f'=AVERAGEIF({K},"HIT",{N})'
    S["D10"] = f'=AVERAGEIF({Lc},"HIT",{O})'
    S["B11"] = "Avg Error on MISS days"
    S["C11"] = f'=AVERAGEIF({K},"MISS",{N})'
    S["D11"] = f'=AVERAGEIF({Lc},"MISS",{O})'
    S["B12"] = "Days Actual Inside Band (0.000% err)"
    S["C12"] = f"=COUNTIF({N},0)"
    S["D12"] = f"=COUNTIF({O},0)"
    for r in range(8, 12):
        for col in "CD":
            S[f"{col}{r}"].number_format = "0.0000%"
        for col in "EFG":
            S[f"{col}{r}"] = "—"
    for r in range(5, 13):
        for col in "BCDEFG":
            S[f"{col}{r}"].font = F_BOLD if col == "B" else F_BODY
            S[f"{col}{r}"].border = BOX
            if col != "B":
                S[f"{col}{r}"].alignment = CENTER

    # streaks (computed from the log)
    def longest(flags):
        best = cur = 0
        for f in flags:
            cur = cur + 1 if f else 0
            best = max(best, cur)
        return best

    both_miss = [not e for e in either]
    S["B14"] = "▸  STREAK ANALYSIS"
    S["B14"].font = F_SECTION
    streaks = [("Longest Dual-Hit Winning Streak", longest(dual)),
               ("Longest Either-Hit Streak", longest(either)),
               ("Longest Miss Streak (Both missed)", longest(both_miss))]
    for k, (lab, v) in enumerate(streaks):
        S[f"B{15+k}"], S[f"C{15+k}"] = lab, v
        S[f"B{15+k}"].font, S[f"C{15+k}"].font = F_BOLD, F_BODY

    # monthly
    months = defaultdict(lambda: [0, 0])
    for (day, *_), d in zip(rows, dual):
        key = f"{day:%Y-%m}"
        months[key][0] += 1
        months[key][1] += d
    # ignore partial first month (< 10 sessions) for best/worst
    full = {k: v for k, v in months.items() if v[0] >= 10}
    mrate = {k: v[1] / v[0] for k, v in full.items()}
    best = max(mrate, key=lambda k: (mrate[k], k))
    worst = min(mrate, key=lambda k: (mrate[k], k))
    S["B19"] = "▸  MONTHLY DUAL HIT RATE ANALYSIS"
    S["B19"].font = F_SECTION
    S["B20"], S["C20"], S["D20"] = "Best Month (Dual Hit Rate)", best, mrate[best]
    S["B21"], S["C21"], S["D21"] = "Worst Month (Dual Hit Rate)", worst, mrate[worst]
    S["B22"], S["C22"] = "Months ≥ 95% Dual Hit Rate", sum(v >= 0.95 for v in mrate.values())
    S["B23"], S["C23"] = "Months < 85% Dual Hit Rate", sum(v < 0.85 for v in mrate.values())
    S["B24"], S["C24"] = "Months Analysed (≥10 sessions)", len(mrate)
    for r in range(20, 25):
        S[f"B{r}"].font = F_BOLD
    S["D20"].number_format = S["D21"].number_format = "0.0%"

    # day of week (formulas)
    S["B26"] = "▸  DAY-OF-WEEK DUAL HIT RATE"
    S["B26"].font = F_SECTION
    header_row(S, 27, ["Day", "Dual Hit Rate", "Sample Days"])
    B = rng_("B")
    for k, dname in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):
        r = 28 + k
        wd = k + 2  # WEEKDAY(): Sunday=1, Monday=2
        S[f"B{r}"] = dname
        S[f"D{r}"] = f"=COUNTIF({rng_('T')},{wd})"
        S[f"C{r}"] = f'=COUNTIFS({rng_("T")},{wd},{K},"HIT",{Lc},"HIT")/D{r}'
        S[f"C{r}"].number_format = "0.00%"
        for col in "BCD":
            S[f"{col}{r}"].border, S[f"{col}{r}"].font = BOX, F_BODY

    # vol quintiles (formulas on the RVol column)
    S["B34"] = "▸  VOLATILITY REGIME — DUAL HIT RATE BY 20D REALIZED VOL QUINTILE"
    S["B34"].font = F_SECTION
    header_row(S, 35, ["Vol Regime", "Dual Hit Rate", "Sample Days", "RVol From", "RVol To"])
    Q = rng_("Q")
    labels = ["Q1 (Low Vol)", "Q2", "Q3", "Q4", "Q5 (High Vol)"]
    for k, lab in enumerate(labels):
        r = 36 + k
        S[f"B{r}"] = lab
        S[f"E{r}"] = f"=PERCENTILE({Q},{k/5})" if k else f"=MIN({Q})"
        S[f"F{r}"] = f"=PERCENTILE({Q},{(k+1)/5})" if k < 4 else f"=MAX({Q})"
        hi_op = "<=" if k == 4 else "<"
        cond = f'{Q},">="&E{r},{Q},"{hi_op}"&F{r}'
        S[f"D{r}"] = f"=COUNTIFS({cond})"
        S[f"C{r}"] = f'=COUNTIFS({cond},{K},"HIT",{Lc},"HIT")/D{r}'
        S[f"C{r}"].number_format = "0.00%"
        S[f"E{r}"].number_format = S[f"F{r}"].number_format = "0.0%"
        for col in "BCDEF":
            S[f"{col}{r}"].border, S[f"{col}{r}"].font = BOX, F_BODY
    S["B41"] = "Quintiles exclude the first 20 sessions (insufficient history for 20D realized vol)."
    S["B41"].font = F_DISC

    # band-geometry check
    S["B43"] = "▸  BAND GEOMETRY CHECK"
    S["B43"].font = F_SECTION
    R = rng_("R")
    checks = [("Min Band Width (Pred High vs Pred Low)", f"=MIN({R})", "0.0000%"),
              ("Max Band Width", f"=MAX({R})", "0.0000%"),
              ("Avg Band Width", f"=AVERAGE({R})", "0.0000%"),
              ("Days HOD band above LOD band",
               f"=SUMPRODUCT(--({rng_('H')}>{rng_('I')}))", "#,##0"),
              ("Total Days", f"=COUNTA({B})", "#,##0")]
    for k, (lab, f, fmt) in enumerate(checks):
        S[f"B{44+k}"], S[f"C{44+k}"] = lab, f
        S[f"B{44+k}"].font, S[f"C{44+k}"].font = F_BOLD, F_BODY
        S[f"C{44+k}"].number_format = fmt
    fake_footer(S, 50, 7)

    # ================================================================ Backtest Summary
    M = ws_sum
    for col, w in zip("BCDEFGHIJK", [20, 18, 18, 22, 16, 16, 11, 11, 11, 12]):
        M.column_dimensions[col].width = w
    banner(M, 4, "XAU/USD GOLD  ·  HOD / LOD PREDICTIVE SIGNAL  ·  BACKTEST ANALYSIS  ·  FAKE DATA (SYNTHETIC)", 11, height=34)
    banner(
        M, 5,
        f"Backtest Period:  {first:%d %b %Y}  →  {last:%d %b %Y}     |     Total Trading Days:  {n:,}"
        f"     |     Band:  0.1%     |     Tolerance:  ±0.05%",
        11, font=F_SUB, height=20,
    )
    SA = "'Statistical Analysis'!"
    kpis = [
        ("DUAL HIT RATE", f"={SA}E7", "0.0%", f'=TEXT({SA}E6,"#,##0")&" / "&TEXT({SA}E5,"#,##0")&" days"'),
        ("HOD ACCURACY", f"={SA}C7", "0.0%", f'=TEXT({SA}C6,"#,##0")&" days predicted"'),
        ("LOD ACCURACY", f"={SA}D7", "0.0%", f'=TEXT({SA}D6,"#,##0")&" days predicted"'),
        ("OVERALL HIT RATE", f"={SA}F7", "0.0%", f'=TEXT({SA}F6,"#,##0")&" days (HOD or LOD)"'),
        ("MISS RATE", f"={SA}G7", "0.00%", f'=TEXT({SA}G6,"#,##0")&" miss days"'),
        ("BACKTEST YEARS", round(years_span, 1), '0.0" yrs"', f"{first.year} – {last.year}"),
    ]
    for j, (lab, f, fmt, sub) in enumerate(kpis):
        col = get_column_letter(2 + j)
        M[f"{col}8"] = lab
        M[f"{col}8"].font, M[f"{col}8"].fill, M[f"{col}8"].alignment = F_HEAD, FILL_GOLD, CENTER
        M[f"{col}9"] = f
        M[f"{col}9"].font, M[f"{col}9"].number_format, M[f"{col}9"].alignment = F_KPI, fmt, CENTER
        M[f"{col}10"] = sub
        M[f"{col}10"].font, M[f"{col}10"].alignment = F_KPI_SUB, CENTER
        for r in (8, 9, 10):
            M[f"{col}{r}"].border = BOX
            if r > 8:
                M[f"{col}{r}"].fill = FILL_LIGHT
    M.row_dimensions[9].height = 34

    M["B13"] = "▸  ANNUAL PERFORMANCE BREAKDOWN"
    M["B13"].font = F_SECTION
    header_row(M, 14, ["Year", "Days", "HOD Hits", "LOD Hits", "Dual Hits", "Either Hits",
                       "HOD Rate", "LOD Rate", "Dual Rate", "Overall Rate"])
    yrs = sorted({r[0].year for r in rows})
    for k, y in enumerate(yrs):
        r = 15 + k
        yr = f"{rng_('S')},$B{r}"
        M[f"B{r}"] = y
        M[f"C{r}"] = f"=COUNTIF({yr})"
        M[f"D{r}"] = f'=COUNTIFS({yr},{K},"HIT")'
        M[f"E{r}"] = f'=COUNTIFS({yr},{Lc},"HIT")'
        M[f"F{r}"] = f'=COUNTIFS({yr},{K},"HIT",{Lc},"HIT")'
        M[f"G{r}"] = f"=D{r}+E{r}-F{r}"
        for col, num in zip("HIJK", "DEFG"):
            M[f"{col}{r}"] = f"={num}{r}/$C{r}"
            M[f"{col}{r}"].number_format = "0.0%"
        for col in "BCDEFGHIJK":
            M[f"{col}{r}"].font, M[f"{col}{r}"].border, M[f"{col}{r}"].alignment = F_BODY, BOX, CENTER
            if k % 2:
                M[f"{col}{r}"].fill = FILL_LIGHT
    tot = 15 + len(yrs)
    M[f"B{tot}"] = "Total"
    for col in "CDEFG":
        M[f"{col}{tot}"] = f"=SUM({col}15:{col}{tot-1})"
    for col, num in zip("HIJK", "DEFG"):
        M[f"{col}{tot}"] = f"={num}{tot}/$C{tot}"
        M[f"{col}{tot}"].number_format = "0.0%"
    for col in "BCDEFGHIJK":
        M[f"{col}{tot}"].font, M[f"{col}{tot}"].border, M[f"{col}{tot}"].alignment = F_BOLD, BOX, CENTER

    mrow = tot + 3
    M[f"B{mrow}"] = "▸  STRATEGY METHODOLOGY & PARAMETERS"
    M[f"B{mrow}"].font = F_SECTION
    meth = [
        ("Security", "OANDA:XAUUSD  (Gold Spot / U.S. Dollar)"),
        ("Signal Type", "Daily HOD / LOD Predictive Model — Daily Level Forecasting"),
        ("Prediction Window", "Pre-session signal generated before the 17:00 ET daily open"),
        ("Predicted Band", "Each prediction is a 0.1% thick price band (Pred High = Pred Low × 1.001)"),
        ("Hit Condition", "Actual High/Low inside the predicted band, or within ±0.05% of its nearest edge"),
        ("Error % Definition", "0 inside the band; otherwise |Actual − nearest band edge| ÷ Actual"),
        ("Tolerance Band", "±0.05% (fixed)"),
        ("Data Source", "TradingView · OANDA:XAUUSD · OHLC Daily (real prices)"),
        ("Predicted Levels", "SYNTHETIC — generated for demonstration; not output of a real model"),
        ("Slippage Model", "Not applied — signal is level-based, not execution-based"),
        ("Run Date", f"{dt.date(2026, 10, 2):%d %b %Y}"),
    ]
    for k, (a, b) in enumerate(meth):
        r = mrow + 1 + k
        M[f"B{r}"], M[f"C{r}"] = a, b
        M[f"B{r}"].font, M[f"C{r}"].font = F_BOLD, F_BODY
    drow = mrow + len(meth) + 2
    M[f"B{drow}"] = ("Past performance is not indicative of future results. Past backtests can be very "
                     "overfitted giving unrealistic results. You are liable for your own losses.")
    M[f"B{drow}"].font = F_DISC
    fake_footer(M, drow + 2, 11)

    wb.properties.title = "XAU/USD HOD/LOD Backtest — FAKE DATA (synthetic)"
    wb.properties.description = FAKE_NOTE
    wb.save(OUT)

    # print python-side truth for cross-checking after recalc
    print(f"saved {OUT}")
    print(f"days={n} hod={sum(hod_hit)} lod={sum(lod_hit)} dual={sum(dual)} either={sum(either)} "
          f"both_miss={sum(both_miss)} dual_rate={dual_rate:.4%}")
    print(f"avg hod err={statistics.mean(hod_err):.6%} lod={statistics.mean(lod_err):.6%}")
    print(f"streaks={streaks} best={best} {mrate[best]:.3f} worst={worst} {mrate[worst]:.3f}")


if __name__ == "__main__":
    main()
