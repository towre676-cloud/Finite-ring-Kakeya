# Shared own periods and common periodic/nonperiodic branches

## Scope

This stage starts after the17,604 common-rank exclusions and the one analytic deleted-direction exclusion. Its disjoint inputs contain9,828 support11 and3,038 support12 profiles, total12,866. Every claimed exclusion is of a whole weight/own-direction profile, uniformly over every residue placement and every fibre shape, for both rings.

## 1. Shared quotient periods reduce actual sumset capacity

An even-size fibre A_a is called own-periodic when A_a+a=A_a. This is equivalent to p_Aa(a)=|A_a|/2. For an offhub edge d=a+b, a is nonzero modulo<d>, since a,b are distinct nonzero residues. Translating an internal d-pair by a preserves the pair, so its quotient label set P_a(d) is invariant under a mod<d>. Thus its size p_Aa(d) is even.

If A_b is also own-periodic, P_b(d) has period b mod<d>, which equals a mod<d>. Both pair-label sets are therefore unions of cosets of the same two-point subgroup. Passing to that quotient gives

    |P_a(d)+P_b(d)+carry| <= p_Aa(d)*p_Ab(d)/2.

This is a bound on the actual quotient sumset, not on the original product cap. Consequently periodic-periodic edges use

    C(p,q)=min(M(p,q),p*q/2),

and all other edges retain M. For an own-periodic weight-w fibre the off-own pair cap is2*floor(w/4), because those pair counts are even and at most floor(w/2).

## 2. Exhaustive common modes

For every positive-own even fibre of weight at least4, branch into own-periodic modeP or own-nonperiodic modeN. Positive-own weight2 is forced intoP. Odd positive-own fibres and own-zero fibres are unbranched.

In a full-spectrum matching, the reserved own slot is constrained as follows:

    own-zero: p=0;
    periodic modeP: p=w/2;
    nonperiodic modeN: 1<=p<w/2;
    unbranched odd positive: p>=1.

The other selected directions use distinct entries of the same full spectrum. A modeP spectrum has only even counts outside its reserved own entry. The same mode is used for every incidence of the fibre, so the product-half cap applies simultaneously to all periodic-periodic pairs.

As before, identical weight/flag fibres are interchangeable in these label-free bounds. For each even weight4,6,...,18, enumerate every possible number assignedP. The full Cartesian set of those count choices covers every actual periodic-mode assignment.

## 3. Exact periodic block catalogue

If A is invariant under own direction a, it is the preimage of a subset B of V/<a>=F2^4, with |B|=w/2. For a nonzero quotient direction dbar,

    p_A(d)=p_A(d+a)=2*p_B(dbar).

Its fifteen paired-block maxima are therefore twice the fifteen pair counts of B. Enumerating every subset of F2^4 of cardinality1 through9 gives a complete periodic block catalogue, with no affine-orbit-classification dependency. The catalogue has1,1,1,2,2,3,3,4,3 histograms for original weights2,4,6,8,10,12,14,16,18 respectively.

For nonperiodic and unbranched fibres, the outside-support channel deliberately retains the broader frozen block catalogue selected only by the own flag. It is an upper-bound relaxation; no exact nonperiodic block-classification claim is made.

## 4. Full-hub and outside-support resource bounds

Both channels use the same established heavy/light resource proof, with periodic-sensitive edge caps and the mode-restricted local matchings. Heavy versus light is determined by the off-own cap:2*floor(w/4) for modeP and floor(w/2) otherwise. Only off-own edges appear in the light-light estimate, so a periodic own count larger than that off-own cap causes no problem.

The hub remains heavy for cutoffs0 through8. An outer hub-edge baseline uses the upper bound for its own count:0 for own-zero, w/2 forP, w/2-1 forN, or floor(w/2) for odd positive fibres. The hub endpoint matches those own-count caps to its exact19-point spectrum. The full-graph doubled demand is992.

The outside-support channel uses the paired-block catalogues, max(0,2*C(h,q)-ell*h) slot scores, and doubled demand32*(32-|S|). No rank3 subgroup correction is applied in this periodic stage: own-periodic fibres need not have affine rank3.

Each channel combines incident heavy deficits using max(max L_i,ceil(sum L_i/2)). Every local matching is certified by integer dual inequalities. A whole profile is excluded only after every periodic-count branch is certified below the appropriate channel demand.

## Stage accounting

The producer found231 candidate additional whole-profile exclusions:95 on support11 and136 on support12. These leave9,733 and2,902 profiles respectively, total12,635, conditional on the exact companion replay and root audit accepting all certificates.
