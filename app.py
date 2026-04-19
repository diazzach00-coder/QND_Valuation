"""
╔══════════════════════════════════════════════════════════════╗
║          EQUITY VALUATION — Streamlit Interface              ║
║          Multi-method DCF  |  Bear / Base / Bull             ║
╚══════════════════════════════════════════════════════════════╝
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import requests
from datetime import datetime, date, timezone

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Equity Valuation",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root */
:root {
    --ink:       #0d0d0d;
    --paper:     #faf9f6;
    --cream:     #f2efe8;
    --rule:      #dedad1;
    --accent:    #c8392b;
    --accent2:   #1d6fa4;
    --green:     #2e7d52;
    --mono:      'DM Mono', monospace;
    --serif:     'DM Serif Display', serif;
    --sans:      'DM Sans', sans-serif;
}

/* Global */
html, body, [class*="css"] {
    font-family: var(--sans) !important;
    color: var(--ink) !important;
    background-color: var(--paper) !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .main > div, .block-container {
    background-color: var(--paper) !important;
    color: var(--ink) !important;
}
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] div {
    color: var(--ink) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--ink) !important;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #e8e4dc !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stSelectbox select {
    background: #1a1a1a !important;
    color: #e8e4dc !important;
    border: 1px solid #333 !important;
    border-radius: 4px;
    font-family: var(--mono) !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label {
    color: #aaa8a0 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] hr {
    border-color: #2a2a2a !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #faf9f6 !important;
    font-family: var(--serif) !important;
}

/* Main header */
.ev-masthead {
    border-bottom: 2px solid var(--ink);
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.ev-masthead h1 {
    font-family: var(--serif);
    font-size: 2.8rem;
    line-height: 1.05;
    letter-spacing: -0.02em;
    margin: 0;
}
.ev-masthead .ev-sub {
    font-family: var(--mono);
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    color: #888;
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.ev-company-pill {
    display: inline-block;
    background: var(--ink);
    color: var(--paper) !important;
    font-family: var(--mono);
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    padding: 0.3rem 0.9rem;
    border-radius: 2px;
    margin-left: 1rem;
    vertical-align: middle;
}

/* Section headers */
.ev-section {
    border-top: 1px solid #dedad1;
    padding-top: 0.6rem;
    margin-top: 2.5rem;
    margin-bottom: 1.2rem;
}
.ev-section h2 {
    font-family: var(--serif);
    font-size: 1.55rem;
    letter-spacing: -0.01em;
    margin: 0;
    color: #0d0d0d !important;
}
.ev-section .ev-section-label {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #888 !important;
}

/* Metric cards */
.ev-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1px;
    background: #dedad1;
    border: 1px solid #dedad1;
    margin-bottom: 2rem;
}
.ev-card {
    background: #faf9f6 !important;
    padding: 1.1rem 1.2rem;
}
.ev-card .ev-card-label {
    font-family: var(--mono);
    font-size: 0.63rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #888 !important;
    margin-bottom: 0.35rem;
}
.ev-card .ev-card-value {
    font-family: var(--mono);
    font-size: 1.3rem;
    font-weight: 500;
    color: #0d0d0d !important;
    line-height: 1;
}
.ev-card .ev-card-sub {
    font-size: 0.7rem;
    color: #aaa !important;
    margin-top: 0.2rem;
}

/* Tables */
.ev-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--mono);
    font-size: 0.82rem;
}
.ev-table th {
    background: #0d0d0d !important;
    color: #faf9f6 !important;
    padding: 0.55rem 0.8rem;
    text-align: right;
    font-weight: 500;
    letter-spacing: 0.05em;
    font-size: 0.72rem;
}
.ev-table th:first-child { text-align: left; }
.ev-table td {
    padding: 0.45rem 0.8rem;
    text-align: right;
    border-bottom: 1px solid var(--rule);
    color: #0d0d0d !important;
    background-color: #faf9f6 !important;
}
.ev-table td:first-child {
    text-align: left;
    color: #555 !important;
}
.ev-table tr:last-child td { border-bottom: none; }
.ev-table tr:hover td { background: #f2efe8 !important; }
.ev-table .ev-row-strong td {
    font-weight: 600;
    background: #f0ede5 !important;
    color: #0d0d0d !important;
}

/* Verdict badge */
.ev-verdict {
    display: inline-block;
    font-family: var(--mono);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.4rem 1rem;
    border-radius: 2px;
    font-weight: 500;
}
.ev-verdict.undervalued  { background: #e8f5ee; color: var(--green); border: 1px solid #b8deca; }
.ev-verdict.overvalued   { background: #fdecea; color: var(--accent); border: 1px solid #f0b9b5; }
.ev-verdict.mixed        { background: #eef4fb; color: var(--accent2); border: 1px solid #b8d4ea; }

/* Wacc block */
.ev-wacc-block {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
.ev-wacc-group {
    background: #f2efe8 !important;
    padding: 1.1rem 1.3rem;
    border-left: 3px solid #0d0d0d;
}
.ev-wacc-group h4 {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #888 !important;
    margin: 0 0 0.8rem 0;
}
.ev-wacc-row {
    display: flex;
    justify-content: space-between;
    padding: 0.2rem 0;
    font-family: var(--mono);
    font-size: 0.82rem;
    border-bottom: 1px solid #dedad1;
}
.ev-wacc-row:last-child { border-bottom: none; }
.ev-wacc-row .wk { color: #555 !important; }
.ev-wacc-row .wv { font-weight: 500; color: #0d0d0d !important; }
.ev-wacc-total {
    margin-top: 1rem;
    padding: 0.7rem 1.3rem;
    background: #0d0d0d !important;
    color: #faf9f6 !important;
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.06em;
}

/* Upside coloring */
.up   { color: var(--green) !important; }
.down { color: var(--accent) !important; }
.neu  { color: var(--accent2) !important; }

/* News */
.ev-news-item {
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--rule);
}
.ev-news-item:last-child { border-bottom: none; }
.ev-news-item a {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--ink);
    text-decoration: none;
}
.ev-news-item a:hover { color: var(--accent2); }
.ev-news-meta {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: #aaa;
    margin-top: 0.2rem;
    letter-spacing: 0.04em;
}

/* Scenario pills */
.pill-bear { background:#fdecea; color:var(--accent); padding:0.15rem 0.6rem; border-radius:2px; font-family:var(--mono); font-size:0.72rem; }
.pill-base { background:#eef4fb; color:var(--accent2); padding:0.15rem 0.6rem; border-radius:2px; font-family:var(--mono); font-size:0.72rem; }
.pill-bull { background:#e8f5ee; color:var(--green); padding:0.15rem 0.6rem; border-radius:2px; font-family:var(--mono); font-size:0.72rem; }

/* Info box */
.ev-info {
    background: #f2efe8 !important;
    border-left: 3px solid #1d6fa4;
    padding: 0.8rem 1.1rem;
    font-size: 0.82rem;
    color: #444 !important;
    margin: 1rem 0;
    line-height: 1.6;
}
.ev-warn {
    background: #fef9ec !important;
    border-left: 3px solid #d4a017;
    padding: 0.8rem 1.1rem;
    font-size: 0.82rem;
    color: #5a4400 !important;
    margin: 1rem 0;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — CONFIG
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Equity Valuation")
    st.markdown("---")

    ticker_input = st.text_input("Ticker Symbol", value="ALC", max_chars=10).upper().strip()

    st.markdown("---")
    st.markdown("**Model Parameters**")

    projection_years = st.slider("Projection Years", min_value=3, max_value=10, value=5)
    erp = st.number_input("Equity Risk Premium", min_value=0.01, max_value=0.15,
                          value=0.055, step=0.001, format="%.3f",
                          help="Damodaran implied ERP recommended")
    size_premium = st.number_input("Size Premium", min_value=0.0, max_value=0.05,
                                   value=0.0, step=0.001, format="%.3f",
                                   help="Add for small-cap illiquidity")

    st.markdown("---")

    run = st.button("▶  Run Valuation", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("<div style='font-family:monospace;font-size:0.62rem;color:#aaa;line-height:1.7;'>Data: yfinance + FRED<br>TV: GGM · EV/EBITDA · EV/EBIT<br>Scenarios auto-derived from historical percentiles</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ev-masthead">
  <h1>Equity Valuation
    <span class="ev-company-pill" id="ev-ticker-pill">—</span>
  </h1>
  <div class="ev-sub">Multi-Method DCF  ·  Bear / Base / Bull  ·  Live Market Data</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def ig(info, key, default=None):
    v = info.get(key)
    return v if v not in (None, "", 0) else default

def get_row(df, *keys):
    if df is None or df.empty:
        return pd.Series(dtype=float)
    for k in keys:
        if k in df.index:
            return df.loc[k].astype(float)
    return pd.Series(dtype=float)

def last4(series):
    s = series.dropna().sort_index()
    return s.iloc[-4:] if len(s) >= 4 else s

def fmt_m(v):
    if np.isnan(v): return "N/A"
    return f"${v/1e6:,.0f}M"

def fmt_pct(v):
    if np.isnan(v): return "N/A"
    return f"{v*100:.1f}%"

def upside_color(u):
    if np.isnan(u): return "neu"
    return "up" if u > 0 else "down"


_SECTOR_PEERS = {
    "Technology":             ["MSFT","GOOGL","META","ORCL","CRM","ADBE","AMD","INTC","QCOM","TXN"],
    "Healthcare":             ["JNJ","UNH","PFE","ABBV","MRK","TMO","ABT","DHR","LLY","BMY"],
    "Consumer Cyclical":      ["AMZN","HD","NKE","MCD","SBUX","TGT","LOW","TJX","GM","F"],
    "Consumer Defensive":     ["PG","KO","PEP","WMT","COST","PM","MO","CL","GIS","K"],
    "Energy":                 ["XOM","CVX","COP","SLB","EOG","MPC","VLO","PSX","OXY","HAL"],
    "Industrials":            ["HON","UPS","CAT","DE","LMT","RTX","GE","MMM","EMR","ITW"],
    "Utilities":              ["NEE","DUK","SO","D","AEP","EXC","SRE","XEL","WEC","ES"],
    "Financial Services":     ["JPM","BAC","WFC","GS","MS","BLK","SCHW","AXP","USB","PNC"],
    "Communication Services": ["GOOGL","META","NFLX","DIS","CMCSA","T","VZ","CHTR","EA","TTWO"],
    "Real Estate":            ["AMT","PLD","EQIX","SPG","O","WELL","AVB","EQR","DLR","PSA"],
    "Basic Materials":        ["LIN","APD","NEM","FCX","ECL","DD","DOW","NUE","ALB","MOS"],
}
_FALLBACK_EV_EBITDA = {
    "Technology":20,"Healthcare":16,"Consumer Cyclical":12,"Consumer Defensive":14,
    "Energy":8,"Industrials":13,"Utilities":11,"Financial Services":12,
    "Communication Services":15,"Real Estate":20,"Basic Materials":10,"default":13,
}
_FALLBACK_EV_EBIT = {
    "Technology":28,"Healthcare":22,"Consumer Cyclical":16,"Consumer Defensive":18,
    "Energy":10,"Industrials":16,"Utilities":14,"Financial Services":15,
    "Communication Services":20,"Real Estate":25,"Basic Materials":12,"default":18,
}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if not run:
    st.markdown("""
    <div class="ev-info">
    Enter a ticker in the sidebar and press <strong>Run Valuation</strong> to begin.
    The model fetches live data from yfinance and FRED, auto-derives Bear / Base / Bull
    scenarios from historical percentiles, and produces a full DCF with three terminal
    value approaches.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── FETCH ────────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching data for {ticker_input}…"):
    try:
        tkr  = yf.Ticker(ticker_input)
        info = tkr.info
    except Exception as e:
        st.error(f"Could not retrieve data for **{ticker_input}**: {e}")
        st.stop()

if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
    st.error(f"Ticker **{ticker_input}** not found or returned no data.")
    st.stop()

# Basic info
current_price      = ig(info,"currentPrice") or ig(info,"regularMarketPrice",0)
shares_outstanding = ig(info,"sharesOutstanding",0)
market_cap         = ig(info,"marketCap",0)
beta               = ig(info,"beta",1.0)
sector             = ig(info,"sector","default")
industry           = ig(info,"industry","N/A")
company_name       = ig(info,"longName", ticker_input)
ev_info            = ig(info,"enterpriseValue",0)
trailing_pe        = ig(info,"trailingPE")
forward_pe         = ig(info,"forwardPE")

# Financials
fin = tkr.financials
cf  = tkr.cashflow
bs  = tkr.balance_sheet

def align_series(s, idx, fallback=0.0):
    return s.reindex(idx).fillna(fallback)

rev_raw   = last4(get_row(fin,"Total Revenue","Revenue"))
if rev_raw.empty:
    st.error(f"No revenue data found for **{ticker_input}**.")
    st.stop()

ebit_raw  = last4(get_row(fin,"EBIT","Operating Income"))
ni_raw    = last4(get_row(fin,"Net Income","Net Income Common Stockholders"))
tax_raw   = last4(get_row(fin,"Tax Provision","Income Tax Expense"))
pbi_raw   = last4(get_row(fin,"Pretax Income","Income Before Tax"))
ie_raw    = last4(get_row(fin,"Interest Expense","Interest Expense Non Operating"))
da_raw    = last4(get_row(cf,"Depreciation And Amortization","Depreciation","DepreciationAndAmortization"))
capex_raw = last4(get_row(cf,"Capital Expenditure","Purchase Of Property Plant And Equipment"))
opcf_raw  = last4(get_row(cf,"Operating Cash Flow","Cash Flow From Continuing Operating Activities"))

idx = rev_raw.index

revenue       = rev_raw.values.astype(float)
ebit          = align_series(ebit_raw,  idx).values
da            = align_series(da_raw,    idx).values
capex         = np.abs(align_series(capex_raw, idx).values)
net_income    = align_series(ni_raw,    idx).values
opcf          = align_series(opcf_raw,  idx).values
tax_prov      = align_series(tax_raw,   idx).values
pretax_income = align_series(pbi_raw,   idx).values
interest_exp  = np.abs(align_series(ie_raw, idx).values)
ebitda        = ebit + da
fiscal_years  = [d.year for d in idx]

bs_debt = get_row(bs,"Total Debt","Long Term Debt")
bs_cash = get_row(bs,"Cash And Cash Equivalents","Cash Cash Equivalents And Short Term Investments")
total_debt = float(bs_debt.iloc[0]) if not bs_debt.empty else ig(info,"totalDebt",0)
cash       = float(bs_cash.iloc[0]) if not bs_cash.empty else ig(info,"totalCash",0)
net_debt   = total_debt - cash

# 10Y Treasury
try:
    resp = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv",
        params={"id": "DGS10"},
        timeout=10,
    )
    resp.raise_for_status()
    from io import StringIO
    fred_df = pd.read_csv(StringIO(resp.text), parse_dates=["DATE"])
    fred_df = fred_df[fred_df["DGS10"] != "."]
    rf_rate = float(fred_df["DGS10"].iloc[-1]) / 100
    rf_src  = "FRED"
except Exception:
    rf_rate = 0.043
    rf_src  = "fallback 4.3%"

# Historical P/E
current_pe_percentile = np.nan
pe_status             = "P/E history unavailable"
hist_pe_series        = pd.Series(dtype=float)
try:
    qfin    = tkr.quarterly_financials
    eps_row = get_row(qfin,"Diluted EPS","Basic EPS","Reported EPS")
    if not eps_row.empty:
        eps_sorted = eps_row.sort_index()
        eps_ttm    = eps_sorted.rolling(4).sum().dropna()
        hist_px    = tkr.history(period="10y",auto_adjust=False)["Close"]
        if hist_px.index.tz is not None:
            hist_px.index = hist_px.index.tz_convert(None)
        pe_list = []
        for dt, eps_val in eps_ttm.items():
            if eps_val <= 0: continue
            ts      = pd.Timestamp(dt)
            dt_n    = ts.tz_convert(None) if ts.tzinfo is not None else ts
            cands   = hist_px[hist_px.index >= dt_n]
            if cands.empty: continue
            pe_list.append(float(cands.iloc[0]) / eps_val)
        raw_pe         = pd.Series(pe_list,dtype=float).replace([np.inf,-np.inf],np.nan).dropna()
        hist_pe_series = raw_pe[(raw_pe>0)&(raw_pe<200)]
    if trailing_pe and len(hist_pe_series) >= 8:
        current_pe_percentile = stats.percentileofscore(hist_pe_series.values,trailing_pe,kind="weak")
        if   current_pe_percentile >= 90: pe_status = "Historically expensive"
        elif current_pe_percentile >= 75: pe_status = "Above normal valuation"
        elif current_pe_percentile <= 10: pe_status = "Historically cheap"
        elif current_pe_percentile <= 25: pe_status = "Below normal valuation"
        else:                              pe_status = "Within normal historical range"
    elif trailing_pe:
        pe_status = "N/A (insufficient P/E history)"
except Exception:
    pass

# Effective tax rate
eff_tax = np.where(pretax_income != 0, tax_prov / pretax_income, np.nan)
valid_tax = eff_tax[~np.isnan(eff_tax)]
tax_rate  = float(np.clip(valid_tax[-1] if len(valid_tax) > 0 else 0.21, 0.10, 0.40))

# Peer multiples
_peers = _SECTOR_PEERS.get(sector, [])
with st.spinner(f"Fetching live multiples for {len(_peers)} {sector} peers…"):
    evebitda_vals, evebit_vals, valid_peers = [], [], []
    for t in _peers:
        if t.upper() == ticker_input: continue
        try:
            pi = yf.Ticker(t).info
            mc = pi.get("marketCap"); eb = pi.get("ebitda"); oi = pi.get("ebit") or pi.get("operatingIncome")
            if mc and eb and eb > 0:
                r = mc / eb
                if 2 < r < 100:
                    evebitda_vals.append(float(r)); valid_peers.append(t)
            if mc and oi and oi > 0:
                r = mc / oi
                if 2 < r < 150:
                    evebit_vals.append(float(r))
        except Exception:
            continue

_MIN_PEERS = 3
if len(evebitda_vals) >= _MIN_PEERS:
    ev_ebitda_multiple = float(np.median(evebitda_vals))
    evebitda_src = f"peer median (n={len(evebitda_vals)})"
else:
    ev_ebitda_multiple = float(_FALLBACK_EV_EBITDA.get(sector, _FALLBACK_EV_EBITDA["default"]))
    evebitda_src = "sector default"

if len(evebit_vals) >= _MIN_PEERS:
    ev_ebit_multiple = float(np.median(evebit_vals))
    evebit_src = f"peer median (n={len(evebit_vals)})"
elif ev_info > 0 and float(ebit[-1]) > 0:
    ev_ebit_multiple = ev_info / float(ebit[-1])
    evebit_src = "trailing EV/EBIT"
else:
    ev_ebit_multiple = float(_FALLBACK_EV_EBIT.get(sector, _FALLBACK_EV_EBIT["default"]))
    evebit_src = "sector default"

# Scenarios
rev_growth_series  = pd.Series(revenue).pct_change().dropna().values
ebit_margin_series = ebit / revenue
da_pct_flat        = float(np.mean(da / revenue))
capex_pct_flat     = float(np.mean(capex / revenue))
nwc_pct            = 0.01

SCENARIOS = {
    "Bear": {"rev_growth": float(np.percentile(rev_growth_series,25)),
             "ebit_margin": float(np.percentile(ebit_margin_series,25)), "terminal_g": 0.015},
    "Base": {"rev_growth": float(np.median(rev_growth_series)),
             "ebit_margin": float(np.median(ebit_margin_series)),       "terminal_g": 0.025},
    "Bull": {"rev_growth": float(np.percentile(rev_growth_series,75)),
             "ebit_margin": float(np.percentile(ebit_margin_series,75)),"terminal_g": 0.035},
}

# WACC
Ke = rf_rate + beta * erp + size_premium
cost_of_debt_pretax = np.clip(interest_exp[-1] / total_debt, 0.02, 0.12) if total_debt > 0 else rf_rate + 0.015
Kd_at = cost_of_debt_pretax * (1 - tax_rate)
total_capital = market_cap + total_debt
we = market_cap / total_capital if total_capital > 0 else 1.0
wd = total_debt  / total_capital if total_capital > 0 else 0.0
wacc = we * Ke + wd * Kd_at

# FCF projections
def run_projection(sp, w):
    rg = sp["rev_growth"]; em = sp["ebit_margin"]
    prev_rev = float(revenue[-1])
    res = {k: [] for k in ["revenue","ebit","da","nopat","capex","dnwc","fcf","pv_fcf","disc"]}
    for t in range(1, projection_years + 1):
        r  = prev_rev * (1 + rg); eb = r * em; d  = r * da_pct_flat
        no = eb * (1 - tax_rate); cx = r * capex_pct_flat; dn = (r - prev_rev) * nwc_pct
        fc = no + d - cx - dn;   df_ = (1 + w) ** (-(t - 0.5)); pv = fc * df_
        res["revenue"].append(r); res["ebit"].append(eb); res["da"].append(d)
        res["nopat"].append(no);  res["capex"].append(cx); res["dnwc"].append(dn)
        res["fcf"].append(fc);    res["pv_fcf"].append(pv); res["disc"].append(df_)
        prev_rev = r
    res["sum_pv_fcf"] = sum(res["pv_fcf"])
    res["wacc"] = w
    return res

projection_results = {s: run_projection(sp, wacc) for s, sp in SCENARIOS.items()}

# Terminal values
def compute_tv(scen_name):
    sp      = SCENARIOS[scen_name]; pr = projection_results[scen_name]
    w       = pr["wacc"];           tg = sp["terminal_g"]
    fcf5    = pr["fcf"][-1];        ebit5 = pr["ebit"][-1];  da5 = pr["da"][-1]
    ebitda5 = ebit5 + da5;          mid_disc = (1 + w) ** (-4.5)
    def _m(TV, valid, note):
        return {"TV":TV,"PV_TV":TV*mid_disc if valid else np.nan,"valid":valid,"note":note}
    m1 = _m(fcf5*(1+tg)/(w-tg), fcf5>0 and w>tg, "Invalid: WACC≤g or FCF≤0")
    m2 = _m(ebitda5*ev_ebitda_multiple, ebitda5>0, "Invalid: terminal EBITDA≤0")
    m3 = _m(ebit5*ev_ebit_multiple,     ebit5>0,   "Invalid: terminal EBIT≤0")
    return {"GGM":m1,"EVEBITDA":m2,"EVEBIT":m3}

tv_results = {s: compute_tv(s) for s in SCENARIOS}

# Implied prices
football_data = {s: {} for s in SCENARIOS}
val_records   = []
method_display = {"GGM":"DCF (Gordon Growth TV)","EVEBITDA":"DCF (EV/EBITDA Exit TV)","EVEBIT":"DCF (EV/EBIT Exit TV)"}

all_prices = []
for mkey in ["GGM","EVEBITDA","EVEBIT"]:
    for scen in ["Bear","Base","Bull"]:
        tv_res = tv_results[scen][mkey]; pv_sum = projection_results[scen]["sum_pv_fcf"]
        if not tv_res["valid"]:
            ip = ev_ = eq = up = np.nan; status = tv_res["note"]
        else:
            ev_ = pv_sum + tv_res["PV_TV"]; eq = ev_ - net_debt
            if shares_outstanding <= 0 or eq <= 0:
                ip = up = np.nan; status = "No shares / negative equity"
            else:
                ip = eq / shares_outstanding
                up = (ip - current_price) / current_price if current_price > 0 else np.nan
                status = "OK"
        football_data[scen][mkey] = ip if (not np.isnan(ip) and ip > 0) else np.nan
        if not np.isnan(ip) and ip > 0: all_prices.append(ip)
        val_records.append({"method":method_display[mkey],"scenario":scen,
                             "ev":ev_,"equity":eq,"implied_price":ip,"upside":up,"status":status})

val_df = pd.DataFrame(val_records)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: Update masthead ticker
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ev-masthead">
  <h1>Equity Valuation
    <span class="ev-company-pill">{ticker_input}</span>
  </h1>
  <div class="ev-sub">{company_name} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {industry}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — KEY METRICS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">01</div><h2>Company Snapshot</h2></div>', unsafe_allow_html=True)

nd_ebitda  = net_debt / ebitda[-1] if ebitda[-1] != 0 else float("nan")
tpe_str    = f"{trailing_pe:.1f}×" if trailing_pe else "N/A"
pe_pct_str = f"{current_pe_percentile:.0f}th" if not np.isnan(current_pe_percentile) else "N/A"

cards = [
    ("Current Price",    f"${current_price:,.2f}",     ""),
    ("Market Cap",       f"${market_cap/1e9:,.2f}B",   ""),
    ("Enterprise Value", f"${ev_info/1e9:,.2f}B",      ""),
    ("Net Debt",         f"${net_debt/1e6:,.0f}M",     ""),
    ("Net Debt/EBITDA",  f"{nd_ebitda:.2f}×" if not np.isnan(nd_ebitda) else "N/A", ""),
    ("Beta",             f"{beta:.2f}",                ""),
    ("10Y Treasury",     f"{rf_rate*100:.2f}%",        rf_src),
    ("Trailing P/E",     tpe_str,                      ""),
    ("P/E Percentile",   pe_pct_str,                   pe_status),
]

card_html = '<div class="ev-cards">'
for label, val, sub in cards:
    sub_div = f"<div class='ev-card-sub'>{sub}</div>" if sub else ""
    card_html += f'<div class="ev-card"><div class="ev-card-label">{label}</div><div class="ev-card-value">{val}</div>{sub_div}</div>'
card_html += '</div>'
st.markdown(card_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — HISTORICAL FINANCIALS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">02</div><h2>Historical Financials</h2></div>', unsafe_allow_html=True)

col_labels = [f"FY{y}A" for y in fiscal_years]
rev_growth_h = np.concatenate([[np.nan], np.diff(revenue)/revenue[:-1]])

rows_hist = [
    ("Revenue",         [fmt_m(v) for v in revenue],        False),
    ("Revenue Growth",  ["N/A" if np.isnan(v) else fmt_pct(v) for v in rev_growth_h], False),
    ("EBIT",            [fmt_m(v) for v in ebit],           False),
    ("EBIT Margin",     [fmt_pct(v) for v in ebit/revenue], False),
    ("EBITDA",          [fmt_m(v) for v in ebitda],         True),
    ("EBITDA Margin",   [fmt_pct(v) for v in ebitda/revenue],False),
    ("D&A",             [fmt_m(v) for v in da],             False),
    ("CapEx",           [fmt_m(v) for v in capex],          False),
    ("Eff. Tax Rate",   ["N/A" if np.isnan(v) else fmt_pct(v) for v in eff_tax], False),
    ("Net Income",      [fmt_m(v) for v in net_income],     False),
    ("Op. Cash Flow",   [fmt_m(v) for v in opcf],           True),
]

hdr_html = "".join(f'<th>{c}</th>' for c in col_labels)
tbl_html = f'<table class="ev-table"><thead><tr><th>Metric</th>{hdr_html}</tr></thead><tbody>'
for label, vals, strong in rows_hist:
    row_cls = 'class="ev-row-strong"' if strong else ""
    tbl_html += f'<tr {row_cls}><td>{label}</td>' + "".join(f"<td>{v}</td>" for v in vals) + "</tr>"
tbl_html += "</tbody></table>"
st.markdown(tbl_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — WACC
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">03</div><h2>WACC</h2></div>', unsafe_allow_html=True)

wacc_html = f"""
<div class="ev-wacc-block">
  <div class="ev-wacc-group">
    <h4>Cost of Equity (CAPM)</h4>
    <div class="ev-wacc-row"><span class="wk">Risk-Free Rate (rf)</span><span class="wv">{rf_rate*100:.2f}%</span></div>
    <div class="ev-wacc-row"><span class="wk">Beta (β)</span><span class="wv">{beta:.2f}</span></div>
    <div class="ev-wacc-row"><span class="wk">Equity Risk Premium</span><span class="wv">{erp*100:.2f}%</span></div>
    <div class="ev-wacc-row"><span class="wk">Size Premium</span><span class="wv">{size_premium*100:.2f}%</span></div>
    <div class="ev-wacc-row"><span class="wk"><strong>Ke</strong></span><span class="wv"><strong>{Ke*100:.2f}%</strong></span></div>
  </div>
  <div class="ev-wacc-group">
    <h4>Cost of Debt & Capital Structure</h4>
    <div class="ev-wacc-row"><span class="wk">Pre-tax Cost of Debt</span><span class="wv">{cost_of_debt_pretax*100:.2f}%</span></div>
    <div class="ev-wacc-row"><span class="wk">Tax Rate</span><span class="wv">{tax_rate*100:.1f}%</span></div>
    <div class="ev-wacc-row"><span class="wk"><strong>Kd (after-tax)</strong></span><span class="wv"><strong>{Kd_at*100:.2f}%</strong></span></div>
    <div class="ev-wacc-row"><span class="wk">Equity Weight (we)</span><span class="wv">{we*100:.1f}%</span></div>
    <div class="ev-wacc-row"><span class="wk">Debt Weight (wd)</span><span class="wv">{wd*100:.1f}%</span></div>
  </div>
</div>
<div class="ev-wacc-total">
  <span>WACC</span><span>{wacc*100:.2f}%</span>
</div>
"""
st.markdown(wacc_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SCENARIO ASSUMPTIONS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">04</div><h2>Scenario Assumptions</h2></div>', unsafe_allow_html=True)

scen_html = f"""
<table class="ev-table">
<thead><tr>
  <th>Parameter</th>
  <th><span class="pill-bear">Bear</span></th>
  <th><span class="pill-base">Base</span></th>
  <th><span class="pill-bull">Bull</span></th>
  <th>All Scenarios</th>
</tr></thead>
<tbody>
<tr><td>Revenue Growth (flat)</td>
    <td>{SCENARIOS['Bear']['rev_growth']*100:.1f}%</td>
    <td>{SCENARIOS['Base']['rev_growth']*100:.1f}%</td>
    <td>{SCENARIOS['Bull']['rev_growth']*100:.1f}%</td><td>—</td></tr>
<tr><td>EBIT Margin (flat)</td>
    <td>{SCENARIOS['Bear']['ebit_margin']*100:.1f}%</td>
    <td>{SCENARIOS['Base']['ebit_margin']*100:.1f}%</td>
    <td>{SCENARIOS['Bull']['ebit_margin']*100:.1f}%</td><td>—</td></tr>
<tr><td>Terminal Growth Rate</td>
    <td>1.5%</td><td>2.5%</td><td>3.5%</td><td>—</td></tr>
<tr class="ev-row-strong">
    <td>D&A % Revenue</td><td>—</td><td>—</td><td>—</td><td>{da_pct_flat*100:.1f}%</td></tr>
<tr class="ev-row-strong">
    <td>CapEx % Revenue</td><td>—</td><td>—</td><td>—</td><td>{capex_pct_flat*100:.1f}%</td></tr>
<tr class="ev-row-strong">
    <td>NWC % Revenue</td><td>—</td><td>—</td><td>—</td><td>1.0%</td></tr>
<tr class="ev-row-strong">
    <td>Tax Rate</td><td>—</td><td>—</td><td>—</td><td>{tax_rate*100:.1f}%</td></tr>
</tbody></table>
"""
st.markdown(scen_html, unsafe_allow_html=True)

st.markdown(f"""
<div class="ev-info">
  <strong>Exit Multiples</strong> &nbsp;·&nbsp;
  EV/EBITDA: <strong>{ev_ebitda_multiple:.2f}×</strong> ({evebitda_src}) &nbsp;|&nbsp;
  EV/EBIT: <strong>{ev_ebit_multiple:.2f}×</strong> ({evebit_src})
  {"&nbsp;·&nbsp; Peers: " + ", ".join(valid_peers[:8]) if valid_peers else ""}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — FCF PROJECTION (BASE)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">05</div><h2>FCF Projection — Base Scenario</h2></div>', unsafe_allow_html=True)

pr_base = projection_results["Base"]
yr_labels = [f"FY+{t}" for t in range(1, projection_years + 1)]

fcf_hdr = "".join(f"<th>{y}</th>" for y in yr_labels)
def pr_row(label, arr, strong=False):
    cls = 'class="ev-row-strong"' if strong else ""
    return f'<tr {cls}><td>{label}</td>' + "".join(f"<td>{fmt_m(v)}</td>" for v in arr) + "</tr>"

fcf_tbl = f"""
<table class="ev-table"><thead><tr><th>($M)</th>{fcf_hdr}</tr></thead><tbody>
{pr_row("Revenue",     pr_base["revenue"])}
{pr_row("EBIT",        pr_base["ebit"])}
{pr_row("NOPAT",       pr_base["nopat"])}
{pr_row("(+) D&A",     pr_base["da"])}
{pr_row("(-) CapEx",   pr_base["capex"])}
{pr_row("(-) ΔNWC",    pr_base["dnwc"])}
{pr_row("FCF",         pr_base["fcf"], True)}
<tr><td>Discount Factor</td>{''.join(f"<td>{v:.4f}</td>" for v in pr_base["disc"])}</tr>
{pr_row("PV of FCF",   pr_base["pv_fcf"])}
</tbody></table>
"""
st.markdown(fcf_tbl, unsafe_allow_html=True)
st.markdown(f"""
<div class="ev-info">Sum of PV(FCF) — Base: <strong>{fmt_m(pr_base['sum_pv_fcf'])}</strong></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — VALUATION SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">06</div><h2>Valuation Summary</h2></div>', unsafe_allow_html=True)

# Verdict
if all_prices:
    lo, hi = min(all_prices), max(all_prices)
    rng_str = f"${lo:.2f} – ${hi:.2f}"
    if   lo > current_price * 1.15: verdict, vcls = "Undervalued across all methods", "undervalued"
    elif hi < current_price * 0.85: verdict, vcls = "Overvalued across all methods",  "overvalued"
    else:                            verdict, vcls = "Mixed — current price within or near fair value range", "mixed"
else:
    rng_str = "N/A"
    verdict, vcls = "No economically valid implied price produced", "mixed"

st.markdown(f"""
<div style="display:flex;align-items:center;gap:1.5rem;margin-bottom:1.2rem;">
  <div>
    <div style="font-family:var(--mono);font-size:0.65rem;color:#999;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem;">Current Market Price</div>
    <div style="font-family:var(--mono);font-size:2rem;font-weight:500;">${current_price:.2f}</div>
  </div>
  <div>
    <div style="font-family:var(--mono);font-size:0.65rem;color:#999;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem;">Valuation Range</div>
    <div style="font-family:var(--mono);font-size:2rem;font-weight:500;">{rng_str}</div>
  </div>
  <div>
    <span class="ev-verdict {vcls}">{verdict}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Full table
vs_hdr = "<th>Method</th><th>Scenario</th><th>EV</th><th>Equity Value</th><th>Implied Price</th><th>Upside</th><th>Status</th>"
vs_rows = ""
prev_method = None
for _, row in val_df.iterrows():
    if row["method"] != prev_method and prev_method is not None:
        vs_rows += '<tr><td colspan="7" style="padding:0;height:6px;background:var(--cream);"></td></tr>'
    ev_s  = fmt_m(row["ev"])     if not np.isnan(row["ev"])            else "N/A"
    eq_s  = fmt_m(row["equity"]) if not np.isnan(row["equity"])        else "N/A"
    ip_s  = f"${row['implied_price']:.2f}" if not np.isnan(row["implied_price"]) else "N/A"
    up_v  = row["upside"]
    up_s  = f"{up_v*100:+.1f}%" if not np.isnan(up_v) else "N/A"
    ucls  = upside_color(up_v)
    scls  = {"Bear":"pill-bear","Base":"pill-base","Bull":"pill-bull"}[row["scenario"]]
    vs_rows += f"""<tr>
      <td>{row["method"]}</td>
      <td><span class="{scls}">{row["scenario"]}</span></td>
      <td>{ev_s}</td><td>{eq_s}</td><td>{ip_s}</td>
      <td class="{ucls}">{up_s}</td>
      <td style="font-size:0.72rem;color:#888;">{row["status"] if row["status"]!="OK" else "✓"}</td>
    </tr>"""
    prev_method = row["method"]

st.markdown(f"""
<table class="ev-table"><thead><tr>{vs_hdr}</tr></thead><tbody>{vs_rows}</tbody></table>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — SENSITIVITY HEATMAPS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">07</div><h2>Sensitivity Analysis</h2></div>', unsafe_allow_html=True)

base_sp   = SCENARIOS["Base"]
base_wacc = wacc
base_tg   = base_sp["terminal_g"]
base_rg   = base_sp["rev_growth"]
base_em   = base_sp["ebit_margin"]
base_rev0 = float(revenue[-1])

def implied_ggm(rg_, em_, w_, tg_):
    pr_rev = base_rev0; s_pv = 0.0; fcf_last = 0.0
    for t in range(1, projection_years + 1):
        r  = pr_rev*(1+rg_); eb = r*em_; d = r*da_pct_flat
        no = eb*(1-tax_rate); cx = r*capex_pct_flat; dn = (r-pr_rev)*nwc_pct
        fc = no+d-cx-dn
        s_pv += fc*(1+w_)**(-(t-0.5)); fcf_last = fc; pr_rev = r
    if w_<=tg_ or fcf_last<=0: return np.nan
    TV = fcf_last*(1+tg_)/(w_-tg_); PTV = TV*(1+w_)**(-4.5)
    ev = s_pv+PTV; eq = ev-net_debt
    return eq/shares_outstanding if shares_outstanding>0 else np.nan

wacc_range = np.arange(base_wacc-0.02, base_wacc+0.0251, 0.005)
tg_range   = np.arange(0.01, 0.0451, 0.005)
rg_range   = np.arange(base_rg-0.04, base_rg+0.0401, 0.01)
em_range   = np.arange(base_em-0.04, base_em+0.0401, 0.01)
beta_range = np.arange(0.5, 2.51, 0.25)
rf_range   = np.arange(0.02, 0.0601, 0.005)

hm1 = np.array([[implied_ggm(base_rg,base_em,w_,tg_) for tg_ in tg_range] for w_ in wacc_range])
hm2 = np.array([[implied_ggm(rg_,em_,base_wacc,base_tg) for em_ in em_range] for rg_ in rg_range])
hm3 = np.array([[we*(rf_+b_*erp+size_premium)+wd*Kd_at for rf_ in rf_range] for b_ in beta_range])*100

matplotlib.rcParams.update({
    "font.family": "monospace",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

def highlight_cell(ax, row_idx, col_idx):
    ax.add_patch(plt.Rectangle((col_idx-0.5,row_idx-0.5),1,1,
                                fill=False,edgecolor="#0d0d0d",lw=2.5))

fig, axes = plt.subplots(1,3,figsize=(22,7))
fig.patch.set_facecolor("#faf9f6")
for ax in axes: ax.set_facecolor("#faf9f6")
fig.suptitle(f"{company_name} ({ticker_input})  —  Sensitivity Analysis",
             fontsize=13, fontweight="bold", y=1.02, color="#0d0d0d")

df1 = pd.DataFrame(hm1,index=[f"{w*100:.2f}%" for w in wacc_range],
                        columns=[f"{g*100:.1f}%" for g in tg_range])
sns.heatmap(df1,ax=axes[0],annot=True,fmt=".0f",cmap="RdYlGn",
            center=current_price,linewidths=0.4,annot_kws={"size":8},
            linecolor="#e8e4dc")
axes[0].set_title("WACC × Terminal Growth\n→ Implied Price ($)",fontsize=10,pad=8)
axes[0].set_ylabel("WACC"); axes[0].set_xlabel("Terminal Growth Rate")
wi = np.argmin(np.abs(wacc_range-base_wacc)); ti = np.argmin(np.abs(tg_range-base_tg))
highlight_cell(axes[0],wi,ti)

df2 = pd.DataFrame(hm2,index=[f"{r*100:.1f}%" for r in rg_range],
                        columns=[f"{m*100:.1f}%" for m in em_range])
sns.heatmap(df2,ax=axes[1],annot=True,fmt=".0f",cmap="RdYlGn",
            center=current_price,linewidths=0.4,annot_kws={"size":8},
            linecolor="#e8e4dc")
axes[1].set_title("Revenue Growth × EBIT Margin\n→ Implied Price ($)",fontsize=10,pad=8)
axes[1].set_ylabel("Revenue Growth"); axes[1].set_xlabel("EBIT Margin")
ri = np.argmin(np.abs(rg_range-base_rg)); ei = np.argmin(np.abs(em_range-base_em))
highlight_cell(axes[1],ri,ei)

df3 = pd.DataFrame(hm3,index=[f"{b:.2f}" for b in beta_range],
                        columns=[f"{r*100:.1f}%" for r in rf_range])
sns.heatmap(df3,ax=axes[2],annot=True,fmt=".2f",cmap="coolwarm",
            center=wacc*100,linewidths=0.4,annot_kws={"size":8},
            linecolor="#e8e4dc")
axes[2].set_title("Beta × Risk-Free Rate\n→ Implied WACC (%)",fontsize=10,pad=8)
axes[2].set_ylabel("Beta"); axes[2].set_xlabel("Risk-Free Rate")
bi  = np.argmin(np.abs(beta_range-beta)); rfi = np.argmin(np.abs(rf_range-rf_rate))
highlight_cell(axes[2],bi,rfi)

plt.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — FOOTBALL FIELD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">08</div><h2>Football Field</h2></div>', unsafe_allow_html=True)

method_keys_ff  = ["GGM","EVEBITDA","EVEBIT"]
method_names_ff = {"GGM":"DCF (Gordon Growth TV)","EVEBITDA":"DCF (EV/EBITDA Exit TV)","EVEBIT":"DCF (EV/EBIT Exit TV)"}

ff_ranges = {}
for mkey in method_keys_ff:
    bear = football_data["Bear"][mkey]; base = football_data["Base"][mkey]; bull = football_data["Bull"][mkey]
    if any(np.isnan(v) for v in [bear,base,bull]): continue
    ff_ranges[mkey] = (bear,base,bull)

if not ff_ranges:
    st.markdown('<div class="ev-warn">No valid implied prices produced — football field cannot be drawn.</div>', unsafe_allow_html=True)
else:
    n_bars = len(ff_ranges); bar_h = 0.55; gap = 1.0
    y_positions = [i*gap for i in range(n_bars)]

    fig2, ax2 = plt.subplots(figsize=(13, 3.5+n_bars*0.9))
    fig2.patch.set_facecolor("#faf9f6"); ax2.set_facecolor("#faf9f6")

    all_ff_vals = [v for bear,base,bull in ff_ranges.values() for v in (bear,bull)]+[current_price]
    x_lo = min(all_ff_vals)*0.88; x_hi = max(all_ff_vals)*1.12

    for yi,(mkey,(bear,base,bull)) in zip(y_positions,ff_ranges.items()):
        span = bull-bear
        ax2.barh(yi,span,left=bear,height=bar_h,color="#4C72B0",alpha=0.18,zorder=2)
        ax2.barh(yi,base-bear,left=bear,height=bar_h,color="#c8392b",alpha=0.22,zorder=3)
        ax2.barh(yi,bull-base,left=base,height=bar_h,color="#2e7d52",alpha=0.22,zorder=3)
        ax2.barh(yi,span,left=bear,height=bar_h,color="none",edgecolor="#4C72B0",linewidth=1.5,zorder=4)
        ax2.plot([base,base],[yi-bar_h/2,yi+bar_h/2],color="#0d0d0d",linewidth=2.5,zorder=5)

        def up_str(p):
            u = (p-current_price)/current_price*100
            return f"${p:.0f}\n({'+' if u>=0 else ''}{u:.1f}%)"

        pad = (x_hi-x_lo)*0.005
        ax2.text(bear-pad,yi,up_str(bear),ha="right",va="center",fontsize=7.5,color="#c8392b",fontweight="bold")
        ax2.text(base,yi+bar_h/2+0.06,f"${base:.0f}",ha="center",va="bottom",fontsize=7.5,color="#0d0d0d",fontweight="bold")
        ax2.text(bull+pad,yi,up_str(bull),ha="left",va="center",fontsize=7.5,color="#2e7d52",fontweight="bold")

    ax2.axvline(current_price,color="#0d0d0d",linestyle="--",linewidth=1.8,zorder=6)
    ax2.text(current_price,n_bars*gap-0.05,f"${current_price:.2f}",ha="center",va="bottom",
             fontsize=8.5,fontweight="bold",color="#0d0d0d",
             bbox=dict(fc="#faf9f6",ec="#0d0d0d",pad=2,lw=1))

    ax2.set_yticks(y_positions)
    ax2.set_yticklabels([method_names_ff[k] for k in ff_ranges],fontsize=10,fontweight="bold")
    ax2.set_xlim(x_lo,x_hi); ax2.set_ylim(-gap*0.6,(n_bars-1)*gap+gap*0.7)
    ax2.set_xlabel("Implied Share Price  ($)",fontsize=10)
    ax2.xaxis.grid(True,linestyle=":",alpha=0.4,zorder=0); ax2.set_axisbelow(True)
    ax2.spines[["top","right"]].set_visible(False)

    legend_els = [
        mpatches.Patch(color="#c8392b",alpha=0.5,label="Bear"),
        mpatches.Patch(color="#2e7d52",alpha=0.5,label="Bull"),
        plt.Line2D([0],[0],color="#0d0d0d",lw=2.5,label="Base"),
        plt.Line2D([0],[0],color="#0d0d0d",lw=1.8,linestyle="--",label=f"Current  ${current_price:.2f}"),
    ]
    ax2.legend(handles=legend_els,fontsize=8.5,loc="lower right",framealpha=0.9,edgecolor="#dedad1")
    ax2.set_title(f"{company_name}  ({ticker_input})  —  Valuation Football Field\n"
                  f"All bars are DCF-based; only the terminal value method differs.",
                  fontsize=11,fontweight="bold",pad=12)
    plt.tight_layout()
    st.pyplot(fig2,use_container_width=True)
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — METHODOLOGY GUIDANCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">09</div><h2>Methodology Guidance</h2></div>', unsafe_allow_html=True)

_tech_comms  = ["Technology","Communication Services"]
_industrial  = ["Energy","Industrials","Basic Materials"]
_consumer_hc = ["Consumer Defensive","Consumer Cyclical","Healthcare"]
_regulated   = ["Utilities","Real Estate"]
_financial   = ["Financial Services"]

_ggm_v = tv_results["Base"]["GGM"]["valid"]
_evb_v = tv_results["Base"]["EVEBITDA"]["valid"]
_evt_v = tv_results["Base"]["EVEBIT"]["valid"]

if   sector in _tech_comms:  rec = "EV/EBITDA Exit and Gordon Growth are most relevant. High margins mean EBITDA closely tracks FCF. Verify TV does not exceed 70% of total EV — if so, weight EV/EBITDA more heavily."
elif sector in _industrial:  rec = "EV/EBIT Exit is most reliable given significant CapEx requirements. EBITDA overstates earnings power here. Cross-check against industry reinvestment rates."
elif sector in _consumer_hc: rec = "Gordon Growth TV is the anchor. Stable cash flows make long-term projections reliable. Use EV/EBITDA as a sanity check against sector peers."
elif sector in _regulated:   rec = "Gordon Growth TV is preferred. Consider a dividend discount model if the company pays consistent dividends. EV/EBITDA and EV/EBIT are less meaningful for regulated capital structures."
elif sector in _financial:   rec = "EV-based methods are not meaningful for banks and insurers — debt is an input, not capital structure. Price-to-Book and ROE-based models are more appropriate."
else:                         rec = "Review all three methods and weight toward the range where two or more methods converge."

if not (_ggm_v or _evb_v or _evt_v):
    rec += " ⚠ All terminal value methods are invalid under base-case projections — do not treat any implied prices as reliable."

st.markdown(f'<div class="ev-info"><strong>{company_name} ({sector})</strong><br>{rec}</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
method_guide = [
    ("DCF — Gordon Growth TV", "Mature, profitable companies with stable cash flows.",
     "Pre-revenue, early-stage, highly cyclical. Also invalid when WACC ≤ g or terminal FCF ≤ 0.",
     "Consumer staples, industrials, large-cap tech."),
    ("DCF — EV/EBITDA Exit TV", "Capital-light businesses where EBITDA ≈ FCF.",
     "CapEx-heavy industries; financial services. Invalid when terminal EBITDA ≤ 0.",
     "Software, media, asset-light services."),
    ("DCF — EV/EBIT Exit TV", "Capital-intensive industries with high recurring CapEx.",
     "Financial services, companies with large non-cash charges.",
     "Manufacturing, energy, retail, telecom."),
]
for col, (title, best, avoid, examples) in zip([col1,col2,col3], method_guide):
    with col:
        st.markdown(f'<div style="background:#f2efe8;padding:1.1rem 1.2rem;border-top:3px solid #0d0d0d;height:100%;"><div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;color:#888;margin-bottom:0.6rem;">{title}</div><div style="margin-bottom:0.7rem;"><span style="font-family:monospace;font-size:0.65rem;color:#2e7d52;text-transform:uppercase;">Best for</span><br><span style="font-size:0.82rem;color:#0d0d0d;">{best}</span></div><div style="margin-bottom:0.7rem;"><span style="font-family:monospace;font-size:0.65rem;color:#c8392b;text-transform:uppercase;">Avoid</span><br><span style="font-size:0.82rem;color:#0d0d0d;">{avoid}</span></div><div><span style="font-family:monospace;font-size:0.65rem;color:#888;text-transform:uppercase;">Examples</span><br><span style="font-size:0.82rem;color:#0d0d0d;">{examples}</span></div></div>', unsafe_allow_html=True)

# Convergence
base_prices_dict = {k: football_data["Base"][k] for k in ["GGM","EVEBITDA","EVEBIT"]}
valid_base = {k: v for k,v in base_prices_dict.items() if not np.isnan(v) and v > 0}
st.markdown("---")
if len(valid_base) >= 2:
    vals   = list(valid_base.values())
    spread = (max(vals)-min(vals))/np.mean(vals)*100
    mnames = {"GGM":"Gordon Growth","EVEBITDA":"EV/EBITDA Exit","EVEBIT":"EV/EBIT Exit"}
    if spread <= 20:
        conv_msg = f"✓ Methods agree within 20% (spread: {spread:.1f}%) — valuation range is reasonably tight."
        conv_cls = "ev-info"
    else:
        hi_k = max(valid_base,key=valid_base.get); lo_k = min(valid_base,key=valid_base.get)
        conv_msg = (f"⚠ Methods diverge by {spread:.1f}% (>{20}% threshold). "
                    f"Highest: {mnames[hi_k]} (${valid_base[hi_k]:.2f}), "
                    f"Lowest: {mnames[lo_k]} (${valid_base[lo_k]:.2f}). "
                    f"Re-examine terminal value assumptions and exit multiples.")
        conv_cls = "ev-warn"
    st.markdown(f'<div class="{conv_cls}"><strong>Convergence Check</strong> &nbsp;—&nbsp; {conv_msg}</div>', unsafe_allow_html=True)
elif len(valid_base) == 1:
    st.markdown('<div class="ev-warn">Only one valid base-case method. Convergence cannot be assessed — cross-check against comparable company multiples.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="ev-warn">No valid base-case implied prices. Review projected operating economics.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — NEWS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ev-section"><div class="ev-section-label">10</div><h2>Recent News</h2></div>', unsafe_allow_html=True)

_news     = tkr.news or []
_articles = [a for a in _news if a.get("link") and a.get("title")][:6]

if not _articles:
    st.markdown(f'<div class="ev-info">No recent news found for {ticker_input}.</div>', unsafe_allow_html=True)
else:
    news_html = ""
    for a in _articles:
        title = a.get("title","No title"); link = a.get("link","#")
        pub   = a.get("publisher") or "Unknown"
        ts    = a.get("providerPublishTime")
        dt_s  = datetime.fromtimestamp(ts,tz=timezone.utc).strftime("%b %d, %Y") if ts else ""
        news_html += f"""
        <div class="ev-news-item">
          <a href="{link}" target="_blank">{title}</a>
          <div class="ev-news-meta">{pub}{" · " + dt_s if dt_s else ""}</div>
        </div>"""
    st.markdown(news_html, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid var(--rule);margin-top:3rem;padding-top:1rem;
            font-family:var(--mono);font-size:0.65rem;color:#bbb;letter-spacing:0.06em;">
  Data: yfinance · FRED (DGS10) · Scenarios auto-derived from historical percentiles ·
  For academic / research use only — not investment advice.
</div>
""", unsafe_allow_html=True)
