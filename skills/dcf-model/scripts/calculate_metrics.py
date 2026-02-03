#!/usr/bin/env python3
"""
Financial Metrics Calculator

Computes historical financial metrics from parsed financial statements
for use in DCF projections: growth rates, margins, returns, working capital days.
"""

import json
import sys
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class HistoricalMetrics:
    """Collection of computed historical metrics by year."""
    years: list = field(default_factory=list)

    # Growth metrics
    revenue_growth: dict = field(default_factory=dict)
    gross_profit_growth: dict = field(default_factory=dict)
    ebit_growth: dict = field(default_factory=dict)
    net_income_growth: dict = field(default_factory=dict)

    # Margin metrics
    gross_margin: dict = field(default_factory=dict)
    ebit_margin: dict = field(default_factory=dict)
    ebitda_margin: dict = field(default_factory=dict)
    net_margin: dict = field(default_factory=dict)

    # Return metrics
    roa: dict = field(default_factory=dict)  # Return on Assets
    roe: dict = field(default_factory=dict)  # Return on Equity
    roic: dict = field(default_factory=dict)  # Return on Invested Capital

    # Working capital metrics (in days)
    dso: dict = field(default_factory=dict)  # Days Sales Outstanding
    dio: dict = field(default_factory=dict)  # Days Inventory Outstanding
    dpo: dict = field(default_factory=dict)  # Days Payables Outstanding
    cash_conversion_cycle: dict = field(default_factory=dict)

    # Capital intensity
    capex_to_revenue: dict = field(default_factory=dict)
    capex_to_da: dict = field(default_factory=dict)  # CapEx to D&A ratio
    da_to_revenue: dict = field(default_factory=dict)

    # Leverage metrics
    debt_to_equity: dict = field(default_factory=dict)
    debt_to_ebitda: dict = field(default_factory=dict)
    interest_coverage: dict = field(default_factory=dict)

    # Effective tax rate
    effective_tax_rate: dict = field(default_factory=dict)


class MetricsCalculator:
    """Calculates financial metrics from parsed statements."""

    def __init__(self, parsed_data: dict):
        self.data = parsed_data
        self.years = sorted(parsed_data.get("years", []), reverse=True)
        self.income = parsed_data.get("income_statement", {})
        self.balance = parsed_data.get("balance_sheet", {})
        self.cashflow = parsed_data.get("cash_flow_statement", {})

    def _get_value(self, statement: dict, line_item: str, year: int) -> Optional[float]:
        """Get value for a specific line item and year."""
        item = statement.get(line_item, {})
        values = item.get("values", {})
        return values.get(year) or values.get(str(year))

    def _safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """Safely divide, returning None if invalid."""
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator

    def _calc_growth(self, current: Optional[float], prior: Optional[float]) -> Optional[float]:
        """Calculate YoY growth rate."""
        if current is None or prior is None or prior == 0:
            return None
        return (current - prior) / abs(prior)

    def _avg(self, value1: Optional[float], value2: Optional[float]) -> Optional[float]:
        """Calculate average of two values."""
        if value1 is None or value2 is None:
            return value1 or value2
        return (value1 + value2) / 2

    def calculate_growth_metrics(self, metrics: HistoricalMetrics) -> None:
        """Calculate year-over-year growth rates."""
        for i, year in enumerate(self.years[:-1]):
            prior_year = self.years[i + 1]

            # Revenue growth
            rev = self._get_value(self.income, "revenue", year)
            rev_prior = self._get_value(self.income, "revenue", prior_year)
            metrics.revenue_growth[year] = self._calc_growth(rev, rev_prior)

            # Gross profit growth
            gp = self._get_value(self.income, "gross_profit", year)
            gp_prior = self._get_value(self.income, "gross_profit", prior_year)
            metrics.gross_profit_growth[year] = self._calc_growth(gp, gp_prior)

            # EBIT growth
            ebit = self._get_value(self.income, "operating_income", year)
            ebit_prior = self._get_value(self.income, "operating_income", prior_year)
            metrics.ebit_growth[year] = self._calc_growth(ebit, ebit_prior)

            # Net income growth
            ni = self._get_value(self.income, "net_income", year)
            ni_prior = self._get_value(self.income, "net_income", prior_year)
            metrics.net_income_growth[year] = self._calc_growth(ni, ni_prior)

    def calculate_margin_metrics(self, metrics: HistoricalMetrics) -> None:
        """Calculate profitability margins."""
        for year in self.years:
            revenue = self._get_value(self.income, "revenue", year)

            # Gross margin
            gross_profit = self._get_value(self.income, "gross_profit", year)
            metrics.gross_margin[year] = self._safe_divide(gross_profit, revenue)

            # EBIT margin
            ebit = self._get_value(self.income, "operating_income", year)
            metrics.ebit_margin[year] = self._safe_divide(ebit, revenue)

            # EBITDA margin
            da = self._get_value(self.cashflow, "depreciation", year)
            if ebit is not None and da is not None:
                ebitda = ebit + abs(da)
                metrics.ebitda_margin[year] = self._safe_divide(ebitda, revenue)

            # Net margin
            net_income = self._get_value(self.income, "net_income", year)
            metrics.net_margin[year] = self._safe_divide(net_income, revenue)

    def calculate_return_metrics(self, metrics: HistoricalMetrics) -> None:
        """Calculate return metrics (ROA, ROE, ROIC)."""
        for i, year in enumerate(self.years):
            prior_year = self.years[i + 1] if i + 1 < len(self.years) else None

            net_income = self._get_value(self.income, "net_income", year)
            ebit = self._get_value(self.income, "operating_income", year)
            tax_rate = self._get_value(self.income, "income_tax", year)
            pretax = self._get_value(self.income, "pretax_income", year)

            # Calculate effective tax rate for NOPAT
            eff_tax = self._safe_divide(tax_rate, pretax) if pretax and pretax > 0 else 0.25

            # ROA = Net Income / Average Total Assets
            assets = self._get_value(self.balance, "total_assets", year)
            assets_prior = self._get_value(self.balance, "total_assets", prior_year) if prior_year else None
            avg_assets = self._avg(assets, assets_prior)
            metrics.roa[year] = self._safe_divide(net_income, avg_assets)

            # ROE = Net Income / Average Shareholders' Equity
            equity = self._get_value(self.balance, "total_equity", year)
            equity_prior = self._get_value(self.balance, "total_equity", prior_year) if prior_year else None
            avg_equity = self._avg(equity, equity_prior)
            metrics.roe[year] = self._safe_divide(net_income, avg_equity)

            # ROIC = NOPAT / Invested Capital
            # Invested Capital = Total Debt + Shareholders' Equity - Cash
            if ebit is not None and eff_tax is not None:
                nopat = ebit * (1 - eff_tax)
                debt = (self._get_value(self.balance, "long_term_debt", year) or 0) + \
                       (self._get_value(self.balance, "short_term_debt", year) or 0)
                cash = self._get_value(self.balance, "cash", year) or 0
                invested_capital = (debt + (equity or 0)) - cash

                debt_prior = ((self._get_value(self.balance, "long_term_debt", prior_year) or 0) +
                              (self._get_value(self.balance, "short_term_debt", prior_year) or 0)) if prior_year else 0
                cash_prior = self._get_value(self.balance, "cash", prior_year) or 0 if prior_year else 0
                equity_prior_val = equity_prior or 0
                ic_prior = (debt_prior + equity_prior_val) - cash_prior if prior_year else invested_capital

                avg_ic = self._avg(invested_capital, ic_prior)
                metrics.roic[year] = self._safe_divide(nopat, avg_ic)

    def calculate_working_capital_metrics(self, metrics: HistoricalMetrics) -> None:
        """Calculate working capital days (DSO, DIO, DPO, CCC)."""
        for year in self.years:
            revenue = self._get_value(self.income, "revenue", year)
            cogs = self._get_value(self.income, "cost_of_revenue", year)

            # DSO = (Accounts Receivable / Revenue) * 365
            ar = self._get_value(self.balance, "accounts_receivable", year)
            if ar is not None and revenue:
                metrics.dso[year] = (ar / revenue) * 365

            # DIO = (Inventory / COGS) * 365
            inventory = self._get_value(self.balance, "inventory", year)
            if inventory is not None and cogs:
                metrics.dio[year] = (inventory / abs(cogs)) * 365

            # DPO = (Accounts Payable / COGS) * 365
            ap = self._get_value(self.balance, "accounts_payable", year)
            if ap is not None and cogs:
                metrics.dpo[year] = (ap / abs(cogs)) * 365

            # Cash Conversion Cycle = DSO + DIO - DPO
            dso = metrics.dso.get(year)
            dio = metrics.dio.get(year)
            dpo = metrics.dpo.get(year)
            if dso is not None and dio is not None and dpo is not None:
                metrics.cash_conversion_cycle[year] = dso + dio - dpo

    def calculate_capital_intensity(self, metrics: HistoricalMetrics) -> None:
        """Calculate capital intensity metrics."""
        for year in self.years:
            revenue = self._get_value(self.income, "revenue", year)
            capex = self._get_value(self.cashflow, "capex", year)
            da = self._get_value(self.cashflow, "depreciation", year)

            # CapEx as % of revenue
            if capex is not None:
                metrics.capex_to_revenue[year] = self._safe_divide(abs(capex), revenue)

            # CapEx to D&A ratio
            if capex is not None and da is not None:
                metrics.capex_to_da[year] = self._safe_divide(abs(capex), abs(da))

            # D&A as % of revenue
            if da is not None:
                metrics.da_to_revenue[year] = self._safe_divide(abs(da), revenue)

    def calculate_leverage_metrics(self, metrics: HistoricalMetrics) -> None:
        """Calculate leverage and coverage metrics."""
        for year in self.years:
            equity = self._get_value(self.balance, "total_equity", year)
            ltd = self._get_value(self.balance, "long_term_debt", year) or 0
            std = self._get_value(self.balance, "short_term_debt", year) or 0
            total_debt = ltd + std

            ebit = self._get_value(self.income, "operating_income", year)
            da = self._get_value(self.cashflow, "depreciation", year)
            interest = self._get_value(self.income, "interest_expense", year)

            # Debt to Equity
            metrics.debt_to_equity[year] = self._safe_divide(total_debt, equity)

            # Debt to EBITDA
            if ebit is not None and da is not None:
                ebitda = ebit + abs(da)
                metrics.debt_to_ebitda[year] = self._safe_divide(total_debt, ebitda)

            # Interest Coverage = EBIT / Interest Expense
            if interest and interest > 0:
                metrics.interest_coverage[year] = self._safe_divide(ebit, interest)

    def calculate_tax_rate(self, metrics: HistoricalMetrics) -> None:
        """Calculate effective tax rate."""
        for year in self.years:
            tax_expense = self._get_value(self.income, "income_tax", year)
            pretax_income = self._get_value(self.income, "pretax_income", year)

            if pretax_income and pretax_income > 0:
                metrics.effective_tax_rate[year] = self._safe_divide(tax_expense, pretax_income)

    def calculate_all(self) -> HistoricalMetrics:
        """Calculate all metrics."""
        metrics = HistoricalMetrics(years=self.years)

        self.calculate_growth_metrics(metrics)
        self.calculate_margin_metrics(metrics)
        self.calculate_return_metrics(metrics)
        self.calculate_working_capital_metrics(metrics)
        self.calculate_capital_intensity(metrics)
        self.calculate_leverage_metrics(metrics)
        self.calculate_tax_rate(metrics)

        return metrics

    def to_dict(self, metrics: HistoricalMetrics) -> dict:
        """Convert metrics to dictionary format."""
        def format_metric(values: dict, as_percent: bool = False) -> dict:
            """Format metric values with optional percentage conversion."""
            result = {}
            for year, value in values.items():
                if value is not None:
                    result[year] = round(value * 100, 2) if as_percent else round(value, 2)
            return result

        return {
            "years": metrics.years,
            "growth": {
                "revenue_growth_pct": format_metric(metrics.revenue_growth, True),
                "gross_profit_growth_pct": format_metric(metrics.gross_profit_growth, True),
                "ebit_growth_pct": format_metric(metrics.ebit_growth, True),
                "net_income_growth_pct": format_metric(metrics.net_income_growth, True)
            },
            "margins": {
                "gross_margin_pct": format_metric(metrics.gross_margin, True),
                "ebit_margin_pct": format_metric(metrics.ebit_margin, True),
                "ebitda_margin_pct": format_metric(metrics.ebitda_margin, True),
                "net_margin_pct": format_metric(metrics.net_margin, True)
            },
            "returns": {
                "roa_pct": format_metric(metrics.roa, True),
                "roe_pct": format_metric(metrics.roe, True),
                "roic_pct": format_metric(metrics.roic, True)
            },
            "working_capital": {
                "dso_days": format_metric(metrics.dso),
                "dio_days": format_metric(metrics.dio),
                "dpo_days": format_metric(metrics.dpo),
                "cash_conversion_cycle_days": format_metric(metrics.cash_conversion_cycle)
            },
            "capital_intensity": {
                "capex_to_revenue_pct": format_metric(metrics.capex_to_revenue, True),
                "capex_to_da_ratio": format_metric(metrics.capex_to_da),
                "da_to_revenue_pct": format_metric(metrics.da_to_revenue, True)
            },
            "leverage": {
                "debt_to_equity_ratio": format_metric(metrics.debt_to_equity),
                "debt_to_ebitda_ratio": format_metric(metrics.debt_to_ebitda),
                "interest_coverage_ratio": format_metric(metrics.interest_coverage)
            },
            "tax": {
                "effective_tax_rate_pct": format_metric(metrics.effective_tax_rate, True)
            }
        }

    def get_averages(self, metrics: HistoricalMetrics) -> dict:
        """Calculate average metrics over the historical period."""
        def calc_avg(values: dict) -> Optional[float]:
            valid_values = [v for v in values.values() if v is not None]
            return sum(valid_values) / len(valid_values) if valid_values else None

        return {
            "avg_revenue_growth": calc_avg(metrics.revenue_growth),
            "avg_gross_margin": calc_avg(metrics.gross_margin),
            "avg_ebit_margin": calc_avg(metrics.ebit_margin),
            "avg_ebitda_margin": calc_avg(metrics.ebitda_margin),
            "avg_net_margin": calc_avg(metrics.net_margin),
            "avg_roa": calc_avg(metrics.roa),
            "avg_roe": calc_avg(metrics.roe),
            "avg_roic": calc_avg(metrics.roic),
            "avg_dso": calc_avg(metrics.dso),
            "avg_dio": calc_avg(metrics.dio),
            "avg_dpo": calc_avg(metrics.dpo),
            "avg_capex_to_revenue": calc_avg(metrics.capex_to_revenue),
            "avg_effective_tax_rate": calc_avg(metrics.effective_tax_rate)
        }


def main():
    """CLI interface for calculating metrics."""
    if len(sys.argv) < 2:
        print("Usage: calculate_metrics.py <parsed_financials.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        parsed_data = json.load(f)

    calculator = MetricsCalculator(parsed_data)
    metrics = calculator.calculate_all()

    output = {
        "company": parsed_data.get("company", {}),
        "metrics": calculator.to_dict(metrics),
        "averages": calculator.get_averages(metrics)
    }

    company_name = parsed_data.get("company", {}).get("ticker", "company")
    output_file = f"{company_name}_metrics.json"

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Metrics saved to: {output_file}")

    # Print summary
    print("\nHistorical Averages:")
    for key, value in output["averages"].items():
        if value is not None:
            label = key.replace("avg_", "").replace("_", " ").title()
            if "margin" in key or "rate" in key or "growth" in key:
                print(f"  {label}: {value*100:.1f}%")
            elif "days" in key.lower() or key in ["avg_dso", "avg_dio", "avg_dpo"]:
                print(f"  {label}: {value:.0f} days")
            else:
                print(f"  {label}: {value:.2f}")


if __name__ == "__main__":
    main()
