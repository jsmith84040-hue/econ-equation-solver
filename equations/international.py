# equations/international.py
from __future__ import annotations

from typing import List, Dict, Any
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
# Convention: e = domestic currency per 1 unit foreign currency
# Example: if e = 1.20, it takes 1.20 domestic currency to buy 1 foreign currency.
e, P, P_star = sp.symbols("e P P_star", real=True)

# Real exchange rate
q = sp.symbols("q", real=True)

# Uncovered interest parity
i, i_star = sp.symbols("i i_star", real=True)
E_e_next = sp.symbols("E_e_next", real=True)

# -----------------------
# Interpreters
# -----------------------
def interpret_ppp(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    warnings = []
    P_val = inputs.get(P, None)
    Pstar_val = inputs.get(P_star, None)
    if P_val is not None and P_val <= 0:
        warnings.append("Domestic price level P should be > 0. Check inputs.")
    if Pstar_val is not None and Pstar_val <= 0:
        warnings.append("Foreign price level P* should be > 0. Check inputs.")

    summary = "PPP-implied nominal exchange rate computed."
    bullets = [
        "PPP is a long-run benchmark; short-run exchange rates can deviate due to sticky prices, capital flows, trade costs, etc.",
        "Be consistent with units (price indices vs absolute price levels).",
    ]
    return {"summary": summary, "bullets": [f"• {b}" for b in bullets], "warnings": warnings, "policy_notes": [], "chart": None}


def interpret_real_fx(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    q_val = float(result)
    warnings = []
    if q_val <= 0:
        warnings.append("Real exchange rate q should usually be > 0. Check inputs and definitions.")

    summary = "Real exchange rate computed."
    bullets = [
        "With e = domestic per foreign, higher e usually means nominal depreciation of domestic currency.",
        "Higher q typically corresponds to **real depreciation** (foreign goods relatively more expensive vs domestic).",
        "Interpretation depends on the exact convention used for e (always confirm).",
    ]
    return {"summary": summary, "bullets": [f"• {b}" for b in bullets], "warnings": warnings, "policy_notes": [], "chart": None}


def interpret_uip(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    # If solving for i, interpret the expected depreciation term
    warnings = []
    e0 = inputs.get(e, None)
    ee = inputs.get(E_e_next, None)
    if e0 is not None and e0 <= 0:
        warnings.append("Current exchange rate e should be > 0 under this convention.")
    if ee is not None and ee <= 0:
        warnings.append("Expected future exchange rate E[e_{t+1}] should be > 0.")

    summary = "UIP relationship computed (uncovered interest parity)."
    bullets = [
        "UIP says interest differentials reflect expected currency depreciation/appreciation (risk-neutral, frictionless benchmark).",
        "In practice, risk premia and expectations errors often cause UIP deviations.",
    ]

    if e0 is not None and ee is not None and e0 > 0:
        exp_dep = (ee - e0) / e0
        bullets.append(f"• Implied expected depreciation (E[e_{t+1}]−e_t)/e_t ≈ {exp_dep:.2%}.")
        if exp_dep > 0:
            bullets.append("• Positive expected depreciation (domestic currency expected to **depreciate**) tends to raise domestic interest rate i relative to i* in UIP.")
        elif exp_dep < 0:
            bullets.append("• Negative expected depreciation (domestic currency expected to **appreciate**) tends to lower i relative to i* in UIP.")
        else:
            bullets.append("• No expected FX change implies i ≈ i* under UIP (ignoring risk premia).")

    return {"summary": summary, "bullets": bullets, "warnings": warnings, "policy_notes": [], "chart": None}


# -----------------------
# EQUATIONS
# -----------------------
EQUATIONS: List[EquationDef] = [
    EquationDef(
        key="ppp",
        name="Purchasing Power Parity (PPP)",
        description="e = P / P*",
        eq=sp.Eq(e, P / P_star),
        symbols=[e, P, P_star],
        defaults={P: 120.0, P_star: 100.0},
        hints={e: "nominal FX (domestic per foreign)", P: "domestic price level", P_star: "foreign price level"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_ppp,
    ),
    EquationDef(
        key="real_exchange_rate",
        name="Real exchange rate",
        description="q = e·P* / P",
        eq=sp.Eq(q, e * P_star / P),
        symbols=[q, e, P_star, P],
        defaults={e: 1.20, P_star: 100.0, P: 120.0},
        hints={q: "real FX", e: "nominal FX (domestic per foreign)", P_star: "foreign price level", P: "domestic price level"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_real_fx,
    ),
    EquationDef(
        key="uip",
        name="Uncovered Interest Parity (UIP)",
        description="i = i* + (E[e_{t+1}] − e_t)/e_t",
        eq=sp.Eq(i, i_star + (E_e_next - e) / e),
        symbols=[i, i_star, E_e_next, e],
        defaults={i_star: 0.03, E_e_next: 1.25, e: 1.20},
        hints={i: "domestic interest rate", i_star: "foreign interest rate", E_e_next: "expected future FX", e: "current FX"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_uip,
    ),
]
