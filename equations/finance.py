# equations/finance.py
from __future__ import annotations

from typing import List, Dict, Any
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
PV, FV, r, t = sp.symbols("PV FV r t", real=True)
PMT, n = sp.symbols("PMT n", real=True)
PV_ann = sp.symbols("PV_ann", real=True)

NPV = sp.symbols("NPV", real=True)
C0, C1, C2, C3 = sp.symbols("C0 C1 C2 C3", real=True)

# CAPM
E_Ri, Rf, beta, E_Rm = sp.symbols("E_Ri Rf beta E_Rm", real=True)

# -----------------------
# Interpreters
# -----------------------
def interpret_npv(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    val = float(result)
    if val > 0:
        summary = "NPV is **positive** → (rule-of-thumb) **accept** the project (adds value at this discount rate)."
    elif val < 0:
        summary = "NPV is **negative** → (rule-of-thumb) **reject** the project (destroys value at this discount rate)."
    else:
        summary = "NPV is **zero** → project is break-even at this discount rate."

    bullets = [
        "NPV depends heavily on the chosen discount rate.",
        "If comparing projects, use consistent assumptions about risk and timing.",
    ]
    return {"summary": summary, "bullets": [f"• {b}" for b in bullets], "warnings": [], "policy_notes": [], "chart": None}


def interpret_rate_basic(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    # Used when solving for r (rate); warns if rate looks implausible
    rr = float(result)
    warnings = []
    if rr < -0.99:
        warnings.append("Rate < −99% is not meaningful in standard discounting. Check inputs.")
    if rr > 1.0:
        warnings.append("Rate > 100% per period is unusually high—check units (annual vs monthly) and inputs.")

    summary = "Discount rate solved."
    bullets = [
        "Ensure r matches the timing of cash flows (per period).",
        "If rates are annual but cash flows are monthly, convert consistently.",
    ]
    return {"summary": summary, "bullets": [f"• {b}" for b in bullets], "warnings": warnings, "policy_notes": [], "chart": None}


def interpret_capm(result: float, solve_for: sp.Symbol, inputs: Dict[sp.Symbol, float]) -> Dict[str, Any]:
    eri = float(result)
    rf = float(inputs.get(Rf, 0.0))
    erm = float(inputs.get(E_Rm, 0.0))
    b = float(inputs.get(beta, 0.0))

    summary = "CAPM-implied expected return computed."
    bullets = [
        f"• If β > 1, the asset is more sensitive to market movements (higher systematic risk).",
        f"• Market risk premium here is (E[Rm] − Rf) = {(erm - rf):.2%}.",
        f"• With β = {b:.2f}, CAPM adds β·premium = {(b * (erm - rf)):.2%} to Rf.",
    ]
    warnings = []
    if eri < -0.5 or eri > 1.5:
        warnings.append("Expected return looks extreme; double-check rates are in decimals (0.08 for 8%).")

    return {"summary": summary, "bullets": bullets, "warnings": warnings, "policy_notes": [], "chart": None}


# -----------------------
# EQUATIONS
# -----------------------
EQUATIONS: List[EquationDef] = [
    EquationDef(
        key="present_value",
        name="Present Value",
        description="PV = FV / (1 + r)^t",
        eq=sp.Eq(PV, FV / (1 + r) ** t),
        symbols=[PV, FV, r, t],
        defaults={FV: 1000.0, r: 0.05, t: 3.0},
        hints={PV: "present value", FV: "future value", r: "rate (decimal)", t: "time (periods)"},
        result_type=ResultType.GENERIC,
        interpreter=None,  # base display is fine; rate sanity appears if you solve for r via r
    ),
    EquationDef(
        key="future_value",
        name="Future Value",
        description="FV = PV(1 + r)^t",
        eq=sp.Eq(FV, PV * (1 + r) ** t),
        symbols=[FV, PV, r, t],
        defaults={PV: 1000.0, r: 0.05, t: 3.0},
        hints={FV: "future value", PV: "present value", r: "rate (decimal)", t: "time (periods)"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="pv_of_annuity",
        name="PV of annuity",
        description="PV = PMT · (1 − (1 + r)^(−n)) / r",
        eq=sp.Eq(PV_ann, PMT * (1 - (1 + r) ** (-n)) / r),
        symbols=[PV_ann, PMT, r, n],
        defaults={PMT: 100.0, r: 0.05, n: 10.0},
        hints={PV_ann: "present value", PMT: "payment", r: "rate (decimal)", n: "number of periods"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="npv_3_cashflows",
        name="NPV (C0..C3)",
        description="NPV = −C0 + C1/(1+r) + C2/(1+r)^2 + C3/(1+r)^3",
        eq=sp.Eq(NPV, -C0 + C1 / (1 + r) + C2 / (1 + r) ** 2 + C3 / (1 + r) ** 3),
        symbols=[NPV, C0, C1, C2, C3, r],
        defaults={C0: 1000.0, C1: 450.0, C2: 450.0, C3: 450.0, r: 0.08},
        hints={NPV: "net present value", C0: "initial cost", C1: "cash flow 1", C2: "cash flow 2", C3: "cash flow 3", r: "discount rate"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_npv,
    ),
    EquationDef(
        key="capm",
        name="CAPM",
        description="E[Ri] = Rf + β(E[Rm] − Rf)",
        eq=sp.Eq(E_Ri, Rf + beta * (E_Rm - Rf)),
        symbols=[E_Ri, Rf, beta, E_Rm],
        defaults={Rf: 0.03, beta: 1.20, E_Rm: 0.08},
        hints={E_Ri: "expected return", Rf: "risk-free rate", beta: "beta", E_Rm: "market return"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_capm,
    ),

    # Optional helper: solve for discount rate from PV/FV/t (same equation; interpreter triggers if solve_for=r)
    EquationDef(
        key="rate_from_pv_fv",
        name="Solve rate from PV & FV",
        description="r = (FV/PV)^(1/t) − 1",
        eq=sp.Eq(r, (FV / PV) ** (1 / t) - 1),
        symbols=[r, FV, PV, t],
        defaults={FV: 1000.0, PV: 800.0, t: 3.0},
        hints={r: "rate (decimal)", FV: "future value", PV: "present value", t: "time (periods)"},
        result_type=ResultType.GENERIC,
        interpreter=interpret_rate_basic,
    ),
]
