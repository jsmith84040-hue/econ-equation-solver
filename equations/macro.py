# equations/macro.py
from __future__ import annotations

from typing import List
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
Y, C, I, G = sp.symbols("Y C I G", real=True)
X, M_imp = sp.symbols("X M_imp", real=True)
T = sp.symbols("T", real=True)

# Savings identity
S = sp.symbols("S", real=True)

# Fisher / rates
i, r, pi_e = sp.symbols("i r pi_e", real=True)

# Quantity theory
M, V, P_level = sp.symbols("M V P_level", real=True)

# Money demand (linear LM block)
k, h = sp.symbols("k h", real=True)

# Growth accounting
gY, gA, gK, gL, alpha = sp.symbols("gY gA gK gL alpha", real=True)

EQUATIONS: List[EquationDef] = [
    EquationDef(
        key="gdp_identity",
        name="GDP identity",
        description="Y = C + I + G + (X − M)",
        eq=sp.Eq(Y, C + I + G + (X - M_imp)),
        symbols=[Y, C, I, G, X, M_imp],
        defaults={C: 500.0, I: 200.0, G: 150.0, X: 100.0, M_imp: 80.0},
        hints={Y: "GDP", C: "consumption", I: "investment", G: "gov spending", X: "exports", M_imp: "imports"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="savings_identity",
        name="National saving (closed economy style)",
        description="S = Y − C − G",
        eq=sp.Eq(S, Y - C - G),
        symbols=[S, Y, C, G],
        defaults={Y: 1000.0, C: 650.0, G: 200.0},
        hints={S: "national saving", Y: "income/output", C: "consumption", G: "government spending"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="fisher_equation",
        name="Fisher equation",
        description="i = r + πᵉ",
        eq=sp.Eq(i, r + pi_e),
        symbols=[i, r, pi_e],
        defaults={r: 0.02, pi_e: 0.03},
        hints={i: "nominal rate", r: "real rate", pi_e: "expected inflation"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="quantity_theory",
        name="Quantity theory of money",
        description="M·V = P·Y",
        eq=sp.Eq(M * V, P_level * Y),
        symbols=[M, V, P_level, Y],
        defaults={M: 100.0, V: 1.50, P_level: 2.00, Y: 75.00},
        hints={M: "money supply", V: "velocity", P_level: "price level", Y: "real output"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="money_demand_lm_block",
        name="Money demand (LM building block)",
        description="M/P = kY − h i",
        eq=sp.Eq(M / P_level, k * Y - h * i),
        symbols=[M, P_level, k, Y, h, i],
        defaults={M: 500.0, P_level: 2.00, k: 0.50, Y: 1000.0, h: 50.0, i: 0.05},
        hints={M: "money supply", P_level: "price level", k: "income sensitivity", Y: "income", h: "rate sensitivity", i: "interest rate"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="growth_accounting",
        name="Growth accounting",
        description="gY = gA + α gK + (1−α) gL",
        eq=sp.Eq(gY, gA + alpha * gK + (1 - alpha) * gL),
        symbols=[gY, gA, alpha, gK, gL],
        defaults={gA: 0.01, alpha: 0.33, gK: 0.03, gL: 0.01},
        hints={gY: "output growth", gA: "TFP growth", alpha: "capital share", gK: "capital growth", gL: "labor growth"},
        result_type=ResultType.GENERIC,
    ),
]
