# kakeya_sharp v0.1

Exact computation and relaxation analysis for the sharp Kakeya law
k(R,n) = 3·2^n − 2 over R ∈ {Z/4Z, F_2[ε]/(ε²)}.

Requirements: Python ≥ 3.10, `ortools`, `python-sat`.

    python3 tests_basic.py                      # K_* is Kakeya (n ≤ 5), fibre identity ≡ line enumeration
    python3 -m kakeya_sharp.sat_decide 3 21     # UNSAT in both rings  → k(R,3) ≥ 22
    python3 -m kakeya_sharp.relaxation 3 100    # defect relaxation (T): optimum 22
    python3 -m kakeya_sharp.profiles 3 22       # unique equality profile (8,2,…,2)
    python3 -m kakeya_sharp.profiles 3 23 7     # no T-point ≤ 23 without a full fibre
    python3 -m kakeya_sharp.equality_n2         # census: 32 extremal sets per ring at n = 2
    python3 -m kakeya_sharp.relaxation 4 1400   # n = 4 relaxation (see results/)

All results are in `results/`; the monograph is `monograph/kakeya_sharp_law.html`.
