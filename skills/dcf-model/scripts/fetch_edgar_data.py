#!/usr/bin/env python3
"""
SEC EDGAR Data Fetcher

Fetches financial data from SEC EDGAR API for DCF modeling.
Rate limited to 10 requests/second per SEC guidelines.
"""

import json
import time
import urllib.request
import urllib.error
import ssl
import sys
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class CompanyInfo:
    """Company metadata from SEC EDGAR."""
    cik: str
    name: str
    ticker: str
    sic: str
    sic_description: str
    fiscal_year_end: str
    state_of_incorporation: str
    filings: list


@dataclass
class FinancialFact:
    """Single financial fact from XBRL data."""
    concept: str
    label: str
    value: float
    unit: str
    start: Optional[str]
    end: str
    form: str
    filed: str
    frame: Optional[str]


class EdgarFetcher:
    """Fetches data from SEC EDGAR with rate limiting."""

    BASE_URL = "https://data.sec.gov"
    USER_AGENT = "DCF-Model-Skill contact@example.com"  # SEC requires identification
    RATE_LIMIT = 0.1  # 10 requests per second = 0.1s between requests

    def __init__(self, user_email: str = "contact@example.com"):
        self.user_agent = f"DCF-Model-Skill {user_email}"
        self._last_request_time = 0.0
        # Create SSL context for HTTPS requests
        self._ssl_context = ssl.create_default_context()
        # Fallback for environments with certificate issues
        try:
            import certifi
            self._ssl_context.load_verify_locations(certifi.where())
        except ImportError:
            pass

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT:
            time.sleep(self.RATE_LIMIT - elapsed)
        self._last_request_time = time.time()

    def _fetch(self, url: str) -> dict:
        """Fetch JSON from SEC EDGAR with rate limiting."""
        self._rate_limit()

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=30, context=self._ssl_context) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Company not found: {url}")
            raise RuntimeError(f"SEC EDGAR API error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error: {e.reason}")

    def normalize_cik(self, cik: str) -> str:
        """Normalize CIK to 10-digit zero-padded format."""
        return cik.zfill(10)

    def lookup_by_ticker(self, ticker: str) -> str:
        """Look up CIK from ticker symbol using SEC company tickers JSON."""
        # Note: company_tickers.json is at www.sec.gov, not data.sec.gov
        url = "https://www.sec.gov/files/company_tickers.json"
        data = self._fetch(url)

        ticker_upper = ticker.upper()
        for entry in data.values():
            if entry.get("ticker") == ticker_upper:
                return self.normalize_cik(str(entry["cik_str"]))

        raise ValueError(f"Ticker '{ticker}' not found in SEC database")

    def get_company_info(self, cik: str) -> CompanyInfo:
        """Fetch company metadata and filing history."""
        cik = self.normalize_cik(cik)
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        data = self._fetch(url)

        filings = []
        recent = data.get("filings", {}).get("recent", {})
        if recent:
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])
            for i, form in enumerate(forms):
                if form in ("10-K", "10-Q", "8-K"):
                    filings.append({
                        "form": form,
                        "date": dates[i] if i < len(dates) else None,
                        "accession": accessions[i] if i < len(accessions) else None
                    })

        return CompanyInfo(
            cik=cik,
            name=data.get("name", ""),
            ticker=data.get("tickers", [""])[0] if data.get("tickers") else "",
            sic=data.get("sic", ""),
            sic_description=data.get("sicDescription", ""),
            fiscal_year_end=data.get("fiscalYearEnd", ""),
            state_of_incorporation=data.get("stateOfIncorporation", ""),
            filings=filings[:20]  # Last 20 relevant filings
        )

    def get_company_facts(self, cik: str) -> dict:
        """Fetch all XBRL facts for a company."""
        cik = self.normalize_cik(cik)
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        return self._fetch(url)

    def extract_financial_data(self, cik: str, years: int = 5) -> dict:
        """
        Extract structured financial data for DCF modeling.

        Returns dict with:
        - income_statement: Revenue, COGS, OpEx, EBIT, Interest, Taxes, Net Income
        - balance_sheet: Assets, Liabilities, Equity, Working Capital items
        - cash_flow: CFO, CapEx, D&A, Changes in Working Capital
        """
        facts_data = self.get_company_facts(cik)

        # Extract facts from us-gaap taxonomy
        us_gaap = facts_data.get("facts", {}).get("us-gaap", {})

        # Key XBRL concepts for DCF modeling
        income_concepts = {
            "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                       "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
            "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
            "gross_profit": ["GrossProfit"],
            "operating_expenses": ["OperatingExpenses"],
            "operating_income": ["OperatingIncomeLoss"],
            "interest_expense": ["InterestExpense", "InterestExpenseDebt"],
            "income_before_tax": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"],
            "income_tax": ["IncomeTaxExpenseBenefit"],
            "net_income": ["NetIncomeLoss", "ProfitLoss"]
        }

        balance_concepts = {
            "total_assets": ["Assets"],
            "current_assets": ["AssetsCurrent"],
            "cash": ["CashAndCashEquivalentsAtCarryingValue", "Cash"],
            "accounts_receivable": ["AccountsReceivableNetCurrent"],
            "inventory": ["InventoryNet"],
            "total_liabilities": ["Liabilities"],
            "current_liabilities": ["LiabilitiesCurrent"],
            "accounts_payable": ["AccountsPayableCurrent"],
            "long_term_debt": ["LongTermDebt", "LongTermDebtNoncurrent"],
            "total_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]
        }

        cashflow_concepts = {
            "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
            "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
            "depreciation": ["DepreciationDepletionAndAmortization", "Depreciation"],
            "amortization": ["AmortizationOfIntangibleAssets"]
        }

        def extract_concept_values(concepts_dict: dict) -> dict:
            """Extract values for a set of concepts."""
            result = {}
            for key, concept_names in concepts_dict.items():
                values = []
                for concept in concept_names:
                    if concept in us_gaap:
                        units = us_gaap[concept].get("units", {})
                        # Prefer USD values
                        usd_values = units.get("USD", [])
                        for val in usd_values:
                            # Only annual data (10-K forms)
                            if val.get("form") == "10-K":
                                values.append({
                                    "value": val.get("val"),
                                    "end": val.get("end"),
                                    "start": val.get("start"),
                                    "filed": val.get("filed"),
                                    "frame": val.get("frame")
                                })
                        if values:
                            break  # Use first matching concept

                # Sort by end date and take most recent years
                values.sort(key=lambda x: x.get("end", ""), reverse=True)
                result[key] = values[:years]

            return result

        return {
            "company_cik": cik,
            "income_statement": extract_concept_values(income_concepts),
            "balance_sheet": extract_concept_values(balance_concepts),
            "cash_flow": extract_concept_values(cashflow_concepts)
        }

    def identify_missing_fields(self, financial_data: dict) -> list:
        """Identify fields that are missing from the extracted data."""
        missing = []

        required_income = ["revenue", "operating_income", "net_income"]
        required_balance = ["total_assets", "total_liabilities", "total_equity",
                          "accounts_receivable", "inventory", "accounts_payable"]
        required_cashflow = ["operating_cash_flow", "capex", "depreciation"]

        for field in required_income:
            if not financial_data.get("income_statement", {}).get(field):
                missing.append(f"income_statement.{field}")

        for field in required_balance:
            if not financial_data.get("balance_sheet", {}).get(field):
                missing.append(f"balance_sheet.{field}")

        for field in required_cashflow:
            if not financial_data.get("cash_flow", {}).get(field):
                missing.append(f"cash_flow.{field}")

        return missing


def main():
    """CLI interface for fetching EDGAR data."""
    if len(sys.argv) < 2:
        print("Usage: fetch_edgar_data.py <ticker_or_cik> [email] [years]")
        print("Example: fetch_edgar_data.py AAPL user@example.com 5")
        sys.exit(1)

    identifier = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "user@example.com"
    years = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    fetcher = EdgarFetcher(user_email=email)

    # Determine if CIK or ticker
    if identifier.isdigit():
        cik = fetcher.normalize_cik(identifier)
    else:
        print(f"Looking up ticker: {identifier}")
        cik = fetcher.lookup_by_ticker(identifier)
        print(f"Found CIK: {cik}")

    # Fetch company info
    print(f"\nFetching company info...")
    company = fetcher.get_company_info(cik)
    print(f"Company: {company.name} ({company.ticker})")
    print(f"Industry: {company.sic_description}")
    print(f"Fiscal Year End: {company.fiscal_year_end}")

    # Fetch financial data
    print(f"\nFetching financial data for last {years} years...")
    data = fetcher.extract_financial_data(cik, years)

    # Check for missing fields
    missing = fetcher.identify_missing_fields(data)
    if missing:
        print(f"\nMissing required fields:")
        for field in missing:
            print(f"  - {field}")

    # Output JSON
    output = {
        "company": asdict(company),
        "financial_data": data,
        "missing_fields": missing
    }

    output_file = f"{company.ticker or cik}_edgar_data.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nData saved to: {output_file}")


if __name__ == "__main__":
    main()
