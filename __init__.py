# equations/__init__.py

from .core import EquationDef, solve_equation

from .micro import EQUATIONS as MICRO
from .macro import EQUATIONS as MACRO
from .metrics import EQUATIONS as METRICS
from .finance import EQUATIONS as FINANCE
from .international import EQUATIONS as INTERNATIONAL
from .industrial_org import EQUATIONS as INDUSTRIAL_ORG

CATEGORIES = {
    "Micro": MICRO,
    "Macro": MACRO,
    "Metrics": METRICS,
    "Finance": FINANCE,
    "International": INTERNATIONAL,
    "Industrial Org": INDUSTRIAL_ORG,
}