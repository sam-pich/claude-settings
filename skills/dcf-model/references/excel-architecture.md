# DCF Model Excel Architecture

## Workbook Structure

### Tab Overview

| Tab | Purpose | Key Elements |
|-----|---------|--------------|
| Cover | Model identification | Company, date, analyst, model type, disclaimer |
| Summary | Valuation dashboard | Implied share price, football field, key metrics |
| Assumptions | All inputs | Organized by category, blue text for inputs |
| Historical | Historical financials | 3-5 years data with computed metrics |
| Projections | Forecast model | IS/BS/CF integrated projections |
| DCF Valuation | Core valuation | FCF, discount factors, NPV, terminal value |
| Sensitivity | Analysis tables | 2-var data tables, scenario toggles |
| Supporting | Detail schedules | D&A, debt, working capital |

---

## Color Coding Convention

| Color | RGB | Use |
|-------|-----|-----|
| Blue text | (0, 0, 255) | User inputs - hardcoded values |
| Black text | (0, 0, 0) | Formulas |
| Green text | (0, 128, 0) | Links to other sheets |
| Yellow fill | (255, 255, 0) | Key assumptions needing review |
| Light gray fill | (242, 242, 242) | Headers and labels |
| Light blue fill | (221, 235, 247) | Calculated subtotals |

---

## Tab Specifications

### 1. Cover Tab

```
Row 1-3:   [Blank - spacing]
Row 4:     Company Name (large, bold)
Row 5:     Ticker: [TICKER]
Row 6:     [Blank]
Row 7:     Discounted Cash Flow Analysis
Row 8:     Model Type: [Unlevered FCF / Levered FCF]
Row 9:     [Blank]
Row 10:    Prepared: [Date]
Row 11:    [Blank]
Row 12-15: Disclaimer text (small, italic)
```

### 2. Summary Tab

Structure:
- A1:F1 = Header row
- A3:F8 = Key Valuation Metrics table
- A10:F20 = Sensitivity summary (mini data table)
- H3:M15 = "Football Field" valuation range chart data

Key Metrics Section:
```
| Metric | Base | Bull | Bear |
|--------|------|------|------|
| Enterprise Value | =DCF!EV | =Scenarios!Bull_EV | =Scenarios!Bear_EV |
| Less: Net Debt | ='Historical'!NetDebt | | |
| Equity Value | =EV-NetDebt | | |
| Shares Outstanding | ='Assumptions'!Shares | | |
| Implied Share Price | =EquityValue/Shares | | |
| Current Price | ='Assumptions'!CurrentPrice | | |
| Upside/(Downside) | =(Implied-Current)/Current | | |
```

### 3. Assumptions Tab

Section Layout:

**A. Model Configuration (Rows 3-10)**
```
Row 3:  Model Configuration [Header]
Row 4:  DCF Type: [dropdown: Unlevered/Levered]
Row 5:  Complexity: [dropdown: 2-stage/3-stage/LBO]
Row 6:  Projection Years: [5-10]
Row 7:  Terminal Method: [dropdown: Perpetuity/Exit Multiple/Both]
Row 8:  Historical Years: [3-5]
```

**B. Revenue Assumptions (Rows 12-25)**
```
Row 12: Revenue Assumptions [Header]
Row 13: [Year headers: Y1, Y2, Y3, Y4, Y5, Terminal]
Row 14: Revenue Growth Rate: [inputs per year]
Row 15: Terminal Growth: [input]
Row 16-25: Segment breakdown (if applicable)
```

**C. Cost Assumptions (Rows 27-40)**
```
Row 27: Cost Assumptions [Header]
Row 28: Gross Margin Target: [input]
Row 29: COGS % Revenue: =1-GrossMargin
Row 30: R&D % Revenue: [input]
Row 31: SG&A % Revenue: [input]
Row 32: Other OpEx % Revenue: [input]
Row 33: Total OpEx % Revenue: =SUM(R&D+SG&A+Other)
```

**D. Working Capital (Rows 42-50)**
```
Row 42: Working Capital [Header]
Row 43: DSO (Days): [input]
Row 44: DIO (Days): [input]
Row 45: DPO (Days): [input]
Row 46: Other Current Assets % Rev: [input]
Row 47: Other Current Liab % Rev: [input]
```

**E. Capital Expenditure (Rows 52-58)**
```
Row 52: Capital Expenditure [Header]
Row 53: CapEx % Revenue: [input]
Row 54: D&A % Prior Year PPE: [input]
Row 55: Maintenance CapEx: [calculated]
Row 56: Growth CapEx: [calculated]
```

**F. Capital Structure (Rows 60-75)**
```
Row 60: Capital Structure [Header]
Row 61: Risk-Free Rate: [input]
Row 62: Equity Risk Premium: [input]
Row 63: Beta (Levered): [input]
Row 64: Cost of Equity: =Rf + Beta * ERP
Row 65: [blank]
Row 66: Target D/E Ratio: [input]
Row 67: Cost of Debt (Pre-tax): [input]
Row 68: Tax Rate: [input]
Row 69: Cost of Debt (After-tax): =Kd*(1-Tax)
Row 70: [blank]
Row 71: Weight of Equity: =1/(1+D/E)
Row 72: Weight of Debt: =D/E/(1+D/E)
Row 73: WACC: =We*Ke + Wd*Kd_aftertax
```

**G. Terminal Value (Rows 77-85)**
```
Row 77: Terminal Value [Header]
Row 78: Perpetuity Growth Rate: [input]
Row 79: Exit EBITDA Multiple: [input]
Row 80: [blank]
Row 81: TV (Perpetuity): =Terminal_FCF*(1+g)/(WACC-g)
Row 82: TV (Exit Multiple): =Terminal_EBITDA * Multiple
Row 83: TV (Selected): [based on method selection]
```

### 4. Historical Tab

Structure - Years in columns (C onwards), metrics in rows:

```
     | A (Label) | B (Units) | C (Y-5) | D (Y-4) | E (Y-3) | F (Y-2) | G (Y-1) |
-----|-----------|-----------|---------|---------|---------|---------|---------|
  3  | INCOME STATEMENT |    |         |         |         |         |         |
  4  | Revenue   | $M        | [data]  | [data]  | [data]  | [data]  | [data]  |
  5  | Growth    | %         | n/a     | [calc]  | [calc]  | [calc]  | [calc]  |
  6  | COGS      | $M        | [data]  | [data]  | [data]  | [data]  | [data]  |
  7  | Gross Profit | $M     | [calc]  | [calc]  | [calc]  | [calc]  | [calc]  |
  8  | Gross Margin | %      | [calc]  | [calc]  | [calc]  | [calc]  | [calc]  |
...
```

Key Sections:
1. Income Statement (rows 3-25)
2. Balance Sheet (rows 27-55)
3. Cash Flow Statement (rows 57-75)
4. Key Metrics (rows 77-95)

### 5. Projections Tab

Integrated 3-statement model with years in columns:

```
     | A (Label) | B (Y0 Actual) | C (Y1) | D (Y2) | ... | H (Terminal) |
```

**Income Statement Section:**
```
Revenue             = Prior * (1 + Growth)
COGS                = Revenue * COGS%
Gross Profit        = Revenue - COGS
R&D                 = Revenue * R&D%
SG&A                = Revenue * SG&A%
EBIT                = Gross Profit - R&D - SG&A
Interest            = Avg Debt * Cost of Debt
EBT                 = EBIT - Interest
Taxes               = EBT * Tax Rate
Net Income          = EBT - Taxes
```

**Balance Sheet Section:**
```
Cash                = Plug (from CF)
Accounts Receivable = Revenue * DSO / 365
Inventory           = COGS * DIO / 365
PP&E                = Prior PPE + CapEx - D&A
Total Assets        = Sum

Accounts Payable    = COGS * DPO / 365
Debt                = Prior + Issuance - Repayment
Total Liabilities   = Sum
Equity              = Prior + Net Income - Dividends
Total L+E           = Sum (should equal Assets)
```

**Cash Flow Section:**
```
Net Income          = Link
+ D&A               = D&A Schedule
- Change in WC      = Current - Prior WC
= Cash from Ops     = Sum

- CapEx             = Assumptions
= Cash from Invest  = Sum

+ Debt Issuance     = Schedule
- Debt Repayment    = Schedule
- Dividends         = Policy
= Cash from Fin     = Sum

Net Change in Cash  = CFO + CFI + CFF
```

### 6. DCF Valuation Tab

Core DCF calculation:

```
| Year | Y1 | Y2 | Y3 | Y4 | Y5 | Terminal |
|------|----|----|----|----|----|----|
| EBIT | =Proj!EBIT | | | | | |
| Less: Taxes | =EBIT*TaxRate | | | | | |
| NOPAT | =EBIT-Taxes | | | | | |
| Plus: D&A | =Proj!DA | | | | | |
| Less: CapEx | =Proj!CapEx | | | | | |
| Less: Change NWC | =Proj!dNWC | | | | | |
| Unlevered FCF | =NOPAT+DA-CapEx-dNWC | | | | | |
| | | | | | | |
| Discount Period | 0.5 | 1.5 | 2.5 | 3.5 | 4.5 | 4.5 |
| Discount Factor | =1/(1+WACC)^Period | | | | | |
| PV of FCF | =FCF*DF | | | | | |
| | | | | | | |
| Terminal Value | | | | | | =Formula |
| PV of TV | | | | | | =TV*DF |
| | | | | | | |
| Sum of PV FCFs | =SUM(PV_FCF) |
| Plus: PV of TV | =PV_TV |
| Enterprise Value | =Sum_PV + PV_TV |
| Less: Net Debt | =Debt - Cash |
| Equity Value | =EV - Net Debt |
| Shares Outstanding | =Assumptions!Shares |
| Implied Share Price | =Equity / Shares |
```

### 7. Sensitivity Tab

**2-Variable Data Table (WACC vs Terminal Growth):**

```
        | 1.5% | 2.0% | 2.5% | 3.0% | 3.5% |  <- Terminal Growth
--------|------|------|------|------|------|
8.0%    | [val]| [val]| [val]| [val]| [val]|
8.5%    | [val]| [val]| [val]| [val]| [val]|  <- WACC
9.0%    | [val]| [val]| [val]| [val]| [val]|
9.5%    | [val]| [val]| [val]| [val]| [val]|
10.0%   | [val]| [val]| [val]| [val]| [val]|
```

Formula in corner cell: `=DCF!ImpliedPrice`

**Scenario Toggle Section:**
```
Active Scenario: [dropdown: Base/Bull/Bear]

| Metric | Base | Bull | Bear |
|--------|------|------|------|
| Revenue CAGR | 8% | 12% | 4% |
| Terminal Margin | 15% | 18% | 12% |
| WACC | 9% | 8.5% | 10% |
| Terminal Growth | 2.5% | 3% | 2% |
| Implied Price | $XX | $XX | $XX |
```

### 8. Supporting Tab

**D&A Schedule:**
```
| Year | Opening PPE | CapEx | D&A | Closing PPE |
|------|-------------|-------|-----|-------------|
```

**Debt Schedule:**
```
| Year | Opening Debt | Issuance | Repayment | Interest | Closing |
|------|--------------|----------|-----------|----------|---------|
```

**Working Capital Detail:**
```
| Year | AR | Inventory | Prepaid | AP | Accrued | NWC | Change |
|------|----|-----------|---------|----|---------|-----|--------|
```

---

## Formula Patterns

### Named Ranges

Create these named ranges for cleaner formulas:
- `WACC` = Assumptions!$C$73
- `TaxRate` = Assumptions!$C$68
- `TerminalGrowth` = Assumptions!$C$78
- `ExitMultiple` = Assumptions!$C$79
- `ProjectionYears` = Assumptions!$C$6

### Key Formulas

**WACC:**
```excel
=We*Ke + Wd*Kd*(1-TaxRate)
```

**Unlevered FCF:**
```excel
=NOPAT + DA - CapEx - ChangeInNWC
```

**Terminal Value (Perpetuity):**
```excel
=TerminalFCF * (1 + TerminalGrowth) / (WACC - TerminalGrowth)
```

**Terminal Value (Exit Multiple):**
```excel
=TerminalEBITDA * ExitMultiple
```

**Discount Factor (Mid-Year Convention):**
```excel
=1 / (1 + WACC) ^ (Year - 0.5)
```

**Enterprise Value:**
```excel
=SUM(PV_of_FCFs) + PV_of_TerminalValue
```

**Equity Value:**
```excel
=EnterpriseValue - TotalDebt + Cash
```

---

## Cell Formatting

### Number Formats

| Type | Format | Example |
|------|--------|---------|
| Currency (millions) | `#,##0.0` | 1,234.5 |
| Percentage | `0.0%` | 12.5% |
| Multiple | `0.0x` | 8.5x |
| Years | `0` | 5 |
| Share price | `$#,##0.00` | $45.67 |

### Column Widths

| Column Type | Width |
|-------------|-------|
| Row labels | 25-30 |
| Year columns | 12-15 |
| Unit column | 8 |

---

## Data Validation

### Dropdowns

| Cell | Options |
|------|---------|
| DCF Type | Unlevered, Levered |
| Complexity | 2-stage, 3-stage, LBO |
| Terminal Method | Perpetuity, Exit Multiple, Both |
| Active Scenario | Base, Bull, Bear |

### Input Constraints

| Field | Min | Max |
|-------|-----|-----|
| Revenue Growth | -50% | 100% |
| Terminal Growth | 0% | 4% |
| WACC | 5% | 20% |
| Beta | 0.3 | 3.0 |
| Exit Multiple | 3x | 25x |

---

## Error Checking

Include these checks:
1. Balance sheet balances: `=IF(Assets=Liabilities+Equity,"OK","ERROR")`
2. Cash flow ties: `=IF(EndingCash=PriorCash+NetCashFlow,"OK","ERROR")`
3. Terminal growth < WACC: `=IF(g<WACC,"OK","ERROR: g >= WACC")`
4. Circular reference flag (if debt is modeled with interest)

---

## Print Setup

- Orientation: Landscape
- Fit to: 1 page wide by X pages tall
- Margins: 0.5" all sides
- Headers: Company Name | Tab Name | Page X of Y
- Gridlines: Off for presentation, On for working copy
