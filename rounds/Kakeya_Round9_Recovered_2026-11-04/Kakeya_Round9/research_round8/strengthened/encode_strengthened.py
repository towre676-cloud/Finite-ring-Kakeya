"""Explicit heavy-fibre and all-edge tetrahedral cuts on the frozen baseline.

All new capacity variables are created here and exposed by named maps.
No baseline auxiliary variable numbers or clause positions are inferred.
The baseline's spectrum and directional pair-count maps are its public API.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research_round6/joint_maxima/encode_joint_maxima.py"
BASE_SHA256 = "776af5c5699f5e153990cdfb8b0897d690202c9895dd95134eec9b8df295feba"
EXPOSED_BASE = ROOT / "research_round6/encoder_audit/encode_maximal_cosets.py"
EXPOSED_BASE_SHA256 = "7e3225d4b5d0ff50d4578fc7d1d4a924d122449ce4e87f00520bac0ee0016102"
if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA256:
    raise ValueError("Frozen baseline source changed")
if hashlib.sha256(EXPOSED_BASE.read_bytes()).hexdigest() != EXPOSED_BASE_SHA256:
    raise ValueError("Frozen selector-export baseline changed")
spec = importlib.util.spec_from_file_location("round8_frozen_joint_baseline", BASE)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
spec = importlib.util.spec_from_file_location("round8_frozen_selector_exports", EXPOSED_BASE)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
load_spectra, load_M = E.load_spectra, E.load_M
all_subspaces, write_dimacs = E.all_subspaces, E.write_dimacs


def require(condition, message):
    if not condition:
        raise ValueError(message)


def disjunction(formula, choices):
    """Return a fresh indicator equivalent to the OR, including empty OR."""
    choices = list(choices)
    indicator = formula.new()
    formula.add([-indicator] + choices)
    for choice in choices:
        formula.add([-choice, indicator])
    return indicator


def nonplanar_four_pair_type(spectrum):
    """Sufficient type flag only; affine-rank intervals must be exactly four."""
    weight, histogram, rank_min, rank_max = spectrum
    if (rank_min, rank_max) != (4, 4):
        return False
    energy = sum(p*p*count for p, count in enumerate(histogram))
    return ((weight == 8 and energy == 64 and histogram[4] == 1)
            or (weight == 11 and energy == 205))


def add_heavy_cardinality(formula, support, spectra):
    """Nine heavy fibres for maximum<=13, eight for maximum<=18."""
    support = list(support)
    require(len(support) == len(set(support)) == 13,
            "The heavy-cardinality theorem requires thirteen distinct vertices")
    domains = {v: sorted(i for vv, i in formula.z if vv == v) for v in support}
    require(all(domains.values()), "Empty spectrum domain")
    weights = [spectra[i][0] for indices in domains.values() for i in indices]
    require(all(2 <= w <= 18 for w in weights), "Heavy theorem domain is weights2..18")
    upper = max(weights)
    minimum_heavy = 9 if upper <= 13 else 8
    before = formula.n, len(formula.cl)
    formula.r8_heavy = {
        v: disjunction(formula, [formula.z[v, i] for i in domains[v] if spectra[i][0] >= 4])
        for v in support
    }
    outputs = formula.unary_sum([formula.r8_heavy[v] for v in support])
    formula.add([outputs[minimum_heavy - 1]])
    return {"required_heavy_vertices": minimum_heavy, "heavy_threshold": 4,
            "largest_domain_weight": upper,
            "added_variables": formula.n - before[0],
            "added_clauses": len(formula.cl) - before[1]}


def add_edge_capacity(formula, a, b, direction, table, type_a, type_b):
    """Create a fresh unary upper capacity for one edge.

    bits[j] means capacity>=j+1, for j=0..15.  The caller may sum these
    bits as independent contributions to the same direction's upper bound.
    Conditional bounds use only explicitly passed, named input literals.
    """
    require(a < b and a ^ b == direction, "Invalid ordered binary residue edge")
    left = sorted(p for v, d, p in formula.y if (v, d) == (a, direction))
    right = sorted(q for v, d, q in formula.y if (v, d) == (b, direction))
    require(left and right, "Missing directional pair-count selectors")
    bits = [formula.new() for _ in range(16)]
    for j in range(15):
        formula.add([-bits[j + 1], bits[j]])
    for p in left:
        for q in right:
            cap = table[p][q]
            require(type(cap) is int and 0 <= cap <= min(16, p*q),
                    "Invalid inherited sumset-capacity entry")
            if cap < 16:
                formula.add([-bits[cap], -formula.y[a, direction, p], -formula.y[b, direction, q]])
    if 4 in left and 4 in right:
        formula.add([-bits[14], -type_a, -type_b,
                     -formula.y[a, direction, 4], -formula.y[b, direction, 4]])
    return bits


def add_all_edge_tetrahedral_capacities(formula, support, spectra, table):
    """A second transparent capacity upper bound for all31 directions."""
    support = sorted(support)
    require(len(support) == len(set(support)) and all(0 <= v < 32 for v in support),
            "Support must be a set of binary5 residues")
    before = formula.n, len(formula.cl)
    eligible = [i for i, spectrum in enumerate(spectra) if nonplanar_four_pair_type(spectrum)]
    formula.r8_tetra_type = {
        v: disjunction(formula, [formula.z[v, i] for i in eligible if (v, i) in formula.z])
        for v in support
    }
    formula.r8_edge_capacity = {}
    formula.r8_direction_edges = {d: [] for d in range(1, 32)}
    for a, b in itertools.combinations(support, 2):
        d = a ^ b
        formula.r8_edge_capacity[a, b] = add_edge_capacity(
            formula, a, b, d, table, formula.r8_tetra_type[a], formula.r8_tetra_type[b])
        formula.r8_direction_edges[d].append((a, b))
    for d, edges in formula.r8_direction_edges.items():
        outputs = formula.unary_sum([literal for edge in edges for literal in formula.r8_edge_capacity[edge]])
        formula.add([outputs[15]] if len(outputs) >= 16 else [])
    gated_edges = sum((a, a ^ b, 4) in formula.y and (b, a ^ b, 4) in formula.y
                      for a, b in formula.r8_edge_capacity)
    return {"eligible_spectrum_indices": eligible, "edge_count": len(formula.r8_edge_capacity),
            "direction_count": 31, "conditional_tetrahedral_edges": gated_edges,
            "new_capacity_bits": 16*len(formula.r8_edge_capacity),
            "capacity_semantics": "bits[j] means capacity>=j+1; explicit new edge variables",
            "added_variables": formula.n - before[0],
            "added_clauses": len(formula.cl) - before[1]}


def append_strengthening(formula, support, spectra, table, *, enabled=True,
                         heavy=True, tetrahedral=True):
    """Append reviewed cuts and expose r8_heavy/r8_edge_capacity maps."""
    before = formula.n, len(formula.cl)
    formula.r8_heavy = {}
    formula.r8_tetra_type = {}
    formula.r8_edge_capacity = {}
    formula.r8_direction_edges = {}
    metadata = {"enabled": bool(enabled), "heavy_requested": bool(heavy),
                "tetrahedral_requested": bool(tetrahedral), "components": {}}
    if enabled:
        if heavy:
            metadata["components"]["heavy"] = add_heavy_cardinality(formula, support, spectra)
        if tetrahedral:
            metadata["components"]["tetrahedral"] = add_all_edge_tetrahedral_capacities(
                formula, support, spectra, table)
    metadata.update(added_variables=formula.n - before[0], added_clauses=len(formula.cl) - before[1])
    formula.r8_strengthened_metadata = metadata
    return metadata


def encode(T, maximum, spectra, table, subspaces, *, total=93, hub_min=11,
           enabled=True, heavy=True, tetrahedral=True):
    # This audited export variant is byte-identical to E when strengthen=False.
    # It exposes H/K selector maps without adding a single constraint.
    formula = B.encode(T, maximum, spectra, table, subspaces,
                       outtotal=total, hub_min=hub_min, strengthen=False)
    append_strengthening(formula, [0] + list(T), spectra, table,
                         enabled=enabled, heavy=heavy, tetrahedral=tetrahedral)
    return formula
