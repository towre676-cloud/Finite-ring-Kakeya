"""One-clause consequence of the elementary ten-heavy exclusion.

Call only after add_heavy_cover_cut, on a formula whose actual weight
budget is the explicitly supplied total_upper_bound <=93. The existing
counter is exact; no new auxiliary variable or untrusted optimizer output
is used. The theorem's support classification is replayed separately.
"""


def add_eleven_heavy_cut(formula, *, total_upper_bound):
    if type(total_upper_bound) is not int or not 26 <= total_upper_bound <= 93:
        raise ValueError("Ten-heavy exclusion requires the formula's actual total budget to be at most93")
    metadata = getattr(formula, "r8_heavy_cover_metadata", {})
    if metadata.get("theorem") != "SUPPORT13_MAXIMUM_LE11_REQUIRES_TEN_HEAVY_AND_FULL_HEAVY_DIFFERENCE_COVER":
        raise ValueError("The validated heavy-cover component must precede this cut")
    if metadata.get("support_size") != 13 or not 2 <= metadata.get("maximum_domain_weight", 99) <= 11:
        raise ValueError("Wrong support or fibre-weight domain")
    outputs = getattr(formula, "r8_heavy_cover_count_outputs", ())
    if len(outputs) != 13 or any(type(x) is not int or not 1 <= x <= formula.n for x in outputs):
        raise ValueError("Missing exact thirteen-input heavy counter")
    formula.add([outputs[10]])
    result = {"theorem": "SUPPORT13_MAXIMUM_LE11_TOTAL_LE93_REQUIRES_ELEVEN_HEAVY",
              "support_size": 13, "maximum_domain_weight": metadata["maximum_domain_weight"],
              "total_upper_bound": total_upper_bound, "minimum_heavy": 11,
              "added_variables": 0, "added_clauses": 1,
              "required_existing_counter": "r8_heavy_cover_count_outputs",
              "fibre_spectrum_census_premise": False,
              "finite_support_normalization_cases": 14950}
    formula.r8_eleven_heavy_metadata = result
    return result
