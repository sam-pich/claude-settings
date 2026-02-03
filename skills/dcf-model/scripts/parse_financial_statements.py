#!/usr/bin/env python3
"""
Financial Statement Parser

Transforms raw SEC EDGAR XBRL data into standardized DCF model line items.
Handles different accounting conventions and normalizes data structure.
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class LineItem:
    """Standardized financial line item."""
    name: str
    values: dict = field(default_factory=dict)  # year -> value
    unit: str = "USD"
    source: str = "EDGAR"


@dataclass
class IncomeStatement:
    """Standardized income statement structure."""
    revenue: LineItem = field(default_factory=lambda: LineItem("Revenue"))
    cost_of_revenue: LineItem = field(default_factory=lambda: LineItem("Cost of Revenue"))
    gross_profit: LineItem = field(default_factory=lambda: LineItem("Gross Profit"))
    rd_expense: LineItem = field(default_factory=lambda: LineItem("R&D Expense"))
    sga_expense: LineItem = field(default_factory=lambda: LineItem("SG&A Expense"))
    operating_expenses: LineItem = field(default_factory=lambda: LineItem("Operating Expenses"))
    operating_income: LineItem = field(default_factory=lambda: LineItem("Operating Income (EBIT)"))
    interest_expense: LineItem = field(default_factory=lambda: LineItem("Interest Expense"))
    other_income: LineItem = field(default_factory=lambda: LineItem("Other Income/Expense"))
    pretax_income: LineItem = field(default_factory=lambda: LineItem("Pre-tax Income"))
    income_tax: LineItem = field(default_factory=lambda: LineItem("Income Tax Expense"))
    net_income: LineItem = field(default_factory=lambda: LineItem("Net Income"))


@dataclass
class BalanceSheet:
    """Standardized balance sheet structure."""
    # Assets
    cash: LineItem = field(default_factory=lambda: LineItem("Cash & Equivalents"))
    short_term_investments: LineItem = field(default_factory=lambda: LineItem("Short-term Investments"))
    accounts_receivable: LineItem = field(default_factory=lambda: LineItem("Accounts Receivable"))
    inventory: LineItem = field(default_factory=lambda: LineItem("Inventory"))
    prepaid_expenses: LineItem = field(default_factory=lambda: LineItem("Prepaid Expenses"))
    other_current_assets: LineItem = field(default_factory=lambda: LineItem("Other Current Assets"))
    total_current_assets: LineItem = field(default_factory=lambda: LineItem("Total Current Assets"))
    ppe_net: LineItem = field(default_factory=lambda: LineItem("PP&E, Net"))
    intangibles: LineItem = field(default_factory=lambda: LineItem("Intangible Assets"))
    goodwill: LineItem = field(default_factory=lambda: LineItem("Goodwill"))
    other_assets: LineItem = field(default_factory=lambda: LineItem("Other Assets"))
    total_assets: LineItem = field(default_factory=lambda: LineItem("Total Assets"))

    # Liabilities
    accounts_payable: LineItem = field(default_factory=lambda: LineItem("Accounts Payable"))
    accrued_expenses: LineItem = field(default_factory=lambda: LineItem("Accrued Expenses"))
    short_term_debt: LineItem = field(default_factory=lambda: LineItem("Short-term Debt"))
    current_portion_ltd: LineItem = field(default_factory=lambda: LineItem("Current Portion of LTD"))
    other_current_liabilities: LineItem = field(default_factory=lambda: LineItem("Other Current Liabilities"))
    total_current_liabilities: LineItem = field(default_factory=lambda: LineItem("Total Current Liabilities"))
    long_term_debt: LineItem = field(default_factory=lambda: LineItem("Long-term Debt"))
    deferred_tax_liabilities: LineItem = field(default_factory=lambda: LineItem("Deferred Tax Liabilities"))
    other_liabilities: LineItem = field(default_factory=lambda: LineItem("Other Liabilities"))
    total_liabilities: LineItem = field(default_factory=lambda: LineItem("Total Liabilities"))

    # Equity
    common_stock: LineItem = field(default_factory=lambda: LineItem("Common Stock"))
    retained_earnings: LineItem = field(default_factory=lambda: LineItem("Retained Earnings"))
    treasury_stock: LineItem = field(default_factory=lambda: LineItem("Treasury Stock"))
    other_equity: LineItem = field(default_factory=lambda: LineItem("Other Comprehensive Income"))
    total_equity: LineItem = field(default_factory=lambda: LineItem("Total Shareholders' Equity"))


@dataclass
class CashFlowStatement:
    """Standardized cash flow statement structure."""
    # Operating
    net_income: LineItem = field(default_factory=lambda: LineItem("Net Income"))
    depreciation: LineItem = field(default_factory=lambda: LineItem("Depreciation & Amortization"))
    stock_compensation: LineItem = field(default_factory=lambda: LineItem("Stock-based Compensation"))
    deferred_taxes: LineItem = field(default_factory=lambda: LineItem("Deferred Taxes"))
    change_receivables: LineItem = field(default_factory=lambda: LineItem("Change in Receivables"))
    change_inventory: LineItem = field(default_factory=lambda: LineItem("Change in Inventory"))
    change_payables: LineItem = field(default_factory=lambda: LineItem("Change in Payables"))
    other_operating: LineItem = field(default_factory=lambda: LineItem("Other Operating Activities"))
    cash_from_operations: LineItem = field(default_factory=lambda: LineItem("Cash from Operations"))

    # Investing
    capex: LineItem = field(default_factory=lambda: LineItem("Capital Expenditures"))
    acquisitions: LineItem = field(default_factory=lambda: LineItem("Acquisitions"))
    investments: LineItem = field(default_factory=lambda: LineItem("Purchases/Sales of Investments"))
    other_investing: LineItem = field(default_factory=lambda: LineItem("Other Investing Activities"))
    cash_from_investing: LineItem = field(default_factory=lambda: LineItem("Cash from Investing"))

    # Financing
    debt_issued: LineItem = field(default_factory=lambda: LineItem("Debt Issued"))
    debt_repaid: LineItem = field(default_factory=lambda: LineItem("Debt Repaid"))
    stock_issued: LineItem = field(default_factory=lambda: LineItem("Stock Issued"))
    stock_repurchased: LineItem = field(default_factory=lambda: LineItem("Stock Repurchased"))
    dividends_paid: LineItem = field(default_factory=lambda: LineItem("Dividends Paid"))
    other_financing: LineItem = field(default_factory=lambda: LineItem("Other Financing Activities"))
    cash_from_financing: LineItem = field(default_factory=lambda: LineItem("Cash from Financing"))


class FinancialStatementParser:
    """Parses EDGAR data into standardized financial statements."""

    # XBRL concept mappings - maps standard names to possible XBRL tags
    INCOME_MAPPINGS = {
        "revenue": [
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "TotalRevenuesAndOtherIncome"
        ],
        "cost_of_revenue": [
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold"
        ],
        "gross_profit": ["GrossProfit"],
        "rd_expense": [
            "ResearchAndDevelopmentExpense",
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"
        ],
        "sga_expense": [
            "SellingGeneralAndAdministrativeExpense",
            "GeneralAndAdministrativeExpense"
        ],
        "operating_expenses": ["OperatingExpenses"],
        "operating_income": [
            "OperatingIncomeLoss",
            "IncomeLossFromOperations"
        ],
        "interest_expense": [
            "InterestExpense",
            "InterestExpenseDebt",
            "InterestAndDebtExpense"
        ],
        "pretax_income": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
        ],
        "income_tax": ["IncomeTaxExpenseBenefit"],
        "net_income": [
            "NetIncomeLoss",
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic"
        ]
    }

    BALANCE_MAPPINGS = {
        "cash": [
            "CashAndCashEquivalentsAtCarryingValue",
            "Cash",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
        ],
        "short_term_investments": [
            "ShortTermInvestments",
            "MarketableSecuritiesCurrent"
        ],
        "accounts_receivable": [
            "AccountsReceivableNetCurrent",
            "AccountsReceivableNet",
            "ReceivablesNetCurrent"
        ],
        "inventory": [
            "InventoryNet",
            "InventoryFinishedGoodsNetOfReserves"
        ],
        "total_current_assets": ["AssetsCurrent"],
        "ppe_net": [
            "PropertyPlantAndEquipmentNet",
            "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"
        ],
        "intangibles": [
            "IntangibleAssetsNetExcludingGoodwill",
            "FiniteLivedIntangibleAssetsNet"
        ],
        "goodwill": ["Goodwill"],
        "total_assets": ["Assets"],
        "accounts_payable": [
            "AccountsPayableCurrent",
            "AccountsPayable"
        ],
        "short_term_debt": [
            "ShortTermBorrowings",
            "DebtCurrent"
        ],
        "total_current_liabilities": ["LiabilitiesCurrent"],
        "long_term_debt": [
            "LongTermDebt",
            "LongTermDebtNoncurrent",
            "LongTermDebtAndCapitalLeaseObligations"
        ],
        "total_liabilities": ["Liabilities"],
        "common_stock": [
            "CommonStockValue",
            "CommonStocksIncludingAdditionalPaidInCapital"
        ],
        "retained_earnings": ["RetainedEarningsAccumulatedDeficit"],
        "treasury_stock": [
            "TreasuryStockValue",
            "TreasuryStockCommonValue"
        ],
        "total_equity": [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
        ]
    }

    CASHFLOW_MAPPINGS = {
        "net_income": [
            "NetIncomeLoss",
            "ProfitLoss"
        ],
        "depreciation": [
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "Depreciation"
        ],
        "stock_compensation": [
            "ShareBasedCompensation",
            "StockCompensationPlan"
        ],
        "cash_from_operations": [
            "NetCashProvidedByUsedInOperatingActivities"
        ],
        "capex": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
            "PaymentsForCapitalImprovements"
        ],
        "acquisitions": [
            "PaymentsToAcquireBusinessesNetOfCashAcquired",
            "BusinessCombinationConsiderationTransferredIncludingEquityInterestInAcquireeHeldPriorToCombination1"
        ],
        "cash_from_investing": [
            "NetCashProvidedByUsedInInvestingActivities"
        ],
        "debt_issued": [
            "ProceedsFromIssuanceOfLongTermDebt",
            "ProceedsFromDebtNetOfIssuanceCosts"
        ],
        "debt_repaid": [
            "RepaymentsOfLongTermDebt",
            "RepaymentsOfDebt"
        ],
        "stock_repurchased": [
            "PaymentsForRepurchaseOfCommonStock",
            "StockRepurchasedAndRetiredDuringPeriodValue"
        ],
        "dividends_paid": [
            "PaymentsOfDividends",
            "PaymentsOfDividendsCommonStock"
        ],
        "cash_from_financing": [
            "NetCashProvidedByUsedInFinancingActivities"
        ]
    }

    def __init__(self, edgar_data: dict):
        """Initialize with raw EDGAR data."""
        self.edgar_data = edgar_data
        self.company_info = edgar_data.get("company", {})
        self.financial_data = edgar_data.get("financial_data", {})

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract fiscal year from date string."""
        if not date_str:
            return None
        try:
            return int(date_str[:4])
        except (ValueError, IndexError):
            return None

    def _get_values_by_year(self, raw_values: list) -> dict:
        """Convert list of values to year -> value dictionary."""
        result = {}
        for item in raw_values:
            year = self._extract_year(item.get("end"))
            if year and item.get("value") is not None:
                # Keep most recent value for each year if duplicates
                if year not in result or item.get("filed", "") > result.get(f"{year}_filed", ""):
                    result[year] = item["value"]
                    result[f"{year}_filed"] = item.get("filed", "")

        # Remove tracking fields
        return {k: v for k, v in result.items() if not str(k).endswith("_filed")}

    def parse_income_statement(self) -> IncomeStatement:
        """Parse income statement from EDGAR data."""
        income = IncomeStatement()
        raw_income = self.financial_data.get("income_statement", {})

        for attr_name, mappings in self.INCOME_MAPPINGS.items():
            line_item = getattr(income, attr_name, None)
            if line_item:
                raw_values = raw_income.get(attr_name, [])
                line_item.values = self._get_values_by_year(raw_values)

        # Calculate derived values if missing
        years = set()
        for item in [income.revenue, income.cost_of_revenue, income.gross_profit]:
            years.update(item.values.keys())

        for year in years:
            # Gross profit = Revenue - COGS
            if year not in income.gross_profit.values:
                rev = income.revenue.values.get(year)
                cogs = income.cost_of_revenue.values.get(year)
                if rev is not None and cogs is not None:
                    income.gross_profit.values[year] = rev - cogs

        return income

    def parse_balance_sheet(self) -> BalanceSheet:
        """Parse balance sheet from EDGAR data."""
        balance = BalanceSheet()
        raw_balance = self.financial_data.get("balance_sheet", {})

        for attr_name, mappings in self.BALANCE_MAPPINGS.items():
            line_item = getattr(balance, attr_name, None)
            if line_item:
                raw_values = raw_balance.get(attr_name, [])
                line_item.values = self._get_values_by_year(raw_values)

        return balance

    def parse_cash_flow_statement(self) -> CashFlowStatement:
        """Parse cash flow statement from EDGAR data."""
        cashflow = CashFlowStatement()
        raw_cf = self.financial_data.get("cash_flow", {})

        for attr_name, mappings in self.CASHFLOW_MAPPINGS.items():
            line_item = getattr(cashflow, attr_name, None)
            if line_item:
                raw_values = raw_cf.get(attr_name, [])
                line_item.values = self._get_values_by_year(raw_values)

        return cashflow

    def get_available_years(self) -> list:
        """Get list of years with available data."""
        years = set()

        for statement_type in ["income_statement", "balance_sheet", "cash_flow"]:
            statement_data = self.financial_data.get(statement_type, {})
            for line_item, values in statement_data.items():
                for item in values:
                    year = self._extract_year(item.get("end"))
                    if year:
                        years.add(year)

        return sorted(years, reverse=True)

    def to_model_format(self) -> dict:
        """Convert to dictionary format suitable for DCF model."""
        income = self.parse_income_statement()
        balance = self.parse_balance_sheet()
        cashflow = self.parse_cash_flow_statement()
        years = self.get_available_years()

        def line_item_to_dict(item: LineItem) -> dict:
            return {"name": item.name, "values": item.values, "unit": item.unit}

        return {
            "company": self.company_info,
            "years": years,
            "income_statement": {
                "revenue": line_item_to_dict(income.revenue),
                "cost_of_revenue": line_item_to_dict(income.cost_of_revenue),
                "gross_profit": line_item_to_dict(income.gross_profit),
                "rd_expense": line_item_to_dict(income.rd_expense),
                "sga_expense": line_item_to_dict(income.sga_expense),
                "operating_expenses": line_item_to_dict(income.operating_expenses),
                "operating_income": line_item_to_dict(income.operating_income),
                "interest_expense": line_item_to_dict(income.interest_expense),
                "pretax_income": line_item_to_dict(income.pretax_income),
                "income_tax": line_item_to_dict(income.income_tax),
                "net_income": line_item_to_dict(income.net_income)
            },
            "balance_sheet": {
                "cash": line_item_to_dict(balance.cash),
                "accounts_receivable": line_item_to_dict(balance.accounts_receivable),
                "inventory": line_item_to_dict(balance.inventory),
                "total_current_assets": line_item_to_dict(balance.total_current_assets),
                "ppe_net": line_item_to_dict(balance.ppe_net),
                "intangibles": line_item_to_dict(balance.intangibles),
                "goodwill": line_item_to_dict(balance.goodwill),
                "total_assets": line_item_to_dict(balance.total_assets),
                "accounts_payable": line_item_to_dict(balance.accounts_payable),
                "short_term_debt": line_item_to_dict(balance.short_term_debt),
                "total_current_liabilities": line_item_to_dict(balance.total_current_liabilities),
                "long_term_debt": line_item_to_dict(balance.long_term_debt),
                "total_liabilities": line_item_to_dict(balance.total_liabilities),
                "retained_earnings": line_item_to_dict(balance.retained_earnings),
                "total_equity": line_item_to_dict(balance.total_equity)
            },
            "cash_flow_statement": {
                "depreciation": line_item_to_dict(cashflow.depreciation),
                "stock_compensation": line_item_to_dict(cashflow.stock_compensation),
                "cash_from_operations": line_item_to_dict(cashflow.cash_from_operations),
                "capex": line_item_to_dict(cashflow.capex),
                "acquisitions": line_item_to_dict(cashflow.acquisitions),
                "cash_from_investing": line_item_to_dict(cashflow.cash_from_investing),
                "dividends_paid": line_item_to_dict(cashflow.dividends_paid),
                "cash_from_financing": line_item_to_dict(cashflow.cash_from_financing)
            }
        }


def main():
    """CLI interface for parsing financial statements."""
    if len(sys.argv) < 2:
        print("Usage: parse_financial_statements.py <edgar_data.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        edgar_data = json.load(f)

    parser = FinancialStatementParser(edgar_data)
    model_data = parser.to_model_format()

    company_name = model_data.get("company", {}).get("ticker", "company")
    output_file = f"{company_name}_parsed_financials.json"

    with open(output_file, "w") as f:
        json.dump(model_data, f, indent=2)

    print(f"Parsed financial data saved to: {output_file}")
    print(f"Available years: {model_data['years']}")


if __name__ == "__main__":
    main()
