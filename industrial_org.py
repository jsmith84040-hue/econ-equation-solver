# equations/industrial_org.py
from __future__ import annotations

from typing import List
import sympy as sp

from .core import EquationDef, ResultType

# -----------------------
# Symbols
# -----------------------
P, Q = sp.symbols("P Q", real=True)
MC, MR = sp.symbols("MC MR", real=True)
ATC, AVC = sp.symbols("ATC AVC", real=True)

# Demand / pricing
a, b = sp.symbols("a b", real=True)
eps = sp.symbols("eps", real=True)  # own-price elasticity (typically negative)

# Cournot
n = sp.symbols("n", real=True, positive=True)
q_i = sp.symbols("q_i", real=True)

# Concentration / HHI
HHI = sp.symbols("HHI", real=True)
s1, s2 = sp.symbols("s1 s2", real=True)  # shares in percentage points (e.g., 30 for 30%)

# Merger / synergy
V_A, V_B, V_M, Synergy = sp.symbols("V_A V_B V_M Synergy", real=True)

# Vertical integration (double marginalization, stylized)
MC_u, MC_d = sp.symbols("MC_u MC_d", real=True)

# Lerner / markup
Lerner = sp.symbols("Lerner", real=True)
Markup = sp.symbols("Markup", real=True)

# Rule-of-thumb link (Cournot-ish)
abs_eps = sp.symbols("abs_eps", real=True, positive=True)

# Cross-price elasticity (useful in merger analysis)
eps_xy = sp.symbols("eps_xy", real=True)
dQx_dPy, Py, Qx = sp.symbols("dQx_dPy Py Qx", real=True)

# -----------------------
# Equations
# -----------------------
EQUATIONS: List[EquationDef] = [
    # ---- Perfect competition basics ----
    EquationDef(
        key="pc_price_equals_mc",
        name="Perfect competition: P = MC",
        description="P = MC",
        eq=sp.Eq(P, MC),
        symbols=[P, MC],
        defaults={MC: 10.0},
        hints={P: "price", MC: "marginal cost"},
        result_type=ResultType.MONOPOLY_PRICING,  # triggers P vs MC efficiency note
    ),
    EquationDef(
        key="shutdown_threshold",
        name="Shutdown threshold (short run)",
        description="P = AVC (operate if P ≥ AVC)",
        eq=sp.Eq(P, AVC),
        symbols=[P, AVC],
        defaults={AVC: 8.0},
        hints={P: "price", AVC: "avg variable cost"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="profit_from_atc",
        name="Profit using ATC",
        description="π = (P − ATC)·Q",
        eq=sp.Eq(sp.Symbol("pi", real=True), (P - ATC) * Q),
        symbols=[sp.Symbol("pi", real=True), P, ATC, Q],
        defaults={P: 12.0, ATC: 10.0, Q: 100.0},
        hints={sp.Symbol("pi", real=True): "profit", P: "price", ATC: "avg total cost", Q: "quantity"},
        result_type=ResultType.GENERIC,
    ),

    # ---- Monopoly / market power ----
    EquationDef(
        key="monopoly_mr_equals_mc",
        name="Monopoly: MR = MC",
        description="MR = MC",
        eq=sp.Eq(MR, MC),
        symbols=[MR, MC],
        defaults={MR: 10.0, MC: 10.0},
        hints={MR: "marginal revenue", MC: "marginal cost"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="mr_linear_inverse_demand",
        name="MR from inverse demand (P = a − bQ)",
        description="If P = a − bQ then MR = a − 2bQ",
        eq=sp.Eq(MR, a - 2 * b * Q),
        symbols=[MR, a, b, Q],
        defaults={a: 100.0, b: 1.0, Q: 20.0},
        hints={MR: "marginal revenue", a: "intercept", b: "slope", Q: "total quantity"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="lerner_index_def",
        name="Lerner index (definition)",
        description="L = (P − MC)/P",
        eq=sp.Eq(Lerner, (P - MC) / P),
        symbols=[Lerner, P, MC],
        defaults={P: 15.0, MC: 10.0},
        hints={Lerner: "Lerner index", P: "price", MC: "marginal cost"},
        result_type=ResultType.MARKET_POWER,  # will interpret magnitude + note P>MC if both known
    ),
    EquationDef(
        key="lerner_elasticity_form",
        name="Lerner index (elasticity form)",
        description="(P − MC)/P = −1/ε (ε negative for typical demand)",
        eq=sp.Eq((P - MC) / P, -1 / eps),
        symbols=[P, MC, eps],
        defaults={MC: 10.0, eps: -2.0, P: 15.0},
        hints={P: "price", MC: "marginal cost", eps: "elasticity (negative)"},
        result_type=ResultType.MONOPOLY_PRICING,  # triggers allocative inefficiency warning when P>MC
    ),
    EquationDef(
        key="monopoly_pricing_rule",
        name="Monopoly pricing rule",
        description="P = MC / (1 + 1/ε) (ε negative ⇒ P > MC)",
        eq=sp.Eq(P, MC / (1 + 1 / eps)),
        symbols=[P, MC, eps],
        defaults={MC: 10.0, eps: -2.0},
        hints={P: "price", MC: "marginal cost", eps: "elasticity (negative)"},
        result_type=ResultType.MONOPOLY_PRICING,  # triggers allocative inefficiency warning when P>MC
    ),
    EquationDef(
        key="markup_ratio",
        name="Markup ratio",
        description="Markup = P/MC",
        eq=sp.Eq(Markup, P / MC),
        symbols=[Markup, P, MC],
        defaults={P: 15.0, MC: 10.0},
        hints={Markup: "markup ratio", P: "price", MC: "marginal cost"},
        result_type=ResultType.MARKET_POWER,
    ),

    # ---- Cournot oligopoly (identical firms, linear inverse demand P = a − bQ) ----
    EquationDef(
        key="cournot_firm_output",
        name="Cournot: firm output",
        description="q_i = (a − MC) / (b(n + 1))",
        eq=sp.Eq(q_i, (a - MC) / (b * (n + 1))),
        symbols=[q_i, a, MC, b, n],
        defaults={a: 100.0, MC: 20.0, b: 1.0, n: 3.0},
        hints={q_i: "firm output", a: "intercept", MC: "marginal cost", b: "slope", n: "number of firms"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="cournot_total_output",
        name="Cournot: total output",
        description="Q = n(a − MC) / (b(n + 1))",
        eq=sp.Eq(Q, n * (a - MC) / (b * (n + 1))),
        symbols=[Q, a, MC, b, n],
        defaults={a: 100.0, MC: 20.0, b: 1.0, n: 3.0},
        hints={Q: "total output", a: "intercept", MC: "marginal cost", b: "slope", n: "number of firms"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="cournot_price",
        name="Cournot: price from inverse demand",
        description="P = a − bQ",
        eq=sp.Eq(P, a - b * Q),
        symbols=[P, a, b, Q],
        defaults={a: 100.0, b: 1.0, Q: 60.0},
        hints={P: "price", a: "intercept", b: "slope", Q: "total output"},
        result_type=ResultType.GENERIC,
    ),

    # ---- Concentration / merger screens ----
    EquationDef(
        key="hhi_components",
        name="HHI (components)",
        description="HHI = s1^2 + s2^2 + (sum of squared other shares)  (shares in % points)",
        eq=sp.Eq(HHI, s1**2 + s2**2 + sp.Symbol("s3_sq_plus", real=True)),
        symbols=[HHI, s1, s2, sp.Symbol("s3_sq_plus", real=True)],
        defaults={s1: 30.0, s2: 20.0, sp.Symbol("s3_sq_plus", real=True): 900.0},
        hints={
            HHI: "Herfindahl–Hirschman Index",
            s1: "share 1 (%)",
            s2: "share 2 (%)",
            sp.Symbol("s3_sq_plus", real=True): "Σ(other shares²)",
        },
        result_type=ResultType.CONCENTRATION_HHI,  # triggers concentration tier + policy note
    ),
    EquationDef(
        key="delta_hhi_merger",
        name="ΔHHI from merger",
        description="ΔHHI = 2·s1·s2  (shares in % points)",
        eq=sp.Eq(sp.Symbol("delta_HHI", real=True), 2 * s1 * s2),
        symbols=[sp.Symbol("delta_HHI", real=True), s1, s2],
        defaults={s1: 30.0, s2: 20.0},
        hints={
            sp.Symbol("delta_HHI", real=True): "change in HHI",
            s1: "merging firm 1 share (%)",
            s2: "merging firm 2 share (%)",
        },
        result_type=ResultType.DELTA_HHI,  # triggers merger red-flag policy notes
    ),

    # ---- Merger value / synergy ----
    EquationDef(
        key="merger_value_identity",
        name="Merger value identity",
        description="V_Merged = V_A + V_B + Synergy",
        eq=sp.Eq(V_M, V_A + V_B + Synergy),
        symbols=[V_M, V_A, V_B, Synergy],
        defaults={V_A: 1000.0, V_B: 800.0, Synergy: 150.0},
        hints={V_M: "merged value", V_A: "firm A value", V_B: "firm B value", Synergy: "synergy"},
        result_type=ResultType.GENERIC,
    ),
    EquationDef(
        key="synergy_from_values",
        name="Synergy from values",
        description="Synergy = V_Merged − (V_A + V_B)",
        eq=sp.Eq(Synergy, V_M - (V_A + V_B)),
        symbols=[Synergy, V_M, V_A, V_B],
        defaults={V_M: 2000.0, V_A: 1000.0, V_B: 800.0},
        hints={Synergy: "synergy", V_M: "merged value", V_A: "firm A value", V_B: "firm B value"},
        result_type=ResultType.SYNERGY,  # triggers positive/negative synergy interpretation
    ),

    # ---- Vertical integration (stylized) ----
    EquationDef(
        key="integrated_mc_sum",
        name="Integrated MC (stylized)",
        description="MC_total = MC_u + MC_d",
        eq=sp.Eq(sp.Symbol("MC_total", real=True), MC_u + MC_d),
        symbols=[sp.Symbol("MC_total", real=True), MC_u, MC_d],
        defaults={MC_u: 4.0, MC_d: 6.0},
        hints={sp.Symbol("MC_total", real=True): "combined MC", MC_u: "upstream MC", MC_d: "downstream MC"},
        result_type=ResultType.GENERIC,
    ),

    # ---- Cournot-ish rule of thumb: Lerner ≈ HHI / |ε| ----
    EquationDef(
        key="lerner_hhi_rule_of_thumb",
        name="Lerner ≈ HHI/|ε| (rule of thumb)",
        description="(P−MC)/P ≈ HHI/|ε| (enter HHI as a decimal like 0.25, not 2500)",
        eq=sp.Eq(Lerner, HHI / abs_eps),
        symbols=[Lerner, HHI, abs_eps],
        defaults={HHI: 0.25, abs_eps: 2.0},
        hints={Lerner: "Lerner index", HHI: "HHI (decimal)", abs_eps: "|ε|"},
        result_type=ResultType.MARKET_POWER,
    ),

    # ---- Cross-price elasticity (merger substitution check) ----
    EquationDef(
        key="cross_price_elasticity",
        name="Cross-price elasticity",
        description="εxy = (dQx/dPy)·(Py/Qx)",
        eq=sp.Eq(eps_xy, dQx_dPy * (Py / Qx)),
        symbols=[eps_xy, dQx_dPy, Py, Qx],
        defaults={dQx_dPy: 1.2, Py: 8.0, Qx: 40.0},
        hints={eps_xy: "cross elasticity", dQx_dPy: "derivative", Py: "price of y", Qx: "quantity of x"},
        result_type=ResultType.ELASTICITY_CROSS,
    ),
]