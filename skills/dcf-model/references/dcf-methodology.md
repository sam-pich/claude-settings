# DCF Valuation Methodology

## Core Concept

DCF valuation determines the present value of expected future cash flows. The fundamental equation:

```
Value = Sum of [CF_t / (1 + r)^t] for t = 1 to infinity
```

Where:
- CF_t = Cash flow in period t
- r = Discount rate (cost of capital)
- t = Time period

---

## DCF Types

### 1. Unlevered DCF (Enterprise Value)

**Cash Flow:** Free Cash Flow to Firm (FCFF)
**Discount Rate:** Weighted Average Cost of Capital (WACC)
**Result:** Enterprise Value

**When to use:**
- Comparing companies with different capital structures
- M&A analysis
- Companies with changing capital structure

**Formula:**
```
FCFF = NOPAT + D&A - CapEx - Change in NWC

Where:
NOPAT = EBIT x (1 - Tax Rate)
```

**To get Equity Value:**
```
Equity Value = Enterprise Value - Net Debt + Non-operating Assets
Net Debt = Total Debt - Cash - Short-term Investments
```

### 2. Levered DCF (Equity Value)

**Cash Flow:** Free Cash Flow to Equity (FCFE)
**Discount Rate:** Cost of Equity (Ke)
**Result:** Equity Value directly

**When to use:**
- Financial institutions (banks, insurance)
- Stable capital structure
- Direct equity valuation

**Formula:**
```
FCFE = Net Income + D&A - CapEx - Change in NWC - Debt Repayment + Debt Issuance
```

---

## Cost of Capital

### Cost of Equity (CAPM)

```
Ke = Rf + Beta x ERP

Where:
Rf = Risk-free rate (10-year Treasury yield)
Beta = Levered beta of the company
ERP = Equity Risk Premium (historical: 5-6%)
```

**Beta:**
- Measures systematic risk relative to market
- Levered beta includes financial leverage
- Unlevered beta (asset beta) removes leverage effect

```
Unlevered Beta = Levered Beta / [1 + (1 - Tax Rate) x (D/E)]
Relevered Beta = Unlevered Beta x [1 + (1 - Tax Rate) x (Target D/E)]
```

### Cost of Debt

```
Kd = Risk-free Rate + Credit Spread

After-tax Cost of Debt = Kd x (1 - Tax Rate)
```

Credit spread based on credit rating:
| Rating | Spread |
|--------|--------|
| AAA | 0.5% |
| AA | 0.8% |
| A | 1.0% |
| BBB | 1.5% |
| BB | 2.5% |
| B | 4.0% |
| CCC | 7.0% |

### WACC

```
WACC = (E / V) x Ke + (D / V) x Kd x (1 - T)

Where:
E = Market value of equity
D = Market value of debt
V = E + D (total capital)
T = Corporate tax rate
```

---

## Model Complexity

### 2-Stage Model

1. **Explicit forecast period** (5-10 years): Detailed projections
2. **Terminal value**: Steady-state assumption

Best for: Mature companies with predictable growth

### 3-Stage Model

1. **High growth phase** (3-5 years): Above-market growth
2. **Transition phase** (3-5 years): Growth converging to market
3. **Stable phase**: Terminal value

Best for: Growth companies expected to mature

### LBO-Style Model

Detailed debt schedule with:
- Multiple debt tranches (senior, mezzanine, etc.)
- Cash sweep mechanics
- Interest expense on average debt
- Mandatory and optional prepayments

Best for: Private equity analysis, leveraged situations

---

## Terminal Value

Terminal value often represents 60-80% of total DCF value.

### Method 1: Perpetuity Growth (Gordon Growth)

```
TV = Terminal FCF x (1 + g) / (WACC - g)

Where:
g = Long-term growth rate (should not exceed GDP growth)
```

**Key constraint:** g < WACC, otherwise undefined

**Typical values:**
- Developed markets: 2-3%
- Should not exceed long-term nominal GDP growth (~4%)

### Method 2: Exit Multiple

```
TV = Terminal Year EBITDA x Exit Multiple
```

**Multiple selection:**
- Based on comparable trading multiples
- Often use current multiple or historical average
- Adjust for expected market conditions

**Typical ranges by sector:**
| Sector | EV/EBITDA Range |
|--------|-----------------|
| Technology | 10-20x |
| Healthcare | 10-15x |
| Consumer Staples | 8-12x |
| Industrials | 7-10x |
| Utilities | 6-9x |
| Financials | N/A (use P/E) |

### Implied Perpetuity Growth

Cross-check exit multiple implies perpetuity growth:
```
Implied g = WACC - (Terminal FCF / TV)
```

If implied g > 4%, the multiple may be too aggressive.

---

## Free Cash Flow Build-Up

### Unlevered FCF

| Line Item | Calculation |
|-----------|-------------|
| Revenue | Projected |
| (-) COGS | Revenue x COGS% |
| **Gross Profit** | Revenue - COGS |
| (-) Operating Expenses | R&D + SG&A + Other |
| **EBIT** | Gross Profit - OpEx |
| (-) Taxes on EBIT | EBIT x Tax Rate |
| **NOPAT** | EBIT x (1 - Tax Rate) |
| (+) D&A | From projections |
| (-) CapEx | From projections |
| (-) Change in NWC | Current NWC - Prior NWC |
| **Unlevered FCF** | NOPAT + D&A - CapEx - dNWC |

### Net Working Capital

```
NWC = Current Assets (ex Cash) - Current Liabilities (ex Debt)

Specifically:
NWC = Accounts Receivable + Inventory + Prepaid - Accounts Payable - Accrued
```

**Projection approach:**

Using days outstanding:
```
AR = Revenue x (DSO / 365)
Inventory = COGS x (DIO / 365)
AP = COGS x (DPO / 365)
```

Or as percentage of revenue:
```
NWC = Revenue x NWC%
```

---

## Discounting Conventions

### Mid-Year Convention

Assumes cash flows occur mid-year, not year-end:

```
Discount Factor = 1 / (1 + WACC)^(t - 0.5)

Year 1: 1 / (1 + WACC)^0.5
Year 2: 1 / (1 + WACC)^1.5
...
```

More realistic for evenly distributed cash flows throughout the year.

### Stub Period

For partial-year projections (model built mid-fiscal year):

```
Days remaining = Days from model date to fiscal year end
Stub discount = Days remaining / 365
```

---

## Sensitivity Analysis

### 2-Variable Data Table

Standard sensitivities:
1. **WACC vs Terminal Growth**
2. **WACC vs Exit Multiple**
3. **Revenue Growth vs EBIT Margin**

### Scenario Analysis

| Driver | Bear | Base | Bull |
|--------|------|------|------|
| Revenue CAGR | -2% | +5% | +10% |
| Terminal Margin | 12% | 15% | 18% |
| CapEx % Revenue | 8% | 6% | 5% |
| WACC | 10% | 9% | 8% |
| Terminal Growth | 2% | 2.5% | 3% |

---

## Sanity Checks

### 1. Balance Sheet Balances
```
Assets = Liabilities + Equity
```

### 2. Cash Flow Ties to Balance Sheet
```
Ending Cash = Beginning Cash + CFO + CFI + CFF
```

### 3. Terminal Growth < WACC
```
If g >= WACC, terminal value is undefined
```

### 4. Implied Metrics Reasonable
```
Implied EV/EBITDA in line with comps
Implied P/E in line with comps
ROIC converges to WACC in terminal year (no excess returns)
```

### 5. Terminal Value % of Total

If TV > 80% of enterprise value, either:
- Explicit forecast period too short
- Terminal assumptions too aggressive
- Consider longer projection period

---

## Common Pitfalls

1. **Double-counting:** Don't include interest expense in FCF (already in WACC)
2. **Wrong tax rate:** Use marginal rate for projections, not effective historical
3. **Circular reference:** Interest on debt depends on debt which depends on cash which depends on CFO
4. **Forgetting non-operating items:** Add back excess cash, subtract minority interest
5. **Terminal growth > GDP:** Implies company becomes infinite share of economy
6. **Ignoring optionality:** DCF doesn't capture options, flexibility, or real options value
7. **Static capital structure:** WACC should reflect target, not current structure

---

## Industry Adjustments

### Technology
- Higher growth rates acceptable
- Lower CapEx intensity
- Consider stock compensation in cash flow
- SaaS: ARR growth, retention, CAC/LTV

### Financial Services
- Use dividend discount model instead of DCF
- Or P/E, P/Book multiples
- ROE and cost of equity are key metrics

### Real Estate
- Use NAV (Net Asset Value) approach
- Cap rate = NOI / Property Value
- AFFO (Adjusted Funds from Operations) for REITs

### Cyclical Industries
- Normalize through-cycle earnings
- Consider replacement cost floor
- Multiple scenarios for different cycle positions
