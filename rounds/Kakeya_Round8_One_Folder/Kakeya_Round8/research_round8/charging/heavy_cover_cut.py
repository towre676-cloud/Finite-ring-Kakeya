"""Append the census-free support13 / maximum<=11 heavy-cover theorem.

Interface: f.new/add/unary_sum, f.z[(residue,spectrum_index)] and
f.r8_heavy[residue]. The spectrum domain is exactly-one in the base CNF.
Heavy flags are defined again by equivalence here, so this component does
not rely on an uninspected external flag definition. No old file is edited.
"""
from itertools import combinations


def add_heavy_cover_cut(f, support, spectra):
    support = tuple(support)
    if len(support) != 13 or len(set(support)) != 13 or any(type(v) is not int or not 0 <= v < 32 for v in support):
        raise ValueError("Heavy-cover theorem requires thirteen distinct residues in F2^5")
    if set(v for v, _ in f.z) != set(support):
        raise ValueError("Spectrum vertices differ from the declared support")
    domains = {v: [i for vv, i in f.z if vv == v] for v in support}
    if any(not domain for domain in domains.values()):
        raise ValueError("Every fibre needs a nonempty exactly-one spectrum domain")
    if any(not 2 <= spectra[i][0] <= 11 for domain in domains.values() for i in domain):
        raise ValueError("Heavy-cover theorem requires all fibre weights in [2,11]")
    heavy = f.r8_heavy
    if set(heavy) != set(support) or len(set(heavy.values())) != len(support):
        raise ValueError("Expected one distinct heavy indicator per support vertex")
    if any(type(x) is not int or not 1 <= x <= f.n for x in heavy.values()):
        raise ValueError("Invalid existing heavy-indicator variable")
    before = f.n, len(f.cl)
    for v in support:
        choices = [f.z[v, i] for i in domains[v] if spectra[i][0] >= 4]
        f.add([-heavy[v]] + choices)
        for choice in choices:
            f.add([-choice, heavy[v]])
    outputs = f.unary_sum([heavy[v] for v in support])
    f.add([outputs[9]])
    edge_vars = {}
    direction_edges = {d: [] for d in range(1, 32)}
    for a, b in combinations(sorted(support), 2):
        edge = f.new()
        f.add([-edge, heavy[a]])
        f.add([-edge, heavy[b]])
        f.add([edge, -heavy[a], -heavy[b]])
        edge_vars[a, b] = edge
        direction_edges[a ^ b].append((a, b))
    for d in range(1, 32):
        f.add([edge_vars[edge] for edge in direction_edges[d]])
    f.r8_heavy_cover_edge_ands = edge_vars
    f.r8_heavy_cover_direction_edges = direction_edges
    f.r8_heavy_cover_count_outputs = outputs
    metadata = {"theorem": "SUPPORT13_MAXIMUM_LE11_REQUIRES_TEN_HEAVY_AND_FULL_HEAVY_DIFFERENCE_COVER",
                "support_size": 13, "maximum_domain_weight": max(spectra[i][0] for domain in domains.values() for i in domain),
                "heavy_threshold": 4, "minimum_heavy": 10,
                "required_heavy_directions": 31, "total_weight_assumption": None,
                "new_variables": f.n - before[0], "new_clauses": len(f.cl) - before[1],
                "all_auxiliary_edges_are_exact_ANDs": True,
                "heavy_flags_redefined_by_equivalence": True}
    f.r8_heavy_cover_metadata = metadata
    return metadata
