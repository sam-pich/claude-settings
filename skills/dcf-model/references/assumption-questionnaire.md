# DCF Assumption Questionnaire

## Overview

This questionnaire collects all assumptions needed for a complete DCF model. Questions are grouped by category and ordered by dependency (earlier questions inform later ones).

**Key principle:** Do not use defaults. Prompt user for all values. Historical data provides reference points but the user must confirm or adjust assumptions.

---

## Phase 1: Model Configuration

### Q1.1 Basic Setup

| Question | Options/Format | Required |
|----------|---------------|----------|
| Company identifier (ticker or CIK) | Text | Yes |
| DCF type | Unlevered (WACC) / Levered (Equity) | Yes |
| Model complexity | 2-stage / 3-stage / LBO-style | Yes |
| Projection period (years) | Number: 5-10 | Yes |
| Historical data years | Number: 3-5 | Yes |

### Q1.2 Terminal Value Method

| Question | Options | Required |
|----------|---------|----------|
| Terminal value method | Perpetuity growth / Exit multiple / Both | Yes |

---

## Phase 2: Revenue Assumptions

### Q2.1 Revenue Growth

Present historical growth rates first:
```
Historical Revenue Growth:
  FY2022: +8.2%
  FY2023: +5.4%
  FY2024: -2.1%
  3-year average: +3.8%
```

| Question | Format | Required |
|----------|--------|----------|
| Year 1 revenue growth rate | Percentage | Yes |
| Year 2 revenue growth rate | Percentage | Yes |
| Year 3 revenue growth rate | Percentage | Yes |
| Year 4 revenue growth rate (if projecting 4+ years) | Percentage | Conditional |
| Year 5 revenue growth rate (if projecting 5+ years) | Percentage | Conditional |
| How should growth rates transition to terminal growth? | Linear / Step-down / Custom | If 3-stage |
| Terminal/perpetuity growth rate | Percentage (0-4%) | Yes |

### Q2.2 Revenue Drivers (Bottom-Up, Optional)

For more granular models:

| Question | Format | Required |
|----------|--------|----------|
| Model revenue by segment? | Yes/No | Optional |
| Segment 1 name | Text | If yes |
| Segment 1 FY1 revenue | Dollar amount | If yes |
| Segment 1 growth rate | Percentage | If yes |
| (Repeat for each segment) | | |

For unit economics approach:

| Question | Format | Required |
|----------|--------|----------|
| Number of customers/units (current) | Number | Optional |
| Customer/unit growth rate | Percentage | Optional |
| Average revenue per customer/unit | Dollar amount | Optional |
| Price growth rate | Percentage | Optional |

---

## Phase 3: Cost Assumptions

### Q3.1 Cost of Revenue

Present historical margins first:
```
Historical Gross Margin:
  FY2022: 43.2%
  FY2023: 44.1%
  FY2024: 42.8%
  Average: 43.4%
```

| Question | Format | Required |
|----------|--------|----------|
| Target gross margin (or COGS % of revenue) | Percentage | Yes |
| Should margin improve over projection period? | Yes/No | No |
| Terminal year gross margin (if improving) | Percentage | If improving |

### Q3.2 Operating Expenses

Present historical OpEx breakdown:
```
Historical OpEx as % of Revenue:
  R&D: 15.2%
  SG&A: 12.4%
  Other: 2.1%
  Total: 29.7%
```

| Question | Format | Required |
|----------|--------|----------|
| R&D expense as % of revenue | Percentage | Yes |
| SG&A expense as % of revenue | Percentage | Yes |
| Other operating expenses as % of revenue | Percentage | Yes |
| Operating leverage: should OpEx % decline as revenue grows? | Yes/No | No |
| Terminal year total OpEx % (if declining) | Percentage | If yes |

### Q3.3 Target Margins

| Question | Format | Required |
|----------|--------|----------|
| Target EBIT margin (or calculate from above) | Percentage | Optional |
| Target EBITDA margin | Percentage | Optional |

---

## Phase 4: Working Capital

### Q4.1 Working Capital Days

Present historical metrics:
```
Historical Working Capital Days:
  DSO (Days Sales Outstanding): 45 days
  DIO (Days Inventory Outstanding): 38 days
  DPO (Days Payables Outstanding): 62 days
  Cash Conversion Cycle: 21 days
```

| Question | Format | Required |
|----------|--------|----------|
| Days Sales Outstanding (DSO) | Days (0-120) | Yes |
| Days Inventory Outstanding (DIO) | Days (0-180) | Yes |
| Days Payables Outstanding (DPO) | Days (0-120) | Yes |

### Q4.2 Other Working Capital Items

| Question | Format | Required |
|----------|--------|----------|
| Prepaid expenses as % of revenue | Percentage | Optional |
| Other current assets as % of revenue | Percentage | Optional |
| Accrued expenses as % of revenue | Percentage | Optional |
| Other current liabilities as % of revenue | Percentage | Optional |

---

## Phase 5: Capital Expenditures

### Q5.1 CapEx Assumptions

Present historical data:
```
Historical CapEx:
  CapEx as % of Revenue: 4.2%
  CapEx / D&A ratio: 1.1x
  D&A as % of Revenue: 3.8%
```

| Question | Format | Required |
|----------|--------|----------|
| CapEx as % of revenue | Percentage | Yes |
| Or: Maintenance CapEx as % of D&A | Percentage | Alternative |
| Growth CapEx as % of revenue growth | Percentage | Alternative |
| D&A as % of prior year PP&E | Percentage | Yes |

### Q5.2 CapEx Detail (Optional)

| Question | Format | Required |
|----------|--------|----------|
| Break out maintenance vs growth CapEx? | Yes/No | Optional |
| Maintenance CapEx amount or % | Dollar or % | If yes |
| Growth CapEx drivers | Text description | If yes |

---

## Phase 6: Capital Structure

### Q6.1 Cost of Equity Inputs

| Question | Format | Required |
|----------|--------|----------|
| Risk-free rate (10-year Treasury yield) | Percentage | Yes |
| Equity risk premium | Percentage (typically 5-6%) | Yes |
| Company beta (levered) | Number (0.5-3.0) | Yes |
| Source of beta | Bloomberg / CAPM calc / Industry avg | Info only |

### Q6.2 Cost of Debt Inputs (for Unlevered DCF)

| Question | Format | Required |
|----------|--------|----------|
| Target debt-to-equity ratio | Ratio (e.g., 0.5) | If unlevered |
| Pre-tax cost of debt | Percentage | If unlevered |
| Or: Credit rating for spread lookup | AAA to CCC | Alternative |
| Marginal tax rate | Percentage | Yes |

### Q6.3 For Levered DCF Only

| Question | Format | Required |
|----------|--------|----------|
| Current debt balance | Dollar amount | If levered |
| Debt repayment schedule | Amortization or custom | If levered |
| New debt issuance assumed? | Yes/No | If levered |

---

## Phase 7: Terminal Value

### Q7.1 Perpetuity Growth Method

| Question | Format | Required |
|----------|--------|----------|
| Long-term/perpetuity growth rate | Percentage (0-4%) | If perpetuity |
| Rationale for growth rate selection | Text | Optional |

Validation: Growth rate must be less than WACC.

### Q7.2 Exit Multiple Method

Present comparable company multiples:
```
Trading Comparables (EV/EBITDA):
  Peer 1: 12.5x
  Peer 2: 10.8x
  Peer 3: 14.2x
  Average: 12.5x
  Median: 12.5x
```

| Question | Format | Required |
|----------|--------|----------|
| Exit EBITDA multiple | Multiple (e.g., 10.0x) | If exit multiple |
| Rationale for multiple selection | Text | Optional |

### Q7.3 Cross-Check

If using both methods:
| Question | Format | Required |
|----------|--------|----------|
| Which method to use for base case? | Perpetuity / Exit multiple / Average | If both |

---

## Phase 8: Scenario Analysis

### Q8.1 Scenario Setup

| Question | Options | Required |
|----------|---------|----------|
| Include scenario analysis? | Yes/No | Recommended |
| Number of scenarios | 3 (Bear/Base/Bull) or Custom | If yes |

### Q8.2 Scenario Drivers

For each scenario (Bull, Bear):

| Question | Format | Required |
|----------|--------|----------|
| Revenue CAGR adjustment vs base | Percentage | If scenarios |
| Margin adjustment vs base | Percentage points | If scenarios |
| WACC adjustment vs base | Percentage points | If scenarios |
| Terminal growth/multiple adjustment | Varies | If scenarios |

Example scenarios:
```
| Driver | Bear | Base | Bull |
|--------|------|------|------|
| Revenue CAGR | 2% | 5% | 8% |
| Terminal EBIT Margin | 12% | 15% | 18% |
| WACC | 10% | 9% | 8% |
| Terminal Growth | 2% | 2.5% | 3% |
```

---

## Phase 9: Additional Inputs

### Q9.1 Shares and Current Price

| Question | Format | Required |
|----------|--------|----------|
| Shares outstanding (diluted) | Number | Yes |
| Current stock price | Dollar amount | For comparison |
| Include stock-based compensation dilution? | Yes/No | Optional |

### Q9.2 Balance Sheet Adjustments

| Question | Format | Required |
|----------|--------|----------|
| Cash and equivalents (current) | Dollar amount | Yes |
| Total debt (current) | Dollar amount | Yes |
| Minority interest to subtract | Dollar amount | If applicable |
| Non-operating assets to add | Dollar amount | If applicable |

---

## Question Flow Logic

```
START
  |
  v
[Phase 1: Model Config]
  |
  v
[Phase 2: Revenue] <-- Historical data displayed
  |
  v
[Phase 3: Costs] <-- Historical margins displayed
  |
  v
[Phase 4: Working Capital] <-- Historical days displayed
  |
  v
[Phase 5: CapEx] <-- Historical ratios displayed
  |
  v
[Phase 6: Capital Structure]
  |
  +--> If Unlevered: Ask WACC components
  |
  +--> If Levered: Ask debt schedule
  |
  v
[Phase 7: Terminal Value]
  |
  +--> If Perpetuity: Ask growth rate
  |
  +--> If Exit Multiple: Show comps, ask multiple
  |
  v
[Phase 8: Scenarios] (Optional)
  |
  v
[Phase 9: Additional Inputs]
  |
  v
[VALIDATION] --> If errors: Loop back to fix
  |
  v
END --> Generate model
```

---

## Handling Missing Data

If historical data is incomplete, prompt user explicitly:

```
Historical data for [Inventory] is not available from SEC filings.

Please provide:
1. Current inventory balance: $______
2. Historical inventory balance (1 year ago): $______

Or indicate if this company has no inventory (e.g., service business): [Yes/No]
```

Never auto-fill with defaults. Always ask.

---

## Assumption Summary Template

After collecting all inputs, present summary for confirmation:

```
=== DCF Model Assumptions Summary ===

Company: [TICKER] - [Company Name]
DCF Type: Unlevered (WACC)
Projection Period: 5 years
Terminal Method: Perpetuity Growth

REVENUE
  Y1 Growth: 8.0%
  Y2 Growth: 6.0%
  Y3 Growth: 5.0%
  Y4 Growth: 4.0%
  Y5 Growth: 3.5%
  Terminal: 2.5%

MARGINS
  Gross Margin: 43.0%
  EBIT Margin: 15.0% (improving to 17.0%)

CAPITAL
  WACC: 9.2%
    Cost of Equity: 10.5%
    Cost of Debt (after-tax): 4.2%
    Target D/E: 0.3x

TERMINAL VALUE
  Perpetuity Growth: 2.5%
  Implied EV/EBITDA: 11.2x

Please confirm these assumptions are correct: [Yes/Edit]
```
