---
name: dcf-model
description: Generate professional Discounted Cash Flow (DCF) valuation models in Excel. Use when asked to create a DCF model, company valuation, intrinsic value analysis, or financial model for a public company. Integrates with SEC EDGAR for historical financial data and produces multi-tab Excel workbooks with Unlevered FCF (WACC) or Levered FCF (Equity) analysis, sensitivity tables, and scenario analysis.
---

# DCF Model Generator

Generate industry-quality DCF valuation models in Excel, integrating SEC EDGAR data with the `xlsx` skill.

## Workflow

Execute these phases sequentially. Do not skip steps or use defaults - prompt user for all assumptions.

### Phase 1: Model Configuration

Ask user for:
1. **Company identifier** - Ticker symbol (e.g., AAPL) or CIK number
2. **DCF type** - Unlevered FCF (WACC) or Levered FCF (Equity)
3. **Complexity** - 2-stage, 3-stage, or LBO-style
4. **Projection period** - Number of years (5-10)
5. **Terminal value method** - Perpetuity growth, exit multiple, or both
6. **Historical years** - Number of years to display (3-5)

### Phase 2: Data Acquisition

1. Run `scripts/fetch_edgar_data.py` with company identifier:
   ```bash
   python3 scripts/fetch_edgar_data.py TICKER user@email.com 5
   ```

2. Run `scripts/parse_financial_statements.py` on the output:
   ```bash
   python3 scripts/parse_financial_statements.py TICKER_edgar_data.json
   ```

3. Run `scripts/calculate_metrics.py` for historical metrics:
   ```bash
   python3 scripts/calculate_metrics.py TICKER_parsed_financials.json
   ```

4. Review output for missing fields. If data is missing, prompt user:
   ```
   Historical [field] data is not available from SEC filings.
   Please provide the value or indicate if not applicable.
   ```

### Phase 3: Assumption Gathering

Present historical metrics and prompt for each assumption category. See `references/assumption-questionnaire.md` for complete question list.

**Revenue assumptions:**
- Display historical growth rates
- Ask for Y1-Y5 growth rates
- Ask for terminal growth rate (must be < WACC)

**Cost assumptions:**
- Display historical margins
- Ask for target gross margin
- Ask for OpEx breakdown (R&D %, SG&A %, Other %)

**Working capital:**
- Display historical DSO, DIO, DPO
- Ask for projection assumptions

**CapEx:**
- Display historical CapEx/Revenue
- Ask for projection % of revenue

**Capital structure:**
- Ask for risk-free rate (current 10Y Treasury)
- Ask for equity risk premium (typically 5-6%)
- Ask for company beta
- For unlevered DCF: ask for target D/E, cost of debt

**Terminal value:**
- If perpetuity: ask for growth rate
- If exit multiple: show comp multiples, ask for selected multiple

Run `scripts/validate_assumptions.py` on collected assumptions before proceeding.

### Phase 4: Excel Construction

Invoke the `xlsx` skill to build the workbook. Reference `references/excel-architecture.md` for detailed tab structure and `assets/dcf_structure.json` for schema.

**Tab structure:**
1. **Cover** - Company name, date, model type, disclaimer
2. **Summary** - Dashboard with implied share price, key metrics
3. **Assumptions** - All inputs (blue text), organized by category
4. **Historical** - Historical data from EDGAR with computed metrics
5. **Projections** - Income statement, balance sheet, cash flow forecasts
6. **DCF Valuation** - FCF build-up, discounting, terminal value, equity value
7. **Sensitivity** - 2-variable data tables (WACC vs growth, WACC vs multiple)
8. **Supporting** - D&A schedule, debt schedule, working capital detail

**Color coding:**
- Blue text (0, 0, 255): User inputs
- Black text: Formulas
- Green text (0, 128, 0): Cross-sheet links
- Yellow fill: Key assumptions needing attention

**Key formulas:**
```
WACC = We * Ke + Wd * Kd * (1 - T)
Unlevered FCF = NOPAT + D&A - CapEx - Change in NWC
TV (Perpetuity) = Terminal FCF * (1 + g) / (WACC - g)
TV (Exit Multiple) = Terminal EBITDA * Exit Multiple
```

### Phase 5: Verification

Before delivery:
1. Run Excel recalculation
2. Check for formula errors (#REF!, #DIV/0!, etc.)
3. Verify balance sheet balances (Assets = L + E)
4. Verify cash flow ties to balance sheet
5. Check terminal growth < WACC
6. Present valuation summary to user

Output summary:
```
DCF Valuation Summary - [Company Name]

Enterprise Value: $XXX.X B
Less: Net Debt: $XX.X B
Equity Value: $XXX.X B
Shares Outstanding: X.X B
Implied Share Price: $XX.XX

Current Price: $XX.XX
Upside/(Downside): XX.X%

Terminal Value: XX% of Enterprise Value
Implied Exit EV/EBITDA: XX.Xx
```

## Reference Documents

- **Excel structure**: `references/excel-architecture.md` - Tab layouts, formulas, formatting
- **SEC EDGAR API**: `references/sec-edgar-api.md` - XBRL tags, endpoints, data extraction
- **DCF methodology**: `references/dcf-methodology.md` - Formulas, theory, sanity checks
- **Assumption questionnaire**: `references/assumption-questionnaire.md` - Complete question list

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `fetch_edgar_data.py` | Fetch SEC EDGAR data | `python3 fetch_edgar_data.py TICKER email years` |
| `parse_financial_statements.py` | Transform XBRL to model format | `python3 parse_financial_statements.py input.json` |
| `calculate_metrics.py` | Compute historical metrics | `python3 calculate_metrics.py parsed.json` |
| `validate_assumptions.py` | Validate assumption completeness | `python3 validate_assumptions.py assumptions.json` |

## Key Constraints

1. **No defaults** - Always prompt user for missing data
2. **Online only** - Fetch fresh EDGAR data each time
3. **Terminal growth < WACC** - Validate before generating model
4. **Balance sheet must balance** - Include error check formulas
5. **Use xlsx skill** - For professional Excel generation with formulas
