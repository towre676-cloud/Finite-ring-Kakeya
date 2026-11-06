# kakeya_sharp (v0.3 module set)

Exact computation, relaxations and finite proofs for the sharp Kakeya law
k(R,n) = 3·2^n − 2 over R ∈ {Z/4Z, F_2[ε]/(ε²)}.

Requirements: Python ≥ 3.10; `ortools` and `python-sat` for the solver runs.
`stdlib_proof_n3.py`, `nofull_n2.py`, `nofull_n2_independent.py`,
`heavy_orbits.py` and `tests_basic.py` need only the standard library.

## v0.1 commands

    python3 tests_basic.py                         # K_* Kakeya for n ≤ 5; fibre identity ≡ line enumeration
    python3 -m kakeya_sharp.sat_decide 3 21        # UNSAT in both rings → k(R,3) ≥ 22
    python3 -m kakeya_sharp.relaxation 3 100       # defect relaxation (T): optimum 22
    python3 -m kakeya_sharp.profiles 3 22          # unique equality profile (8,2,…,2)
    python3 -m kakeya_sharp.equality_n2            # 32 extremal sets per ring at n = 2

## v0.3 commands

    python3 -m kakeya_sharp.nofull_n2              # plane, no full fibre: Z4 min 12 (64 sets); D2 none
    python3 -m kakeya_sharp.nofull_n2_independent  # same census with fresh tuple arithmetic
    python3 -m kakeya_sharp.stdlib_proof_n3 21 8   # solver-free proof k(R,3) ≥ 22
    python3 -m kakeya_sharp.stdlib_proof_n3 23 7   # solver-free proof: no full fibre ⇒ ≥ 24 at n = 3
    python3 -m kakeya_sharp.exact_local4 4 45 --full0 --seconds 800   # full-fibre case n = 4: INFEASIBLE
    python3 -m kakeya_sharp.heavy_orbits 4 45      # 32 AGL_4 orbits, 21 admissible heavy supports
    python3 -m kakeya_sharp.run_heavy_cases 4 45 200 all _sq          # model X on every heavy support
    python3 -m kakeya_sharp.dual_weights2 4 45     # best support-aware weighting certificate (fails: 165.6 > 120)
    python3 -m kakeya_sharp.theorem_A_check        # Theorem VI.4.2 chain against exact-type assignments

All verdicts are written to `results/` as JSON. The monograph source and its
builder are in `monograph/`.
