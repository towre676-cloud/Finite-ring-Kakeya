# Kakeya v0.3 — The Full-Fibre Half

Open **Kakeya_Full_Fibre_Half_v0.3.html** (Part VI). It continues the v0.2
monograph *Kakeya — Spectral Realization and Carry Geometry* (Parts I–V),
which is preserved unchanged under `v0.2/` together with its verifier.

## Main results

- **Plane carry separation (proved, census-confirmed twice).** In
  F_2[ε]/(ε²) every Kakeya set in R² has a full residue fibre. In Z/4Z the
  full-fibre-free minimum is 12, attained by exactly 64 sets, and the
  separating mechanism is a single carry class in the direction (1,1).
- **k°(R,3) = 24 exactly** (no full fibre, both rings): solver-free
  exhaustive proof (12,415,924 nodes) plus the v0.2 128-member family. The
  extremal heavy support is unique up to AGL_3(F_2): 5 heavy fibres.
- **Full-fibre case of dimension four closed:** every Kakeya set in R⁴ with
  a full fibre has ≥ 46 points (two independent relaxations).
- **Theorem VI.4.2 (all n):** a full fibre and |U| ≤ N/4 imply |K| ≥ 3N − 2,
  with |K| − (3N − 2) ≥ √(N|U|) − 2|U|.
- **Energy inequality (all n):** Σ_a p_a(v)² ≥ N for every direction.
- **k(R,4) reduced to 21 heavy-support orbits** of AGL_4(F_2) (of 32);
  see the monograph table for which are closed.
- **Negative results:** point-level SAT and every additive per-fibre
  weighting certificate fail for the open cases (best support-aware supply
  165.6 against the required 120).

## Layout

| Path | Contents |
|---|---|
| `Kakeya_Full_Fibre_Half_v0.3.html` | Part VI monograph (house style, MathJax) |
| `kakeya_sharp/` | Package: v0.1 modules plus all v0.3 modules, receipts in `results/` |
| `v0.2/` | The v0.2 bundle, unchanged; `python v0.2/kakeya_tilt_sharp_v0.2/verify_release.py` passes |
| `MANIFEST.sha256` | SHA-256 of every file |

See `kakeya_sharp/README.md` for every reproduction command.
