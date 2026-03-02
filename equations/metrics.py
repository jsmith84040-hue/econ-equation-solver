# equations/metrics.py
from __future__ import annotations

from typing import List, Dict, Any
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
beta1_hat, SE_beta1 = sp.symbols("beta1_hat SE_beta1", real=True)
t_stat = sp.symbols("t_stat", real=True)

SSR, SST = sp.symbols("SSR SST", real=True)
R2 = sp.symbols("R2", real=True)

# OLS slope with summary stats
Sxy, Sxx = sp.symbols("Sxy Sxx", real=True)

# Log-log elasticity interpretation
b_loglog, elasticity = sp.symbols("b_loglog elasticity", real=True)

# -----------------------
# Interpreters
# -----------------------
def interpret_t(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    t = float(result)
    at = abs(t)

    # Rule-of-thumb two-sided critical values for large samples:
    # 10% ~ 1.64, 5% ~ 1.96, 1% ~ 2.58
    if at >= 2.58:
        sig = "Statistically significant at ~1% (two-sided, large-sample rule-of-thumb)."
    elif at >= 1.96:
        sig = "Statistically significant at ~5% (two-sided, large-sample rule-of-thumb)."
    elif at >= 1.64:
        sig = "Statistically significant at ~10% (two-sided, large-sample rule-of-thumb)."
    else:
        sig = "Not statistically significant at conventional 10%/5%/1% levels (rule-of-thumb)."

    bullets = [
        "Interpretation uses common large-sample critical values (approximate).",
        "In small samples, significance depends on degrees of freedom (t-distribution).",
        "Sign of t indicates direction of the estimated effect (given the sign of β̂).",
    ]

    return {
        "summary": sig,
        "bullets": [f"• {b}" for b in bullets],
        "warnings": [],
        "policy_notes": [],
        "chart": None,
    }


def interpret_r2(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    r2 = float(result)

    warnings = []
    if r2 < 0 or r2 > 1:
        warnings.append("R² is outside [0,1]. Check whether SSR/SST inputs are correct (or whether this is adjusted R², etc.).")

    if r2 < 0.2:
        summary = "Low explanatory power (rule-of-thumb)."
    elif r2 < 0.5:
        summary = "Moderate explanatory power (rule-of-thumb)."
    else:
        summary = "High explanatory power (rule-of-thumb)."

    bullets = [
        "R² is the fraction of variance in Y explained by the model (in-sample).",
        "High R² does not imply causality; low R² can still be fine depending on context (e.g., micro data).",
    ]

    return {
        "summary": summary,
        "bullets": [f"• {b}" for b in bullets],
        "warnings": warnings,
        "policy_notes": [],
        "chart": None,
    }

# -----------------------
# Equations
# -----------------------
EQUATIONS: List[EquationDef] = [
    EquationDef(
        key="ols_slope_beta1",
        name="OLS slope (β1̂)",
        description="β1̂ = Sxy / Sxx",
        eq=sp.Eq(beta1_hat, Sxy / Sxx),
        symbols=[beta1_hat, Sxy, Sxx],
        defaults={Sxy: 120.0, Sxx: 60.0},
        hints={beta1_hat: "estimated slope", Sxy: "Σ(x−x̄)(y−ȳ)", Sxx: "Σ(x−x̄)^2"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="t_statistic",
        name="t-statistic",
        description="t = β̂ / SE(β̂)",
        eq=sp.Eq(t_stat, beta1_hat / SE_beta1),
        symbols=[t_stat, beta1_hat, SE_beta1],
        defaults={beta1_hat: 1.50, SE_beta1: 0.50},
        hints={t_stat: "t statistic", beta1_hat: "estimate", SE_beta1: "standard error"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_t,
    ),
    EquationDef(
        key="r_squared",
        name="R-squared",
        description="R² = 1 − SSR/SST",
        eq=sp.Eq(R2, 1 - SSR / SST),
        symbols=[R2, SSR, SST],
        defaults={SSR: 40.0, SST: 100.0},
        hints={R2: "R-squared", SSR: "sum squared residuals", SST: "total sum squares"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_r2,
    ),
    EquationDef(
        key="loglog_elasticity",
        name="Log-log elasticity interpretation",
        description="If ln Q = a + b ln P, then elasticity = b",
        eq=sp.Eq(elasticity, b_loglog),
        symbols=[elasticity, b_loglog],
        defaults={b_loglog: -1.50},
        hints={elasticity: "elasticity", b_loglog: "log-log slope"},
        result_type=ResultType.ELASTICITY_PRICE,  # triggers elasticity + TR rule automatically
    ),
]
