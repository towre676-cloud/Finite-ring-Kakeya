"""Isolated exact-maximum next-frontier encoder; no SAT search here.

Supported calls: support13 / maximum12 or13; support14 / maximum11.
The total budget is exactly93 and residue0 is a largest fibre of the
specified exact weight. Disabled mode is byte-identical to the frozen
selector-export baseline. All earlier producers remain unchanged.
"""
from pathlib import Path
import hashlib
import importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("r8_next_frontier_incidence_cuts", HERE / "incidence_cuts.py")
I = importlib.util.module_from_spec(spec); spec.loader.exec_module(I)
append_next_frontier_cuts = I.append_next_frontier_cuts
STRENGTHENED = ROOT / "research_round8/strengthened/encode_strengthened.py"
STRENGTHENED_SHA = "8bc589363ffc4239e349a7dd4a5bf7a93a7d51ca1cb4a102b28189e2db414b4f"
if hashlib.sha256(STRENGTHENED.read_bytes()).hexdigest() != STRENGTHENED_SHA:
    raise ValueError("Frozen Round8 strengthened encoder changed")
spec = importlib.util.spec_from_file_location("r8_incidence_frozen_strengthened", STRENGTHENED)
X = importlib.util.module_from_spec(spec); spec.loader.exec_module(X)
B = X.B
load_spectra, load_M, all_subspaces, write_dimacs = X.load_spectra, X.load_M, X.all_subspaces, X.write_dimacs


def encode(T, maximum, spectra, table, subspaces, *, total=93, hub_min=None,
           enabled=True, tetrahedral=True, propagate=True):
    T = list(T)
    if len(T) != len(set(T)) or any(type(v) is not int or not 1 <= v < 32 for v in T):
        raise ValueError("T must contain distinct nonzero binary5 residues")
    support = [0] + T
    if not ((len(support) == 13 and maximum in (12, 13)) or
            (len(support) == 14 and maximum == 11)):
        raise ValueError("Supported scopes are S13/exact12 or13 and S14/exact11")
    if type(maximum) is not int or type(total) is not int or total != 93:
        raise ValueError("This convenience encoder fixes integer total budget93")
    if hub_min is not None and hub_min != maximum:
        raise ValueError("The distinguished hub must have the specified exact maximum")
    formula = B.encode(T, maximum, spectra, table, subspaces,
                       outtotal=93, hub_min=maximum, strengthen=False)
    before = formula.n, len(formula.cl)
    components = {}
    if enabled:
        components["tetrahedral"] = X.append_strengthening(
            formula, support, spectra, table, enabled=True, heavy=False,
            tetrahedral=bool(tetrahedral))
        components["incidence"] = append_next_frontier_cuts(
            formula, support, spectra, enabled=True, propagate=bool(propagate))
    metadata = {"enabled": bool(enabled), "support": support,
                "maximum_interval": [maximum, maximum], "total_upper_bound": 93,
                "distinguished_hub": 0, "tetrahedral_requested": bool(tetrahedral),
                "optional_pair_propagation_requested": bool(propagate),
                "components": components, "added_variables": formula.n-before[0],
                "added_clauses": len(formula.cl)-before[1],
                "disabled_baseline_identity": not enabled,
                "SAT_solver_called": False, "new_exclusions_claimed": 0}
    formula.r8_next_frontier_metadata = metadata
    return formula
