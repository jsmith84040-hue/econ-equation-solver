# equations/micro.py
from __future__ import annotations

from typing import List
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
P, Q = sp.symbols("P Q", real=True)

# Linear demand / supply
Qd, Qs = sp.symbols("Qd Qs", real=True)
a, b, c, d = sp.symbols("a b c d", real=True)

# Elasticities
eps_p = sp.symbols("eps_p", real=True)
dQ_dP = sp.symbols("dQ_dP", real=True)

eps_y = sp.symbols("eps_y", real=True)
dQ_dY = sp.symbols("dQ_dY", real=True)
Y_income = sp.symbols("Y_income", real=True)

eps_xy = sp.symbols("eps_xy", real=True)
dQx_dPy, Py, Qx = sp.symbols("dQx_dPy Py Qx", real=True)

# Revenue/cost/profit
TR, TC = sp.symbols("TR TC", real=True)
pi = sp.symbols("pi", real=True)

AC, MC, MR = sp.symbols("AC MC MR", real=True)

# Monopoly rule
eps = sp.symbols("eps", real=True)  # own price elasticity (negative for typical demand)

# Production
Y_out, A, K, L = sp.symbols("Y_out A K L", real=True)
alpha, beta = sp.symbols("alpha beta", real=True)

# CES production
delta, rho = sp.symbols("delta rho", real=True)

# -----------------------
# EQUATIONS
# -----------------------
EQUATIONS: List[EquationDef] = [
    # ---- Demand/Supply forms ----
    EquationDef(
        key="demand_linear",
        name="Linear Demand",
        description="Qd = a − bP",
        eq=sp.Eq(Qd, a - b * P),
        symbols=[Qd, a, b, P],
        defaults={a: 100.0, b: 2.0, P: 10.0},
        hints={Qd: "quantity demanded", a: "intercept", b: "slope", P: "price"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="supply_linear",
        name="Linear Supply",
        description="Qs = c + dP",
        eq=sp.Eq(Qs, c + d * P),
        symbols=[Qs, c, d, P],
        defaults={c: 10.0, d: 1.5, P: 10.0},
        hints={Qs: "quantity supplied", c: "intercept", d: "slope", P: "price"},
        result_type=ResultType.GENERIC,
    ),

    # ---- Elasticity variants (these trigger interpretations) ----
    EquationDef(
        key="elasticity_price_point",
        name="Price elasticity (point)",
        description="εp = (dQ/dP)·(P/Q)",
        eq=sp.Eq(eps_p, dQ_dP * (P / Q)),
        symbols=[eps_p, dQ_dP, P, Q],
        defaults={dQ_dP: -2.0, P: 10.0, Q: 50.0},
        hints={eps_p: "price elasticity", dQ_dP: "derivative", P: "price", Q: "quantity"},
        result_type=ResultType.ELASTICITY_PRICE,
    ),
    EquationDef(
        key="elasticity_income",
        name="Income elasticity",
        description="εy = (dQ/dY)·(Y/Q)",
        eq=sp.Eq(eps_y, dQ_dY * (Y_income / Q)),
        symbols=[eps_y, dQ_dY, Y_income, Q],
        defaults={dQ_dY: 0.01, Y_income: 50000.0, Q: 100.0},
        hints={eps_y: "income elasticity", dQ_dY: "derivative", Y_income: "income", Q: "quantity"},
        result_type=ResultType.ELASTICITY_INCOME,
    ),
    EquationDef(
        key="elasticity_cross",
        name="Cross-price elasticity",
        description="εxy = (dQx/dPy)·(Py/Qx)",
        eq=sp.Eq(eps_xy, dQx_dPy * (Py / Qx)),
        symbols=[eps_xy, dQx_dPy, Py, Qx],
        defaults={dQx_dPy: 1.2, Py: 8.0, Qx: 40.0},
        hints={eps_xy: "cross-price elasticity", dQx_dPy: "derivative", Py: "other good price", Qx: "quantity of x"},
        result_type=ResultType.ELASTICITY_CROSS,
    ),

    # ---- Monopoly rule / market power ----
    EquationDef(
        key="monopoly_pricing_rule",
        name="Monopoly pricing rule",
        description="P = MC / (1 + 1/ε)  (ε negative for typical demand)",
        eq=sp.Eq(P, MC / (1 + 1 / eps)),
        symbols=[P, MC, eps],
        defaults={MC: 10.0, eps: -2.0},
        hints={P: "price", MC: "marginal cost", eps: "elasticity (negative)"},
        result_type=ResultType.MONOPOLY_PRICING,
    ),

    # ---- Cost / revenue / profit basics ----
    EquationDef(
        key="total_revenue",
        name="Total revenue",
        description="TR = P·Q",
        eq=sp.Eq(TR, P * Q),
        symbols=[TR, P, Q],
        defaults={P: 10.0, Q: 20.0},
        hints={TR: "total revenue", P: "price", Q: "quantity"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="profit",
        name="Profit (accounting-style)",
        description="π = TR − TC",
        eq=sp.Eq(pi, TR - TC),
        symbols=[pi, TR, TC],
        defaults={TR: 1000.0, TC: 850.0},
        hints={pi: "profit", TR: "total revenue", TC: "total cost"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="average_cost",
        name="Average cost",
        description="AC = TC/Q",
        eq=sp.Eq(AC, TC / Q),
        symbols=[AC, TC, Q],
        defaults={TC: 850.0, Q: 20.0},
        hints={AC: "average cost", TC: "total cost", Q: "quantity"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="mr_equals_mc",
        name="Profit max condition",
        description="MR = MC",
        eq=sp.Eq(MR, MC),
        symbols=[MR, MC],
        defaults={MR: 15.0, MC: 15.0},
        hints={MR: "marginal revenue", MC: "marginal cost"},
        result_type=ResultType.GENERIC,
    ),

    # ---- Production functions ----
    EquationDef(
        key="cobb_douglas_prod",
        name="Cobb–Douglas production",
        description="Y = A·K^α·L^β",
        eq=sp.Eq(Y_out, A * (K ** alpha) * (L ** beta)),
        symbols=[Y_out, A, K, L, alpha, beta],
        defaults={A: 1.0, K: 100.0, L: 50.0, alpha: 0.30, beta: 0.70},
        hints={Y_out: "output", A: "TFP", K: "capital", L: "labor", alpha: "K exponent", beta: "L exponent"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="ces_prod",
        name="CES production",
        description="Y = A·[δK^(−ρ) + (1−δ)L^(−ρ)]^(−1/ρ)",
        eq=sp.Eq(
            Y_out,
            A * (delta * (K ** (-rho)) + (1 - delta) * (L ** (-rho))) ** (-1 / rho),
        ),
        symbols=[Y_out, A, delta, K, L, rho],
        defaults={A: 1.0, delta: 0.50, K: 100.0, L: 50.0, rho: 0.50},
        hints={Y_out: "output", A: "TFP", delta: "share parameter", K: "capital", L: "labor", rho: "substitution parameter"},
        result_type=ResultType.GENERIC,
    ),
]