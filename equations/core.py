# equations/core.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import sympy as sp


class ResultType(str, Enum):
    GENERIC = "generic"
    ELASTICITY_PRICE = "elasticity_price"
    ELASTICITY_INCOME = "elasticity_income"
    ELASTICITY_CROSS = "elasticity_cross"
    PROFIT_ECON = "profit_economic"
    PROFIT_ACCT = "profit_accounting"
    MARKET_POWER = "market_power"
    MONOPOLY_PRICING = "monopoly_pricing"
    CONCENTRATION_HHI = "concentration_hhi"
    DELTA_HHI = "delta_hhi"
    SYNERGY = "synergy"


@dataclass(frozen=True)
class EquationDef:
    key: str
    name: str
    description: str
    eq: sp.Eq
    symbols: List[sp.Symbol]
    defaults: Dict[sp.Symbol, float]
    hints: Dict[sp.Symbol, str]

    # Interpretation engine hook:
    result_type: ResultType = ResultType.GENERIC

    # Optional custom interpreter:
    # signature: (result_value, solve_for_symbol, inputs_dict) -> payload dict
    # payload keys: summary, bullets, warnings, policy_notes, chart
    interpreter: Optional[Callable[[float, sp.Symbol, Dict[sp.Symbol, float]], Dict[str, Any]]] = None


def solve_equation(eq_def: EquationDef, solve_for: sp.Symbol, values: Dict[sp.Symbol, float]) -> List[float]:
    """
    Substitute known values into the equation and solve for 'solve_for'.
    Returns a list of unique real numeric solutions.
    """
    subs = {s: float(v) for s, v in values.items() if s != solve_for}

    eq_subbed = sp.Eq(eq_def.eq.lhs.subs(subs), eq_def.eq.rhs.subs(subs))
    sols = sp.solve(eq_subbed, solve_for, dict=False)

    if not isinstance(sols, (list, tuple)):
        sols = [sols]

    numeric: List[float] = []
    for sol in sols:
        sol_n = sp.N(sol)
        if sol_n.is_real is False:
            continue
        try:
            numeric.append(float(sol_n))
        except Exception:
            continue

    # De-dupe near-equals
    out: List[float] = []
    for x in numeric:
        if not any(abs(x - y) < 1e-9 for y in out):
            out.append(x)
    return out
