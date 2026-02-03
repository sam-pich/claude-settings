#!/usr/bin/env python3
"""
DCF Assumption Validator

Validates completeness and reasonableness of DCF model assumptions.
Identifies missing required inputs and flags potentially unreasonable values.
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(Enum):
    ERROR = "error"      # Must be fixed - model won't work
    WARNING = "warning"  # Should be reviewed - may affect accuracy
    INFO = "info"        # FYI - could be improved


@dataclass
class ValidationIssue:
    """Single validation issue."""
    category: str
    field: str
    message: str
    severity: Severity
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result."""
    is_valid: bool
    issues: list = field(default_factory=list)
    missing_required: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


class AssumptionValidator:
    """Validates DCF model assumptions."""

    # Required assumptions by category
    REQUIRED_ASSUMPTIONS = {
        "model_config": [
            "dcf_type",           # "unlevered" or "levered"
            "complexity",         # "2-stage", "3-stage", or "lbo"
            "projection_years",   # 5-10
            "terminal_method"     # "perpetuity", "exit_multiple", or "both"
        ],
        "revenue": [
            "revenue_growth_y1",
            "revenue_growth_y2",
            "revenue_growth_y3",
            "terminal_growth_rate"
        ],
        "costs": [
            "gross_margin_target",
            "opex_pct_revenue"
        ],
        "capital_structure": [
            "risk_free_rate",
            "equity_risk_premium",
            "beta"
        ],
        "terminal_value": [
            # At least one of these based on terminal_method
            # "perpetuity_growth_rate" or "exit_multiple"
        ]
    }

    # Reasonable ranges for key assumptions
    REASONABLE_RANGES = {
        "revenue_growth": (-0.20, 0.50),        # -20% to +50%
        "terminal_growth_rate": (0.00, 0.04),   # 0% to 4% (should not exceed GDP)
        "perpetuity_growth_rate": (0.00, 0.04), # Same
        "gross_margin": (0.05, 0.95),           # 5% to 95%
        "ebit_margin": (-0.20, 0.60),           # -20% to 60%
        "risk_free_rate": (0.01, 0.10),         # 1% to 10%
        "equity_risk_premium": (0.03, 0.10),    # 3% to 10%
        "beta": (0.3, 3.0),                     # 0.3 to 3.0
        "cost_of_debt": (0.02, 0.15),           # 2% to 15%
        "tax_rate": (0.10, 0.40),               # 10% to 40%
        "exit_multiple": (3.0, 25.0),           # 3x to 25x EBITDA
        "capex_pct_revenue": (0.01, 0.25),      # 1% to 25%
        "dso_days": (15, 120),                  # 15 to 120 days
        "dio_days": (0, 180),                   # 0 to 180 days
        "dpo_days": (15, 120),                  # 15 to 120 days
        "wacc": (0.05, 0.20),                   # 5% to 20%
    }

    def __init__(self, assumptions: dict, historical_metrics: dict = None):
        self.assumptions = assumptions
        self.historical = historical_metrics or {}
        self.result = ValidationResult(is_valid=True)

    def _add_issue(self, category: str, field: str, message: str,
                   severity: Severity, suggestion: str = None):
        """Add validation issue to results."""
        issue = ValidationIssue(
            category=category,
            field=field,
            message=message,
            severity=severity,
            suggestion=suggestion
        )
        self.result.issues.append(issue)

        if severity == Severity.ERROR:
            self.result.is_valid = False
            self.result.missing_required.append(f"{category}.{field}")
        elif severity == Severity.WARNING:
            self.result.warnings.append(f"{category}.{field}: {message}")

    def _get_assumption(self, *path):
        """Get nested assumption value."""
        value = self.assumptions
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _check_required(self, category: str, fields: list) -> None:
        """Check that required fields are present."""
        cat_data = self.assumptions.get(category, {})

        for field in fields:
            value = cat_data.get(field)
            if value is None:
                self._add_issue(
                    category=category,
                    field=field,
                    message=f"Required assumption '{field}' is missing",
                    severity=Severity.ERROR,
                    suggestion=f"Please provide a value for {field}"
                )

    def _check_range(self, category: str, field: str, value: float,
                     range_key: str = None) -> None:
        """Check if value falls within reasonable range."""
        range_key = range_key or field
        if range_key not in self.REASONABLE_RANGES:
            return

        min_val, max_val = self.REASONABLE_RANGES[range_key]

        if value < min_val or value > max_val:
            self._add_issue(
                category=category,
                field=field,
                message=f"Value {value:.2%} is outside typical range ({min_val:.0%} to {max_val:.0%})",
                severity=Severity.WARNING,
                suggestion=f"Verify this assumption is intentional"
            )

    def validate_model_config(self) -> None:
        """Validate model configuration."""
        config = self.assumptions.get("model_config", {})

        # Check DCF type
        dcf_type = config.get("dcf_type")
        if dcf_type not in ["unlevered", "levered"]:
            self._add_issue(
                "model_config", "dcf_type",
                "DCF type must be 'unlevered' (WACC) or 'levered' (equity)",
                Severity.ERROR
            )

        # Check complexity
        complexity = config.get("complexity")
        if complexity not in ["2-stage", "3-stage", "lbo"]:
            self._add_issue(
                "model_config", "complexity",
                "Complexity must be '2-stage', '3-stage', or 'lbo'",
                Severity.ERROR
            )

        # Check projection years
        years = config.get("projection_years")
        if years is None:
            self._add_issue(
                "model_config", "projection_years",
                "Projection period is required",
                Severity.ERROR
            )
        elif years < 3 or years > 15:
            self._add_issue(
                "model_config", "projection_years",
                f"Projection period of {years} years is unusual (typical: 5-10)",
                Severity.WARNING
            )

        # Check terminal method
        method = config.get("terminal_method")
        if method not in ["perpetuity", "exit_multiple", "both"]:
            self._add_issue(
                "model_config", "terminal_method",
                "Terminal method must be 'perpetuity', 'exit_multiple', or 'both'",
                Severity.ERROR
            )

    def validate_revenue_assumptions(self) -> None:
        """Validate revenue projection assumptions."""
        revenue = self.assumptions.get("revenue", {})

        # Check revenue drivers exist
        if not revenue:
            self._add_issue(
                "revenue", "all",
                "Revenue assumptions section is missing",
                Severity.ERROR
            )
            return

        # Check growth rates
        projection_years = self._get_assumption("model_config", "projection_years") or 5

        for i in range(1, min(projection_years + 1, 6)):
            key = f"revenue_growth_y{i}"
            value = revenue.get(key)
            if value is None and i <= 3:
                self._add_issue(
                    "revenue", key,
                    f"Year {i} revenue growth rate is required",
                    Severity.ERROR
                )
            elif value is not None:
                self._check_range("revenue", key, value, "revenue_growth")

        # Check terminal growth
        terminal_growth = revenue.get("terminal_growth_rate")
        if terminal_growth is None:
            self._add_issue(
                "revenue", "terminal_growth_rate",
                "Terminal growth rate is required",
                Severity.ERROR
            )
        elif terminal_growth is not None:
            self._check_range("revenue", "terminal_growth_rate", terminal_growth)
            if terminal_growth > 0.03:
                self._add_issue(
                    "revenue", "terminal_growth_rate",
                    f"Terminal growth of {terminal_growth:.1%} exceeds long-term GDP growth",
                    Severity.WARNING,
                    "Consider using 2-3% for mature companies"
                )

    def validate_cost_assumptions(self) -> None:
        """Validate cost and margin assumptions."""
        costs = self.assumptions.get("costs", {})

        if not costs:
            self._add_issue(
                "costs", "all",
                "Cost assumptions section is missing",
                Severity.ERROR
            )
            return

        # Gross margin
        gm = costs.get("gross_margin_target")
        if gm is not None:
            self._check_range("costs", "gross_margin_target", gm, "gross_margin")

        # OpEx
        opex = costs.get("opex_pct_revenue")
        if opex is None:
            self._add_issue(
                "costs", "opex_pct_revenue",
                "Operating expenses as % of revenue is required",
                Severity.ERROR
            )

    def validate_capital_structure(self) -> None:
        """Validate capital structure and WACC inputs."""
        cap = self.assumptions.get("capital_structure", {})

        if not cap:
            self._add_issue(
                "capital_structure", "all",
                "Capital structure assumptions section is missing",
                Severity.ERROR
            )
            return

        # Risk-free rate
        rf = cap.get("risk_free_rate")
        if rf is None:
            self._add_issue(
                "capital_structure", "risk_free_rate",
                "Risk-free rate is required (typically 10-year Treasury yield)",
                Severity.ERROR
            )
        else:
            self._check_range("capital_structure", "risk_free_rate", rf)

        # Equity risk premium
        erp = cap.get("equity_risk_premium")
        if erp is None:
            self._add_issue(
                "capital_structure", "equity_risk_premium",
                "Equity risk premium is required (typically 5-6%)",
                Severity.ERROR
            )
        else:
            self._check_range("capital_structure", "equity_risk_premium", erp)

        # Beta
        beta = cap.get("beta")
        if beta is None:
            self._add_issue(
                "capital_structure", "beta",
                "Beta is required for cost of equity calculation",
                Severity.ERROR
            )
        else:
            self._check_range("capital_structure", "beta", beta)

        # For unlevered DCF, check WACC components
        dcf_type = self._get_assumption("model_config", "dcf_type")
        if dcf_type == "unlevered":
            # Target capital structure
            target_de = cap.get("target_debt_to_equity")
            if target_de is None:
                self._add_issue(
                    "capital_structure", "target_debt_to_equity",
                    "Target D/E ratio is required for WACC calculation",
                    Severity.ERROR
                )

            # Cost of debt
            cod = cap.get("cost_of_debt")
            if cod is None and target_de and target_de > 0:
                self._add_issue(
                    "capital_structure", "cost_of_debt",
                    "Cost of debt is required when using debt financing",
                    Severity.ERROR
                )
            elif cod is not None:
                self._check_range("capital_structure", "cost_of_debt", cod)

    def validate_terminal_value(self) -> None:
        """Validate terminal value assumptions."""
        tv = self.assumptions.get("terminal_value", {})
        method = self._get_assumption("model_config", "terminal_method")

        if method in ["perpetuity", "both"]:
            pg = tv.get("perpetuity_growth_rate")
            if pg is None:
                self._add_issue(
                    "terminal_value", "perpetuity_growth_rate",
                    "Perpetuity growth rate is required for Gordon Growth method",
                    Severity.ERROR
                )
            else:
                self._check_range("terminal_value", "perpetuity_growth_rate", pg)

                # Check that g < discount rate
                wacc = self._calculate_implied_wacc()
                if wacc and pg >= wacc:
                    self._add_issue(
                        "terminal_value", "perpetuity_growth_rate",
                        f"Growth rate ({pg:.1%}) must be less than WACC ({wacc:.1%})",
                        Severity.ERROR
                    )

        if method in ["exit_multiple", "both"]:
            em = tv.get("exit_multiple")
            if em is None:
                self._add_issue(
                    "terminal_value", "exit_multiple",
                    "Exit EBITDA multiple is required",
                    Severity.ERROR
                )
            else:
                self._check_range("terminal_value", "exit_multiple", em)

    def _calculate_implied_wacc(self) -> Optional[float]:
        """Calculate implied WACC from capital structure assumptions."""
        cap = self.assumptions.get("capital_structure", {})

        rf = cap.get("risk_free_rate")
        erp = cap.get("equity_risk_premium")
        beta = cap.get("beta")

        if not all([rf, erp, beta]):
            return None

        # Cost of equity (CAPM)
        ke = rf + beta * erp

        target_de = cap.get("target_debt_to_equity", 0)
        if target_de == 0:
            return ke

        cod = cap.get("cost_of_debt", 0.05)
        tax_rate = cap.get("tax_rate", 0.25)

        # WACC calculation
        d_ratio = target_de / (1 + target_de)
        e_ratio = 1 - d_ratio

        wacc = e_ratio * ke + d_ratio * cod * (1 - tax_rate)
        return wacc

    def validate_working_capital(self) -> None:
        """Validate working capital assumptions."""
        wc = self.assumptions.get("working_capital", {})

        if not wc:
            self._add_issue(
                "working_capital", "all",
                "Working capital assumptions are missing - will use historical averages",
                Severity.WARNING
            )
            return

        # DSO
        dso = wc.get("dso_days")
        if dso is not None:
            self._check_range("working_capital", "dso_days", dso)

        # DIO
        dio = wc.get("dio_days")
        if dio is not None:
            self._check_range("working_capital", "dio_days", dio)

        # DPO
        dpo = wc.get("dpo_days")
        if dpo is not None:
            self._check_range("working_capital", "dpo_days", dpo)

    def validate_capex(self) -> None:
        """Validate capital expenditure assumptions."""
        capex = self.assumptions.get("capex", {})

        if not capex:
            self._add_issue(
                "capex", "all",
                "CapEx assumptions are missing - will use historical averages",
                Severity.WARNING
            )
            return

        capex_pct = capex.get("capex_pct_revenue")
        if capex_pct is not None:
            self._check_range("capex", "capex_pct_revenue", capex_pct)

    def validate_scenarios(self) -> None:
        """Validate scenario analysis assumptions if present."""
        scenarios = self.assumptions.get("scenarios", {})

        if not scenarios:
            return  # Scenarios are optional

        required_scenarios = ["base", "bull", "bear"]
        for scenario in required_scenarios:
            if scenario not in scenarios:
                self._add_issue(
                    "scenarios", scenario,
                    f"'{scenario}' scenario is missing",
                    Severity.INFO
                )

    def validate_all(self) -> ValidationResult:
        """Run all validations."""
        self.validate_model_config()
        self.validate_revenue_assumptions()
        self.validate_cost_assumptions()
        self.validate_capital_structure()
        self.validate_terminal_value()
        self.validate_working_capital()
        self.validate_capex()
        self.validate_scenarios()

        return self.result

    def get_summary(self) -> dict:
        """Get validation summary."""
        errors = [i for i in self.result.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.result.issues if i.severity == Severity.WARNING]
        infos = [i for i in self.result.issues if i.severity == Severity.INFO]

        return {
            "is_valid": self.result.is_valid,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "info_count": len(infos),
            "errors": [{"field": e.field, "message": e.message} for e in errors],
            "warnings": [{"field": w.field, "message": w.message} for w in warnings],
            "missing_required": self.result.missing_required
        }


def main():
    """CLI interface for validating assumptions."""
    if len(sys.argv) < 2:
        print("Usage: validate_assumptions.py <assumptions.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        assumptions = json.load(f)

    validator = AssumptionValidator(assumptions)
    result = validator.validate_all()
    summary = validator.get_summary()

    print(f"\nValidation {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"  Errors: {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Info: {summary['info_count']}")

    if summary["errors"]:
        print("\nErrors (must fix):")
        for error in summary["errors"]:
            print(f"  - {error['field']}: {error['message']}")

    if summary["warnings"]:
        print("\nWarnings (review recommended):")
        for warning in summary["warnings"]:
            print(f"  - {warning['field']}: {warning['message']}")

    # Output JSON result
    output_file = input_file.replace(".json", "_validation.json")
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
