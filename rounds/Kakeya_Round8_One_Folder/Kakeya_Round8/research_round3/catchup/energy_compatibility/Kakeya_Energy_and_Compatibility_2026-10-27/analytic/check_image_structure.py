"""Finite controls for structural all-dimension theorems (n=2)."""
from itertools import product, combinations
from collections import Counter
from pathlib import Path
import json
from check_three_images import operations


def subgroup(A, add):
    return 0 in A and all(add(a,b) in A for a in A for b in A)


def image_sets(f, add, pi, unit):
    return [set(f), {add(y,v) for v,y in enumerate(f)},
            {add(y,pi(v)) for v,y in enumerate(f)},
            {add(y,unit(v)) for v,y in enumerate(f)}]


def all_additive(ring):
    add, sub, pi, unit = operations(2, ring)
    count = 0
    minimum = 16
    histogram = Counter()
    minimum_unbalanced = 16
    if ring == "dual":
        column_tuples = product(range(16), repeat=4)
        def evaluate(cols):
            f = [0]*16
            for v in range(1,16):
                bit = v & -v
                f[v] = f[v ^ bit] ^ cols[bit.bit_length()-1]
            return f
    else:
        column_tuples = product(range(16), repeat=2)
        def evaluate(cols):
            f = []
            multiples = [[0,c,pi(c),unit(c)] for c in cols]
            for v in range(16):
                d0 = (v&1) + 2*((v>>2)&1)
                d1 = ((v>>1)&1) + 2*((v>>3)&1)
                f.append(add(multiples[0][d0],multiples[1][d1]))
            return f
    for cols in column_tuples:
        f = evaluate(cols)
        imgs = image_sets(f,add,pi,unit)
        assert all(subgroup(A,add) for A in imgs)
        w = len(set.union(*imgs))
        assert w >= 10
        count += 1
        minimum = min(minimum,w)
        sizes = tuple(len(A) for A in imgs)
        histogram[sizes] += 1
        if sizes != (4,4,4,4):
            minimum_unbalanced = min(minimum_unbalanced,w)
    return {"ring":ring, "all_additive_maps":count, "minimum_union":minimum,
            "minimum_union_unbalanced":minimum_unbalanced,
            "image_size_histogram":[{"sizes":k,"count":v} for k,v in sorted(histogram.items())]}


def all_balanced_pair_tilings(ring):
    add,sub,pi,unit = operations(2,ring)
    sets = [set((0,)+tail) for tail in combinations(range(1,16),3)]
    diffs = [{sub(a,b) for a in A for b in A}-{0} for A in sets]
    subflags = [subgroup(A,add) for A in sets]
    count = coset_count = neither_count = 0
    minimum_coset = minimum_neither = 16
    minimum_by_CD = {}
    for i,A in enumerate(sets):
        for j,B in enumerate(sets):
            if diffs[i] & diffs[j]:
                continue
            count += 1
            C = {add(unit(a),pi(b)) for a in A for b in B}
            D = {add(unit(b),pi(a)) for a in A for b in B}
            w = len(A|B|C|D)
            key = (len(C),len(D))
            minimum_by_CD[key] = min(minimum_by_CD.get(key,16),w)
            if subflags[i] or subflags[j]:
                coset_count += 1
                minimum_coset = min(minimum_coset,w)
                assert w >= 10
            else:
                neither_count += 1
                minimum_neither = min(minimum_neither,w)
    return {"ring":ring, "all_normalized_balanced_pair_tilings":count,
            "at_least_one_subgroup":coset_count,"minimum_union_one_subgroup":minimum_coset,
            "neither_subgroup":neither_count,
            "minimum_union_neither_subgroup":minimum_neither if neither_count else None,
            "minimum_union_by_other_image_sizes":[{"sizes":k,"min_union":v}
                                                  for k,v in sorted(minimum_by_CD.items())]}


if __name__ == "__main__":
    report = {"scope":"All n=2 additive maps and normalized balanced-pair tilings; finite controls only",
              "additive_maps":[all_additive(r) for r in ["dual","z4"]],
              "balanced_pair_tilings":[all_balanced_pair_tilings(r) for r in ["dual","z4"]]}
    dest=Path(__file__).with_name("IMAGE_STRUCTURE_SMALL_CHECKS.json")
    dest.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"report":str(dest),"additive":[{k:v for k,v in x.items() if k!='image_size_histogram'}
        for x in report['additive_maps']], "tilings":[{k:v for k,v in x.items() if k!='minimum_union_by_other_image_sizes'}
        for x in report['balanced_pair_tilings']]},indent=2))
