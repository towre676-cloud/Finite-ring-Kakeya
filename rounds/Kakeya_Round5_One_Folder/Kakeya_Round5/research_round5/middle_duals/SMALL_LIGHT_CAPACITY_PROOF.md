# A capacity theorem for two- and three-point light fibres

## The elementary theorem

Let H be nine pair-active residue vertices in F2^5, with fibre pair caps
c_h=floor(w_h/2). Let F be the nonzero directions missing from H+H, and
r=|F|. Then r>=3 and F is sum-free. Suppose every other pair-active fibre
has weight2 or3, and put

    L=sum_light(w_i-1).

For every real b>=1/2, write

    Delta(b)=sum_(h in H) max(0,c_h-b).

The actual sumset capacities in the missing directions obey

    C_F <= b*L+r*Delta(b).                                (1)

Consequently a profile is impossible whenever

    b*L+3*Delta(b)<48.                                    (2)

These statements hold for both target rings and every placement and shape
of the specified fibres. They use neither a spectrum census nor an optimizer.

## Proof

A two-point fibre supplies at mostone pair unit in F. A three-point fibre
has three pair directions, and those directions are d,e,d+e. Since F is
sum-free, it contains at mosttwo of them. Thus the total light pair mass
in F is at most L. Each individual light pair count is0 or1.

Every edge in a missing heavy direction has a light endpoint. For a
light-light edge, its capacity is at most p*q, with p,q in{0,1}. Since
b>=1/2, p*q<=b*(p+q). Charge this to its two light endpoint pair units.

For a light-heavy edge meeting heavy h, its capacity is at most c_h*p,
where p in{0,1} is the light pair count. One has

    c_h*p <= b*p+max(0,c_h-b).

Charge b*p to the light budget. At each fixed heavy residue h, at mostone
incident residue edge occurs in each direction of F, so at most r excess
terms are needed there. Summing gives(1).

Kakeya coverage requires C_F>=16r. Condition(2) implies Delta(b)<16, because
bL is nonnegative. Therefore, for every r>=3,

    bL+r*Delta(b)-16r
      =[bL+3*Delta(b)-48]+(r-3)[Delta(b)-16]<0.

This contradicts coverage and proves the exclusion.

The ring carry translates each single-edge label set. Its cardinality does
not change, so the capacity upper bounds above apply to both rings.

## Exact optimization of this scalar theorem

The function

    f(b)=bL+3*sum_h(c_h-b)_+

is convex and piecewise linear on b>=1/2, with breakpoints among the heavy
caps c_h. Since L>0 in this application, f(b) grows for sufficiently large b.
Its minimum is attained at b=1/2 or one of the finitely many cap values.
Thus checking those breakpoints is exhaustive for theorem(2), including
arbitrary real choices of b. All current witnesses have integer b.

This also explains the multi-price duals. Taking

    t_h=2(c_h-b)_+

gives total doubled excess price2Delta(b), and the simple local upper for
a light fibre is2b*(w_i-1). Conditions(1) and(2) are exactly the resulting
aggregate price certificate. Discovery initially allowed independent prices
on all nine heavies; every accepted new cut simplifies to this single b.

## A concrete new exclusion

The profile

    (17,10,8^4,6^3,2^8)

has heavy caps(8,5,4^4,3^3), L=8, and Delta(4)=4+1=5. Therefore

    C_F<=4*8+5r=32+5r<16r       for every r>=3.

At r=3 the strict bound is47<48. In doubled price form, t=(8,2,0,...,0)
gives94<96. The profile has total93 and was a genuine survivor of the
specified Round4 screens; this proof covers all its placements and shapes.

## The complete finite consequence at this checkpoint

The previous list has275,755 weight profiles. Of those,2,467 have every
light weight in{2,3} after selecting their nine largest fibres as heavy.
An independent closed-form scan of every one of these profiles finds
exactly240 exclusions by theorem(2).

This set is identical to all240 new exclusions discovered by the complete
multi-price pass over186,779 support13..17 profiles. Each was already checked
by an independent backward local DP at its exact rational prices. Thus the
accepted exclusions have three concrete derivations:

1. A forward local active-pattern LP discovery, with rational prices.
2. A separate exact backward-DP certificate replay, with no LP dependency.
3. This elementary capacity theorem and exhaustive breakpoint calculation,
   with no LP, local DP, or spectrum-census dependency for the profile proofs.

The priced-family residual is275,515 profiles. No additional support/maximum
cell closes; the same55 cells remain nonempty. The stronger geometry family
being developed separately has its own cutset; the final ledger must take
the exact union rather than add counts without checking overlap.

The proof of these240 profile contradictions is analytic. The completeness
of the earlier inventory and its earlier exclusions remains a separate
inherited input. This is not external human review or a formal proof in Lean.

## Dimension-dependent general form

The same argument works in dimension n with demand D=2^(n-1) per nonzero
residue direction. If a selected heavy set has a sum-free missing set F and
at least r0>0 missing directions, with all light weights2 or3, then

    C_F<=bL+|F|*Delta(b).

A strict inequality bL+r0*Delta(b)<D*r0 excludes the configuration. The
nine-heavy theorem above uses D=16 and r0=3. This general form still requires
the stated missing-direction hypotheses; it does not prove the unrestricted
dimension-n Kakeya lower bound.

## Replay

From the archive root:

    python3 research_round5/middle_duals/verify_small_light_analytic.py

The script checks the entire previous survivor list, writes one integer
breakpoint certificate per exclusion, and compares its cutset exactly with
the independently verified multi-price set. The authoritative outputs are
SMALL_LIGHT_ANALYTIC_REPLAY.json and SMALL_LIGHT_ANALYTIC_CERTIFICATES.jsonl.
