# SEC EDGAR API Reference

## Overview

SEC EDGAR provides free programmatic access to company filings and structured XBRL financial data. No API key required, but rate limiting and identification are enforced.

## Access Requirements

### Rate Limiting
- Maximum 10 requests per second
- Implement 100ms delay between requests
- Exceeding limits results in temporary IP blocks

### User-Agent Header (Required)
```
User-Agent: CompanyName AdminEmail@company.com
```
Example: `DCF-Model-Skill analyst@example.com`

Requests without proper User-Agent are blocked.

---

## Key Endpoints

### 1. Company Ticker Lookup

**URL:** `https://www.sec.gov/files/company_tickers.json` (Note: www.sec.gov, not data.sec.gov)

**Response:**
```json
{
  "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
  "1": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
  ...
}
```

**Usage:** Convert ticker to CIK for other API calls.

---

### 2. Company Submissions (Filings List)

**URL:** `https://data.sec.gov/submissions/CIK{cik}.json`

**CIK Format:** Zero-padded to 10 digits (e.g., `0000320193`)

**Response Structure:**
```json
{
  "cik": "320193",
  "entityType": "operating",
  "sic": "3571",
  "sicDescription": "Electronic Computers",
  "name": "Apple Inc.",
  "tickers": ["AAPL"],
  "exchanges": ["NASDAQ"],
  "fiscalYearEnd": "0930",
  "stateOfIncorporation": "CA",
  "filings": {
    "recent": {
      "accessionNumber": ["0000320193-23-000077", ...],
      "filingDate": ["2023-11-03", ...],
      "form": ["10-K", "10-Q", "8-K", ...],
      "primaryDocument": ["aapl-20230930.htm", ...]
    }
  }
}
```

**Key Fields:**
- `fiscalYearEnd`: MMDD format (e.g., "0930" = September 30)
- `sic`: Industry classification code
- `filings.recent`: Last ~1000 filings

---

### 3. Company Facts (XBRL Data)

**URL:** `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`

**Response Structure:**
```json
{
  "cik": 320193,
  "entityName": "Apple Inc.",
  "facts": {
    "us-gaap": {
      "Revenues": {
        "label": "Revenues",
        "description": "Amount of revenue...",
        "units": {
          "USD": [
            {
              "end": "2023-09-30",
              "val": 383285000000,
              "accn": "0000320193-23-000077",
              "form": "10-K",
              "filed": "2023-11-03",
              "frame": "CY2023"
            }
          ]
        }
      }
    },
    "dei": {
      "EntityCommonStockSharesOutstanding": {...}
    }
  }
}
```

**Taxonomies:**
- `us-gaap`: US GAAP financial concepts
- `dei`: Document and entity information
- `ifrs-full`: IFRS concepts (foreign filers)

---

## XBRL Concept Mappings

### Income Statement

| Line Item | Primary XBRL Concept | Alternatives |
|-----------|---------------------|--------------|
| Revenue | `Revenues` | `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet` |
| Cost of Revenue | `CostOfRevenue` | `CostOfGoodsAndServicesSold`, `CostOfGoodsSold` |
| Gross Profit | `GrossProfit` | (Calculate: Revenue - COGS) |
| R&D Expense | `ResearchAndDevelopmentExpense` | |
| SG&A Expense | `SellingGeneralAndAdministrativeExpense` | `GeneralAndAdministrativeExpense` |
| Operating Income | `OperatingIncomeLoss` | `IncomeLossFromOperations` |
| Interest Expense | `InterestExpense` | `InterestExpenseDebt` |
| Pre-tax Income | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | |
| Income Tax | `IncomeTaxExpenseBenefit` | |
| Net Income | `NetIncomeLoss` | `ProfitLoss` |

### Balance Sheet

| Line Item | Primary XBRL Concept | Alternatives |
|-----------|---------------------|--------------|
| Cash | `CashAndCashEquivalentsAtCarryingValue` | `Cash` |
| Short-term Investments | `ShortTermInvestments` | `MarketableSecuritiesCurrent` |
| Accounts Receivable | `AccountsReceivableNetCurrent` | `ReceivablesNetCurrent` |
| Inventory | `InventoryNet` | |
| Total Current Assets | `AssetsCurrent` | |
| PP&E Net | `PropertyPlantAndEquipmentNet` | |
| Goodwill | `Goodwill` | |
| Total Assets | `Assets` | |
| Accounts Payable | `AccountsPayableCurrent` | |
| Short-term Debt | `ShortTermBorrowings` | `DebtCurrent` |
| Total Current Liabilities | `LiabilitiesCurrent` | |
| Long-term Debt | `LongTermDebt` | `LongTermDebtNoncurrent` |
| Total Liabilities | `Liabilities` | |
| Retained Earnings | `RetainedEarningsAccumulatedDeficit` | |
| Total Equity | `StockholdersEquity` | `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` |

### Cash Flow Statement

| Line Item | Primary XBRL Concept |
|-----------|---------------------|
| D&A | `DepreciationDepletionAndAmortization` |
| Stock Compensation | `ShareBasedCompensation` |
| Cash from Operations | `NetCashProvidedByUsedInOperatingActivities` |
| CapEx | `PaymentsToAcquirePropertyPlantAndEquipment` |
| Acquisitions | `PaymentsToAcquireBusinessesNetOfCashAcquired` |
| Cash from Investing | `NetCashProvidedByUsedInInvestingActivities` |
| Dividends | `PaymentsOfDividends` |
| Stock Repurchases | `PaymentsForRepurchaseOfCommonStock` |
| Cash from Financing | `NetCashProvidedByUsedInFinancingActivities` |

### Entity Information (DEI)

| Item | XBRL Concept |
|------|--------------|
| Shares Outstanding | `EntityCommonStockSharesOutstanding` |
| Public Float | `EntityPublicFloat` |
| Fiscal Year End | `CurrentFiscalYearEndDate` |

---

## Data Extraction Patterns

### Getting Annual Data (10-K)

Filter facts by `form: "10-K"`:
```python
for val in facts["us-gaap"]["Revenues"]["units"]["USD"]:
    if val["form"] == "10-K":
        print(f"{val['end']}: ${val['val']:,.0f}")
```

### Getting Quarterly Data (10-Q)

Filter by `form: "10-Q"`:
```python
for val in facts["us-gaap"]["Revenues"]["units"]["USD"]:
    if val["form"] == "10-Q":
        print(f"{val['end']}: ${val['val']:,.0f}")
```

### Handling Period vs Point-in-Time

**Period data** (Income Statement, Cash Flow): Has `start` and `end` dates
```json
{"start": "2022-10-01", "end": "2023-09-30", "val": 383285000000}
```

**Point-in-time data** (Balance Sheet): Only has `end` date
```json
{"end": "2023-09-30", "val": 352583000000}
```

### Frame Reference

The `frame` field indicates the reporting period:
- `CY2023` = Calendar year 2023
- `CY2023Q3` = Q3 2023
- `CY2023Q3I` = Q3 2023 instantaneous (balance sheet)

---

## Common Issues

### 1. Missing Concepts

Not all companies use the same XBRL tags. Try alternative concepts:
```python
REVENUE_CONCEPTS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax"
]
```

### 2. Duplicate Values

Same metric reported in multiple filings (10-K contains Q4). Use `filed` date to get most recent:
```python
values.sort(key=lambda x: x['filed'], reverse=True)
```

### 3. Scale Differences

Most values are in USD (not thousands/millions). Check `units` field:
```json
"units": {
  "USD": [...],           // Full dollars
  "shares": [...]         // Share counts
}
```

### 4. Fiscal Year Alignment

Companies have different fiscal year ends. Use `end` date, not calendar year:
```python
fiscal_year = int(val['end'][:4])  # May not match calendar year
```

### 5. Restatements

Historical values may be restated. Use most recent `filed` date for each period:
```python
# Group by period end, keep most recently filed
by_period = {}
for val in values:
    end = val['end']
    if end not in by_period or val['filed'] > by_period[end]['filed']:
        by_period[end] = val
```

---

## Example: Fetching Apple's Revenue

```python
import urllib.request
import json

CIK = "0000320193"
URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

req = urllib.request.Request(
    URL,
    headers={"User-Agent": "MyApp contact@example.com"}
)

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())

revenue = data["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
annual = [v for v in revenue if v["form"] == "10-K"]
annual.sort(key=lambda x: x["end"], reverse=True)

for item in annual[:5]:
    print(f"{item['end']}: ${item['val']/1e9:.1f}B")
```

Output:
```
2023-09-30: $383.3B
2022-10-01: $394.3B
2021-09-25: $365.8B
2020-09-26: $274.5B
2019-09-28: $260.2B
```

---

## Resources

- [SEC EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [XBRL US GAAP Taxonomy](https://xbrl.us/us-gaap/)
- [Company Search](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
