"""Exact missing-heavy-direction incidence cuts on explicit z/y maps.

Public entrypoints:
  add_incidence_budget(f,S,SPEC,enabled=True)
    General conditional theorem, gated by number of heavy fibres >=9.
  append_next_frontier_cuts(f,S,SPEC,enabled=True,propagate=True)
    S13/max<=13 or S14/max<=11 consequences and optional h10 propagation.

The base spectrum choices must be exactly one per fibre. Every new flag
is defined here by equivalence. No existing auxiliary numbering is used.
"""
from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _scope(formula, support, spectra):
    S = tuple(support)
    require(9 <= len(S) <= 32 and len(S) == len(set(S)) and
            all(type(v) is int and 0 <= v < 32 for v in S), "Expected distinct binary5 support residues, size9..32")
    require(set(v for v, _ in formula.z) == set(S), "Spectrum vertices differ from support")
    domains = {v: sorted(i for vv, i in formula.z if vv == v) for v in S}
    require(all(domains.values()), "Every fibre needs a nonempty exactly-one spectrum domain")
    weights = [spectra[i][0] for domain in domains.values() for i in domain]
    require(all(type(w) is int and 2 <= w <= 32 for w in weights), "Fibre domain must lie in weights2..32")
    upper = max(weights)
    P = upper//2
    return S, domains, upper, P, (16+P-1)//P


def _or(formula, literals, records):
    literals = list(literals); output = formula.new()
    formula.add([-output] + literals)
    for literal in literals:
        formula.add([-literal, output])
    records.append(("or", output, tuple(literals)))
    return output


def _and(formula, literals, records):
    literals = list(literals); output = formula.new()
    for literal in literals:
        formula.add([-output, literal])
    formula.add([output] + [-literal for literal in literals])
    records.append(("and", output, tuple(literals)))
    return output


def _counter(formula, literals, records):
    literals = list(literals)
    outputs = formula.unary_sum(literals)
    records.append(("counter", tuple(outputs), tuple(literals)))
    return outputs


def add_incidence_budget(formula, support, spectra, *, enabled=True):
    if not enabled:
        return {"enabled": False, "added_variables": 0, "added_clauses": 0}
    S, domains, upper, P, r = _scope(formula, support, spectra)
    before = formula.n, len(formula.cl)
    records = []
    heavy = {}; weight3 = {}; not3 = {}
    for v in S:
        heavy[v] = _or(formula, [formula.z[v, i] for i in domains[v] if spectra[i][0] >= 4], records)
        weight3[v] = _or(formula, [formula.z[v, i] for i in domains[v] if spectra[i][0] == 3], records)
        not3[v] = _or(formula, [-weight3[v]], records)
    edge_and = {}; direction_edges = {d: [] for d in range(1, 32)}
    for a, b in combinations(sorted(S), 2):
        edge_and[a, b] = _and(formula, [heavy[a], heavy[b]], records)
        direction_edges[a ^ b].append((a, b))
    covered = {}; missing = {}
    for d in range(1, 32):
        covered[d] = _or(formula, [edge_and[edge] for edge in direction_edges[d]], records)
        missing[d] = _or(formula, [-covered[d]], records)
    heavy_count = _counter(formula, [heavy[v] for v in S], records)
    missing_count = _counter(formula, [missing[d] for d in range(1, 32)], records)
    weighted = [missing[d] for d in range(1, 32) for _ in range(r)] + [heavy[v] for v in S] + [not3[v] for v in S]
    budget_count = _counter(formula, weighted, records)
    # Exact theorem premise: at least nine heavy vertices. All auxiliaries
    # remain ordinary equivalences when this semantic inequality is inactive.
    if 2*len(S) < len(budget_count):
        formula.add([-heavy_count[8], -budget_count[2*len(S)]])
    metadata = {"enabled": True, "theorem": "MISSING_HEAVY_DIRECTIONS_LIGHT_INCIDENCE",
                "support_size": len(S), "maximum_domain_weight": upper,
                "maximum_pair_count": P, "required_light_incidence_per_missing_direction": r,
                "minimum_heavy_premise": 9, "budget_rhs": 2*len(S),
                "budget_terms": "r*missing_count+heavy_count+not_weight3_count",
                "total_weight_assumption": None, "all_flags_exact": True,
                "added_variables": formula.n-before[0], "added_clauses": len(formula.cl)-before[1]}
    formula.r8_incidence = {"support": S, "domains": domains, "heavy": heavy, "weight3": weight3,
                            "not_weight3": not3, "heavy_edge_AND": edge_and,
                            "direction_edges": direction_edges, "covered": covered, "missing": missing,
                            "heavy_count_outputs": heavy_count, "missing_count_outputs": missing_count,
                            "budget_count_outputs": budget_count, "construction_records": records,
                            "metadata": metadata}
    return metadata


def append_next_frontier_cuts(formula, support, spectra, *, enabled=True, propagate=True):
    if not enabled:
        return {"enabled": False, "added_variables": 0, "added_clauses": 0}
    S, domains, upper, P, r = _scope(formula, support, spectra)
    s = len(S)
    require((s == 13 and upper <= 13) or (s == 14 and upper <= 11),
            "Next-frontier consequences require S13/max<=13 or S14/max<=11")
    propagation_applies = bool(propagate and s-10 == r)
    if propagation_applies:
        for a, b in combinations(S, 2):
            d = a ^ b
            require((a, d, 1) in formula.y and (b, d, 1) in formula.y,
                    "Directional propagation requires the explicit pair-count1 selectors")
    before = formula.n, len(formula.cl)
    budget_metadata = add_incidence_budget(formula, S, spectra)
    data = formula.r8_incidence
    hc, mc = data["heavy_count_outputs"], data["missing_count_outputs"]
    formula.add([hc[9]])
    formula.add([-mc[2]])
    full_cover_threshold = s-r+1
    for d in range(1, 32):
        if full_cover_threshold <= 0:
            formula.add([-data["missing"][d]])
        else:
            formula.add([-hc[full_cover_threshold-1], -data["missing"][d]])
    propagation_clauses = 0
    pair_lower = None
    if propagation_applies:
        eq10 = _and(formula, [hc[9], -hc[10]], data["construction_records"])
        data["exactly_ten_heavy"] = eq10
        pair_lower = 16-P*(r-1)
        require(1 <= pair_lower <= P, "Incorrect residual heavy pair bound")
        Sset = set(S)
        for d in range(1, 32):
            for a in S:
                gate = [-eq10, -data["missing"][d], data["heavy"][a]]
                b = a ^ d
                if b not in Sset:
                    formula.add(gate); propagation_clauses += 1
                    continue
                formula.add(gate + [data["heavy"][b]])
                formula.add(gate + [formula.y[a, d, 1]])
                partner = [literal for (v, dd, p), literal in formula.y.items()
                           if v == b and dd == d and p >= pair_lower]
                formula.add(gate + partner)
                propagation_clauses += 3
        for a in S:
            formula.add([-eq10, -mc[1], data["heavy"][a], data["weight3"][a]])
            propagation_clauses += 1
    metadata = {"enabled": True, "theorem": "NEXT_FRONTIER_MISSING_DIRECTION_INCIDENCE",
                "support_size": s, "maximum_domain_weight": upper,
                "minimum_heavy": 10, "minimum_heavy_differences": 29,
                "heavy_count_for_full_cover": max(0, full_cover_threshold),
                "budget": budget_metadata, "propagation_requested": bool(propagate),
                "propagation_applies": propagation_applies,
                "missing_direction_heavy_partner_pair_lower_bound": pair_lower,
                "optional_propagation_clauses": propagation_clauses,
                "added_variables": formula.n-before[0], "added_clauses": len(formula.cl)-before[1],
                "new_SAT_exclusions_claimed": 0}
    data["next_frontier_metadata"] = metadata
    return metadata
