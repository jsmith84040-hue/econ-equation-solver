# app.py
from __future__ import annotations

import sympy as sp
import streamlit as st
import matplotlib.pyplot as plt

from equations import CATEGORIES, solve_equation
from equations.core import ResultType

st.set_page_config(page_title="Econ Equation Solver", layout="centered")
st.title("📚 Econ Equation Solver")

# 2-decimal display for inputs
INPUT_FORMAT = "%.2f"


# -------------------------
# Interpretation helpers
# -------------------------
def base_interpretation(eq_def, result: float, solve_for: sp.Symbol, inputs: dict):
    """
    Default interpretations based on ResultType (used when eq_def.interpreter is None).
    Returns a payload dict with optional fields:
      summary, bullets, warnings, policy_notes, chart
    """
    summary = ""
    bullets = []
    warnings = []
    policy_notes = []
    chart = None

    rt = eq_def.result_type

    # ---- Elasticities ----
    if rt == ResultType.ELASTICITY_PRICE:
        e = float(result)
        mag = abs(e)

        if mag > 1:
            summary = "Demand is **elastic** (|ε| > 1)."
        elif mag < 1:
            summary = "Demand is **inelastic** (|ε| < 1)."
        else:
            summary = "Demand is **unit elastic** (|ε| = 1)."

        bullets.append("**Total revenue rule (price ↑):**")
        if mag < 1:
            bullets.append("• If demand is **inelastic**, **TR increases** when price rises (quantity falls proportionally less).")
        elif mag > 1:
            bullets.append("• If demand is **elastic**, **TR decreases** when price rises (quantity falls proportionally more).")
        else:
            bullets.append("• If demand is **unit elastic**, **TR is roughly unchanged** with a small price increase (local approximation).")

        if e > 0:
            warnings.append(
                "Price elasticity is positive here. For a typical downward-sloping demand curve, ε should be negative—double-check signs/inputs."
            )
        else:
            bullets.append("• Negative ε is consistent with a downward-sloping demand curve.")

        # Optional curve demo if we can infer (P,Q) from inputs
        P_val = inputs.get(sp.Symbol("P", real=True))
        Q_val = inputs.get(sp.Symbol("Q", real=True))
        if P_val is not None and Q_val is not None and float(P_val) > 0 and float(Q_val) > 0:
            chart = {"type": "elasticity_demo", "P": float(P_val), "Q": float(Q_val), "eps": e}

    elif rt == ResultType.ELASTICITY_INCOME:
        ey = float(result)
        if ey > 0:
            summary = "This is a **normal good** (income elasticity > 0)."
        elif ey < 0:
            summary = "This is an **inferior good** (income elasticity < 0)."
        else:
            summary = "This good is **income-neutral** (income elasticity = 0)."

        if ey > 1:
            bullets.append("• Income elasticity > 1 suggests a **luxury** (quantity rises more than proportionally with income).")
        elif 0 < ey < 1:
            bullets.append("• 0 < income elasticity < 1 suggests a **necessity** (quantity rises less than proportionally).")

    elif rt == ResultType.ELASTICITY_CROSS:
        exy = float(result)
        if exy > 0:
            summary = "Goods are **substitutes** (cross-price elasticity > 0)."
        elif exy < 0:
            summary = "Goods are **complements** (cross-price elasticity < 0)."
        else:
            summary = "Goods look **unrelated** (cross-price elasticity ≈ 0)."

    # ---- Profits ----
    elif rt == ResultType.PROFIT_ECON:
        pe = float(result)
        if pe > 0:
            summary = "Positive **economic profit** (above normal profit)."
        elif pe < 0:
            summary = "**Economic loss** (below normal profit)."
        else:
            summary = "**Normal profit** (economic profit = 0)."
        bullets.append("• Economic profit includes **opportunity costs** (implicit costs).")

    elif rt == ResultType.PROFIT_ACCT:
        pa = float(result)
        if pa > 0:
            summary = "Positive **accounting profit**."
        elif pa < 0:
            summary = "**Accounting loss**."
        else:
            summary = "Break-even on an **accounting** basis."
        bullets.append("• Accounting profit excludes implicit/opportunity costs.")

    # ---- Market power / monopoly efficiency ----
    elif rt in (ResultType.MARKET_POWER, ResultType.MONOPOLY_PRICING):
        # Allocative inefficiency check if both P and MC are available as inputs
        P_sym = sp.Symbol("P", real=True)
        MC_sym = sp.Symbol("MC", real=True)
        P_val = inputs.get(P_sym)
        MC_val = inputs.get(MC_sym)

        if P_val is not None and MC_val is not None:
            try:
                P_f = float(P_val)
                MC_f = float(MC_val)
                if P_f > MC_f:
                    warnings.append("**Allocative inefficiency:** price exceeds marginal cost (**P > MC**).")
                elif abs(P_f - MC_f) < 1e-9:
                    summary = "Price equals marginal cost (**P = MC**), consistent with allocative efficiency in the basic model."
                else:
                    warnings.append("P < MC detected; check whether the equation/inputs are consistent for your context.")
            except Exception:
                pass

        # If the solved object is Lerner-like, give a simple market power read
        if eq_def.key.lower().find("lerner") >= 0 or "Lerner" in str(solve_for):
            L = float(result)
            summary = f"Lerner index suggests **markup intensity** of about {L:.2f}."
            if L > 0.4:
                bullets.append("• High market power (rule-of-thumb).")
            elif L > 0.2:
                bullets.append("• Moderate market power (rule-of-thumb).")
            else:
                bullets.append("• Low market power (rule-of-thumb).")

    # ---- Concentration / merger screens ----
    elif rt == ResultType.CONCENTRATION_HHI:
        hhi = float(result)
        if hhi < 1500:
            summary = "HHI suggests an **unconcentrated** market (< 1500)."
        elif hhi <= 2500:
            summary = "HHI suggests a **moderately concentrated** market (1500–2500)."
        else:
            summary = "HHI suggests a **highly concentrated** market (> 2500)."

        policy_notes.append("Merger review often flags more concern when markets are highly concentrated and ΔHHI is large.")

    elif rt == ResultType.DELTA_HHI:
        dhhi = float(result)
        summary = f"ΔHHI ≈ {dhhi:.0f} (shares entered in percentage points)."

        if dhhi >= 200:
            policy_notes.append("**Merger red flag:** ΔHHI ≥ 200 can raise competitive concerns, especially if baseline HHI is high.")
        elif dhhi >= 100:
            policy_notes.append("ΔHHI in the 100–200 range can warrant scrutiny depending on baseline HHI and market facts.")
        else:
            policy_notes.append("Small ΔHHI typically indicates lower concentration change—still depends on baseline HHI and market facts.")

    elif rt == ResultType.SYNERGY:
        syn = float(result)
        if syn > 0:
            summary = "Positive synergy estimate (merged value exceeds standalone sum)."
        elif syn < 0:
            summary = "Negative synergy estimate (merged value below standalone sum)."
        else:
            summary = "No estimated synergy."

    return {
        "summary": summary,
        "bullets": bullets,
        "warnings": warnings,
        "policy_notes": policy_notes,
        "chart": chart,
    }


def render_chart(chart_spec):
    """Optional visualization: elasticity demonstration curve through a point (isoelastic)."""
    if not chart_spec:
        return

    if chart_spec.get("type") == "elasticity_demo":
        P0 = float(chart_spec["P"])
        Q0 = float(chart_spec["Q"])
        eps = float(chart_spec["eps"])

        if P0 <= 0 or Q0 <= 0:
            return

        # Isoelastic curve through (P0, Q0): Q = k * P^eps
        k = Q0 / (P0 ** eps)

        P_min = max(P0 * 0.25, 0.01)
        P_max = P0 * 2.0
        grid = [P_min + (P_max - P_min) * i / 100 for i in range(101)]
        Q_grid = [k * (p ** eps) for p in grid]

        fig = plt.figure()
        plt.plot(grid, Q_grid)
        plt.scatter([P0], [Q0])
        plt.xlabel("Price (P)")
        plt.ylabel("Quantity (Q)")
        plt.title("Demand curve through your point (isoelastic demo)")
        st.pyplot(fig)


# -------------------------
# UI
# -------------------------
category = st.selectbox("Category", list(CATEGORIES.keys()))
eq_list = CATEGORIES[category]
eq_by_name = {e.name: e for e in eq_list}

eq_name = st.selectbox("Equation", list(eq_by_name.keys()))
eq_def = eq_by_name[eq_name]

st.caption(eq_def.description)
st.latex(sp.latex(eq_def.eq))

show_graphs = st.toggle("Show graphs (when available)", value=False)

st.markdown("### Mark known variables and enter values")

known_map = {}
values = {}


def label_for(sym: sp.Symbol) -> str:
    hint = eq_def.hints.get(sym, "")
    return f"{sym} — {hint}".strip(" —")


for sym in eq_def.symbols:
    col1, col2 = st.columns([1, 2])

    with col1:
        # Default: first symbol unknown, rest known
        default_known = (sym != eq_def.symbols[0])
        known = st.checkbox("Known", value=default_known, key=f"known_{category}_{eq_def.key}_{sym}")
        known_map[sym] = known

    with col2:
        if known:
            default = float(eq_def.defaults.get(sym, 0.0))
            # Smaller step for common rate-like variables
            step = 0.01 if str(sym) in {"r", "i", "pi_e", "i_star", "Rf", "E_Rm"} else 1.00
            values[sym] = st.number_input(
                label_for(sym),
                value=round(default, 2),
                step=step,
                format=INPUT_FORMAT,
                key=f"val_{category}_{eq_def.key}_{sym}",
            )
        else:
            st.write(f"**{sym}** will be solved for.")

unknowns = [s for s, is_known in known_map.items() if not is_known]

st.markdown("---")
if st.button("✅ Solve", type="primary"):
    if len(unknowns) != 1:
        st.error(
            f"Mark exactly **one** variable as unknown. "
            f"Currently unknown: {', '.join(str(u) for u in unknowns) if unknowns else '(none)'}"
        )
    else:
        solve_for = unknowns[0]
        try:
            sols = solve_equation(eq_def, solve_for, values)

            if len(sols) == 0:
                st.error("No numeric real solution found with the current known values.")
            elif len(sols) == 1:
                result = sols[0]
                st.success(f"{solve_for} = {result:,.2f}")

                # Interpretation (custom interpreter overrides default engine)
                if eq_def.interpreter:
                    payload = eq_def.interpreter(result, solve_for, values)
                else:
                    payload = base_interpretation(eq_def, result, solve_for, values)

                if payload:
                    if payload.get("summary"):
                        st.info(payload["summary"])

                    if payload.get("bullets"):
                        st.markdown("**Notes**")
                        for b in payload["bullets"]:
                            st.write(b)

                    if payload.get("warnings"):
                        st.markdown("**Warnings**")
                        for w in payload["warnings"]:
                            st.warning(w)

                    if payload.get("policy_notes"):
                        st.markdown("**Policy / decision notes**")
                        for p in payload["policy_notes"]:
                            st.write(f"• {p}")

                    if show_graphs:
                        render_chart(payload.get("chart"))

            else:
                st.warning(f"Multiple solutions for {solve_for}:")
                for idx, v in enumerate(sols, start=1):
                    st.write(f"{idx}. {solve_for} = {v:,.2f}")

        except ZeroDivisionError:
            st.error("Division by zero — check your inputs.")
        except Exception as e:
            st.error(f"Error: {e}")
            