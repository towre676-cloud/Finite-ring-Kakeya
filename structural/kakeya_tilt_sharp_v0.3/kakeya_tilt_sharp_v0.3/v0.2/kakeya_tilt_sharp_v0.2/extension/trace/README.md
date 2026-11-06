# Higher-length Teichmüller trace extension

Read **TRACE_THEOREMS.md** for the proofs. The main results are the explicit
length-three law, the all-length diagonal-carry recursion, a complete criterion
and all-dimensional census for affine length-three traces, and the sharp first
occurrence of nonaffine mixed-characteristic traces.

## Reproduce

Python 3.10 or later; no packages to install.

```bash
python3 trace_law.py --profile standard --receipt trace_receipt.json
```

A shorter implementation check is available with `--profile quick`. The
standard receipt records which domains are exhaustive and which are sampled.
The mathematical proofs apply independently of those finite domains.

## Use the recurrence

```python
from trace_law import TraceEngine, affine_incidence_counts

mixed = TraceEngine(p=2, length=3)
flat = TraceEngine(p=2, length=3, flat=True)
# Equivalent canonical ring codes: TraceEngine.from_code("W2^3"), "T2^3".

# Digits are ordered from the residue digit upwards.
assert mixed.affine((0, 0, 0), (1, 1, 0), (1, 1, 0)) == (1, 0, 0)
assert flat.affine((0, 0, 0), (1, 1, 0), (1, 1, 0)) == (1, 0, 1)

# Vector inputs are coordinate-major. Output traces are layer-major.
x = ((0, 0, 0), (0, 0, 0))
v = ((1, 0, 0), (1, 1, 0))
trace = mixed.fibre_trace(x, v, sigma=1)
assert len(trace) == 4

# Proved all-dimensional formula at odd primes, length three.
assert affine_incidence_counts(3, 2) == {
    "total": 2916, "affine": 1944, "nonaffine": 972
}
```

`trace_law.py` does not import or modify the uploaded packages. The independent
oracle uses actual ring arithmetic and separately lifted Teichmüller roots.
