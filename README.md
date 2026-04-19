# Equity Valuation Notebook

A single-ticker, multi-method DCF valuation pipeline built in Python/Jupyter. Point it at any publicly traded equity, run all cells top-to-bottom, and receive: a full historical financial summary, WACC decomposition, three-scenario FCF projections, three terminal-value approaches, sensitivity heatmaps, a football-field chart, and a methodology guidance section.

---

## Features

| Cell | Output |
|------|--------|
| 1 — Config | Single cell to set ticker, projection horizon, ERP, and size premium |
| 2 — Imports | Library validation |
| 3 — Data Fetch | Live data from `yfinance` + 10Y Treasury from FRED; P/E percentile against 10-year history |
| 4 — Historical Financials | Revenue, EBIT, EBITDA, D&A, CapEx, tax rate, net income, operating cash flow (last 4 fiscal years) |
| 5 — Scenario Derivation | Bear / Base / Bull parameters auto-derived from historical percentiles; live peer multiples fetched for exit multiple calibration |
| 6 — WACC | CAPM cost of equity; implied cost of debt from interest expense; market-value-weighted capital structure |
| 7 — FCF Projection | 5-year unlevered FCF model (mid-year convention) for all three scenarios |
| 8 — Terminal Value | Three methods: Gordon Growth Model, EV/EBITDA Exit, EV/EBIT Exit |
| 9 — Valuation Summary | Implied share prices and upside/(downside) for all 9 scenario-method combinations |
| 10 — Sensitivity | Three heatmaps: WACC × terminal *g*, revenue growth × EBIT margin, beta × risk-free rate → WACC |
| 11 — Football Field | Horizontal bar chart spanning Bear-to-Bull with Base tick and current price overlay |
| 12 — Methodology | Which method to trust by sector; convergence check across methods |
| 13 — Recent News | Top-5 headlines from `yfinance` rendered as an HTML table |

---

## Quick Start

```python
# Cell 1 — edit only this cell
TICKER           = "AAPL"
PROJECTION_YEARS = 5
ERP              = 0.055   # Equity Risk Premium — Damodaran recommended
SIZE_PREMIUM     = 0.0     # Add a positive float for small-cap illiquidity premium
```

Then **Run All** (`Kernel → Restart & Run All`).

---

## Installation

```bash
pip install yfinance pandas numpy scipy matplotlib seaborn pandas-datareader
```

All other dependencies (`IPython`, `datetime`) are part of the Python standard library or Jupyter.

---

## Methodology

### DCF Framework

All three valuation methods share the same discounted cash flow engine. The only difference is how the **terminal value** is estimated at the end of Year 5.

**Free Cash Flow (unlevered)**

```
FCF = NOPAT + D&A − CapEx − ΔNWC
NOPAT = EBIT × (1 − tax rate)
```

A **mid-year discount convention** is applied: Year *t* cash flows are discounted at `(1 + WACC)^(−(t − 0.5))`.

---

### Terminal Value Methods

| Method | Formula | Best For | Not Reliable For |
|--------|---------|----------|-----------------|
| **Gordon Growth (GGM)** | `FCF₅ × (1 + g) / (WACC − g)` | Mature companies with stable cash flows | Pre-revenue, early-stage, or highly cyclical companies; when TV > 70% of EV |
| **EV/EBITDA Exit** | `EBITDA₅ × peer median multiple` | Capital-light businesses (software, media) | CapEx-heavy industries; financial services |
| **EV/EBIT Exit** | `EBIT₅ × peer median multiple` | Capital-intensive industries (energy, manufacturing) | Financial services; companies with large non-cash charges |

If any terminal metric is non-positive, or if `WACC ≤ g`, that method is flagged invalid and excluded from the valuation summary.

---

### WACC

```
Ke  = rf + β × ERP + size_premium          (CAPM)
Kd  = interest_expense / total_debt × (1 − tax_rate)
WACC = (E/V) × Ke + (D/V) × Kd
```

- **rf** — 10-year U.S. Treasury yield, fetched live from FRED (`DGS10`). Falls back to 4.3% if FRED is unavailable.
- **β** — from `yfinance` (`info["beta"]`); defaults to 1.0 if missing.
- **ERP** — set in Cell 1; Damodaran's implied ERP is the recommended source.
- **Size premium** — set to 0 by default; add manually for small-cap companies.
- Capital structure weights are based on **market-value equity** and **book-value debt** (most recent balance sheet).

---

### Scenario Construction

Scenarios are derived automatically from the last 4 years of historical data, not manually entered:

| Scenario | Revenue Growth | EBIT Margin | Terminal *g* |
|----------|---------------|-------------|-------------|
| Bear | 25th percentile | 25th percentile | 1.5% |
| Base | Median | Median | 2.5% |
| Bull | 75th percentile | 75th percentile | 3.5% |

D&A %, CapEx %, NWC % (1% flat), and tax rate are held constant across scenarios.

---

### Peer Exit Multiples

The notebook fetches **live market cap / EBITDA** and **market cap / EBIT** ratios for up to 10 sector-defined peers using `yfinance`. The **median** of clean observations (2× < multiple < 100× for EBITDA; 2× < multiple < 150× for EBIT) is used. If fewer than 3 valid peers are found, a hard-coded sector default is applied. Peers are defined in `_SECTOR_PEERS` in Cell 5.

---

### Sensitivity Analysis

Three heatmaps are produced, each with the base-case cell highlighted:

1. **WACC × Terminal Growth** — implied share price (Gordon Growth TV only)
2. **Revenue Growth × EBIT Margin** — implied share price (Gordon Growth TV only)
3. **Beta × Risk-Free Rate** — implied WACC (does not produce a price; diagnostic only)

---

## Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Price, financials, beta, info | `yfinance` | Live on each run |
| 10Y Treasury yield | FRED (`DGS10`) via `pandas-datareader` | Fallback: 4.3% |
| Peer multiples | `yfinance` (per-ticker) | Computed each run; not cached |
| News headlines | `yfinance` `.news` | Top 5 articles |

> **Note:** `yfinance` data quality varies by ticker. Non-U.S. equities, micro-caps, and recently listed companies may return incomplete or missing financials. Always verify key inputs (revenue, EBIT, D&A, CapEx) against SEC filings or a primary data source.

---

## Limitations & Caveats

- **Flat growth and margin assumptions.** Revenue growth and EBIT margin are held constant within each scenario. Real companies exhibit mean-reverting margins and non-linear growth paths.
- **Single discount rate.** One WACC is applied to all projection years and all scenarios. Risk profiles typically differ across scenarios.
- **No reinvestment rate modeling.** The NOPAT-to-FCF bridge uses historical D&A and CapEx percentages. For high-growth companies, reinvestment needs may be systematically understated.
- **Book-value debt weights.** Market-value debt weights are generally preferred but require yield-to-maturity data not available from `yfinance`.
- **Terminal value sensitivity.** For many growth companies, the terminal value will exceed 70% of total enterprise value. The notebook flags this condition; treat such results with caution.
- **Financial services exclusion.** EV-based methods are not meaningful for banks, insurers, or REITs. The methodology cell notes this explicitly, but the model still runs and produces numbers—interpret them skeptically.
- **yfinance data lag.** Financial statement data may lag by one or two quarters depending on the ticker and reporting schedule.

---

## File Structure

```
Equity_Valuation.ipynb   # Main notebook (13 cells)
README.md                # This file
```

---

## License

For academic and personal use. Financial outputs are not investment advice.
