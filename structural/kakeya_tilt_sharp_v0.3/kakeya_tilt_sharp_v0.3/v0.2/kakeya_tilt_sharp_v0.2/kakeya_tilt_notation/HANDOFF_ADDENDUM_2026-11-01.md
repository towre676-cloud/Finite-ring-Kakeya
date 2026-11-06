# HANDOFF addendum, 1 November 2026: notation reform

This package is an overlay on the October `kakeya_package` zips. Unzip it beside them; it adds files and replaces only the monograph.

## What changed

The comparison notation is now fixed by NOTATION.md. The ring pair is written A_{p,l} = Z/p^l and A^flat_{p,l} = F_p[t]/(t^l), and the Kakeya number is kappa_n(R). The tilt defect Delta_n(p,l) = kappa_n(A_{p,l}) - kappa_n(A^flat_{p,l}) carries the comparison. Coordinates are Teichmueller digits, with one carry cocycle gamma (gamma = 0 on the flat side). New ring codes are W{p}^{l} and T{p}^{l}; legacy codes are accepted by tilt.ring().

## New certified content

N1. gamma(a,b) = (a^p + b^p - (a+b)^p)/p mod p, read off the ring tables at p = 2, 3, 5, 7.

N2. Fibre-trace law at length 2: the digit set over a + sigma*alpha is b + sigma*beta + gamma(a, sigma*alpha) + <alpha>. Exhaustive, 3,435,322 incidences per ring, no mismatch.

N3. The c_a(sigma) term of the October Proposition 3 is a coordinate artifact of integer slope representatives, namely the reparametrisation delta -> delta + e(a). It is not a carry. Verified at p = 3, 5, 7.

N4. Propositions 2 and 3 were rebuilt in Teichmueller coordinates and brute-force verified. Proposition 2 gives sizes 10, 22, 46, 94 for n = 2..5. Proposition 3 gives sizes 45, 350, 1323 for p = 3, 5, 7. Both hold in both rings.

kappa.py recomputes kappa_2 = 10, 34, 45 for the pairs (2,2), (2,3), (3,2) and writes Delta_2 = 0. These lower bounds are solver verdicts and are not re-certified. The DRUP certificates in cert_n3/ and sat/counting/ remain authoritative.

## Monograph changes

The monograph gains §0′ Notation, which contains Lemma 0 (the trace law) and the old-to-new table.

The ledger now has a Delta column.

Propositions 2 and 3 are re-proved via Lemma 0. A new Remark explains why c_a was never a carry.

The stale "kappa_4 = 46 untested" paragraph is marked settled, citing Theorem 5.

Throughout the monograph:
- k becomes kappa_n, l (length) or d (design dimension), depending on use.
- pi^{-1} becomes rho^{-1}.
- epsilon becomes pi.
- kappa(a, alpha) becomes gamma(a, alpha).
- The SAT line variable becomes y_{d,L}, and the transversal becomes L*.

## Open

The trace law at l >= 3, where the carry is the full Witt addition tower, is not yet written or checked. The length-3 statements keep their direct form until it is.

## Reproduce

    pip install python-sat
    python3 checks.py       # ~1 min, results/notation_checks.json
    python3 kappa.py        # ~45 s, results/kappa2.json
