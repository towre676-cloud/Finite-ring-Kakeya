# Round 5: independently checkable SAT exclusions

## What has actually been checked

**The checking route is operational. The 38 new Claude maximum-19 certificates have not been supplied to this session and have not been checked here.** The user reports their existence at `/home/user/kakeya_round4/results/m19_s11_12.jsonl`; that path is unavailable in this workspace. Its JSONL field names and the precise conditions (A)–(E) are unknown here.

This package rebuilt pinned upstream tools and successfully checked four earlier Kakeya CNF/DRAT pairs from the available archive. It also exercised a genuine RAT inference, then rejected eight invalid-proof or coverage controls at the required acceptance gates. `PROOF_AUDIT_REPLAY.json` records these outcomes. The four archived cases are:

| Archived case | Required result |
|---|---|
| `n2_three_fibres_dual` | CakeML acceptance of the converted LRAT proof |
| `n5_forced_overlap_dual` | CakeML acceptance of the converted LRAT proof |
| `n5_forced_overlap_z4` | CakeML acceptance of the converted LRAT proof |
| `n5_four12_block_dual` | CakeML acceptance of the converted LRAT proof |

They are small fixed-shape fixtures. Their success establishes that this checker integration works on available certificates; it does not establish the new maximum-19 exclusion, a runtime bound for large certificates, or a complete Kakeya theorem.

## The acceptance path

For each declared case, `audit_certificates.py` does the following:

1. Check the exact CNF and original DRAT bytes against their declared SHA256 hashes. Check the DIMACS header, literal bounds, clause count, and termination without rewriting the formula.
2. Run the pinned upstream `drat-trim` on that formula and proof, asking it to emit LRAT using `-L`. Require successful termination and its exact success marker.
3. Run the pinned upstream CakeML `cake_lpr` artifact on **the same CNF** and the converted LRAT file. Require successful termination, stdout consisting of `s VERIFIED UNSAT`, and empty stderr. The return code alone is insufficient: this checker can report a checking failure on stderr while returning zero.
4. Recheck input and converted-proof hashes, preserve checker logs, and record the result in an incremental receipt. A timeout, resource failure, bad hash, incomplete inventory, or missing success marker is a failure to certify.

**CakeML acceptance is mandatory.** A solver status, Claude's checker status, DRAT-trim's status, or the optional ordinary C LRAT checker's status cannot replace it. Once a sound final checker accepts the LRAT certificate against the original CNF, the solver and DRAT-to-LRAT converter need not themselves be trusted for the formula's unsatisfiability. This is the standard certified-checking arrangement described by the original LRAT paper.[1]

The top-level success status is `PASS_ALL_DECLARED_CNF_CERTIFICATES`. It means exactly that all declared formulas have passed the acceptance path and the declared inventory is exactly covered. It does not certify the mathematical meaning of those formulas.

## A negative control found a real limitation of the ordinary C utility

At DRAT-trim commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, the bundled ordinary `lrat-check.c` utility accepts the following bogus certificate when invoked by its documented command `lrat-check FILE.cnf FILE.lrat`.

CNF:

```text
p cnf 1 1
1 0
```

Purported LRAT proof:

```text
2 0 0
```

The formula is satisfied by `x1 = true`. The proof line attempts to add the empty clause with no propagation hints. The C utility returns zero and prints `c VERIFIED`. The source takes its no-conflict, no-RAT-hints path with a zero pivot. The LRAT checking algorithm in the primary paper explicitly requires rejection if there is no propagated contradiction and the clause has no pivot.[1, Section 4]

**CakeML rejects this input**, reporting `pivot must be non-zero`. DRAT-trim also rejects a bogus empty DRAT clause on the same satisfiable CNF. The complete reproducer and logs are in `control_audit/C_checker_false_positive/` and `controls/satisfiable.cnf`.

This is an observed failure of this particular pinned C utility. It is not a failure of the LRAT inference rules or of the verified CakeML checker. The C utility is preserved only as an optional diagnostic, enabled by `--c-diagnostic`; its success is never an acceptance authority. No external issue report or communication has been sent.

The remaining controls remove required RAT witnesses, remove the hints for the final contradiction, alter a declared CNF hash, omit a declared case, give the wrong affine support transport, and omit a canonical support case. There is also a positive control taken from the upstream DRAT documentation that genuinely uses RAT rather than only reverse unit propagation.[2]

## Exact source provenance and formal scope

The package includes source and license files so that replay needs no downloads.

| Component | Exact upstream commit | Role |
|---|---|---|
| DRAT-trim | `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` | Validate DRAT and produce LRAT |
| `cake_lpr` distribution | `a36874a8b750b43fe4b385b8ddbf5b033e46a3fa` | Required final checker artifact |
| CakeML development recorded upstream | `fb377b4bb704497c921cde68ccc8da3b4f0e9132` | Upstream artifact provenance |
| HOL4 recorded upstream | `0ae7030322cdf2b0d46dc9d5503e2d5eae2fa726` | Upstream artifact provenance |

CakeML documents `cake_lpr` as a verified propagation-redundancy checker, with correctness carried to its generated machine-code artifact.[3–5] This session checks the published x86_64 assembly hash, assembles and links the distributed assembly with its C wrapper, and runs that executable. **This session does not rebuild HOL4, replay the upstream proof development, or formalize the Kakeya encoder.** The trusted execution environment, the C foreign-function interface, linking/loading, and the assumptions specified by the upstream machine-code theorem remain relevant. “An upstream verified checker artifact was run successfully” is the precise claim.

The assembly SHA256 is:

```text
2f3af32d55083839b3fa0e693afd817679c0b8944bef41def05a8b0ec72b7d4a
```

**The upstream checksum file is stale for the C wrapper at this pinned revision.** Its assembly and Makefile entries match. For `basis_ffi.c`, it records the older hash `3fbd8f31c380e7fb40fede74496ff8b7fb63043645b1afff1e5f26aacdccfa69`, whereas the actual pinned wrapper hash is `8e30d84fdcb2177aa5571d7fa6661a2fae5ecfd56baa0ce49c65f9233a9f87cb`. The wrapper was changed upstream to accept memory limits through command-line flags. The package records the discrepancy, exact commit, and actual file hash in `vendor/cake_lpr/PIN.json`; it does not claim all upstream checksum entries match.

## Replay the available certificates

Requirements are Python 3.8 or later, Linux x86_64, and `gcc` or a compatible C compiler. This was run on Linux x86_64 with GCC. Native Windows and other architectures have not been tested. An ARM checker artifact would require a separately pinned build.

From this directory:

```bash
python3 verify_pipeline.py
```

That command rebuilds all tools in a temporary directory, replays the archived examples, and rewrites `archived_audit/`, `control_audit/`, and `PROOF_AUDIT_REPLAY.json`. It performs no new Kakeya SAT search. The positive fixtures use 64 MB heap and 64 MB stack settings; the main audit defaults to 1024 MB heap and 256 MB stack, configurable for larger proofs.

For an explicit manifest of actual certificates:

```bash
python3 audit_certificates.py /absolute/path/m19_manifest.json \
  --output /absolute/path/m19_independent_audit \
  --timeout 3600 --heap-mb 4096 --stack-mb 256
```

The timeout applies to each checker process. Resource exhaustion leaves the case uncertified; increasing limits does not change the mathematical acceptance criterion. A failed new run replaces a previous receipt, so an older `PASS` receipt cannot stand in for a failed invocation in the same output directory.

## Explicit manifest contract

`ARCHIVED_EXAMPLES_MANIFEST.json` is a real runnable example. Each input path is absolute or relative to the manifest's directory. Required fields are:

```json
{
  "schema": "kakeya-proof-audit-v1",
  "label": "Description of the actual supplied certificate collection",
  "expected_case_ids": ["case_a"],
  "coverage_scope": "An explicit description of precisely what these cases cover",
  "encoder_soundness_status": "UNREVIEWED or a precise external theorem reference",
  "orbit_catalogue_completeness_status": "UNREVIEWED or a precise external certificate reference",
  "cases": [{
    "case_id": "case_a",
    "cnf": "actual_input.cnf",
    "proof": "actual_proof.drat",
    "cnf_sha256": "literal 64-character lowercase SHA256 of actual_input.cnf",
    "proof_sha256": "literal 64-character lowercase SHA256 of actual_proof.drat",
    "metadata": {"original_solver_case_id": "retain the real original identifier"}
  }]
}
```

This displayed template is explanatory and is not itself a checked manifest. Case identifiers must be safe filenames and unique. The actual case set must equal the expected case set exactly. Optional `semantic_reference_files` entries contain `path` and `sha256` for the exact encoder, mathematical conditions, support-generation program, or other provenance. Their hashes are checked; their correctness is not inferred from their existence.

An adapter must explicitly map the real Claude JSONL schema into this contract. No adapter pretending to know that unavailable schema has been written. In particular, a JSONL row saying `UNSAT` without its exact input CNF and proof is insufficient.

### The strict maximum-19 marked-support gate

The encoding-bridge work supplies a fixed contract containing **13 marked support classes of size 11 and 25 of size 12**. To use that stricter gate, add:

```json
"coverage_contract": {
  "path": "path/to/M19_MARKED_CASE_CONTRACT.json",
  "sha256": "8d6b60a180c3cefe124e8de47b3c308f840bad9b1b3d1b8b55764ff9f19a5118",
  "ring_scope": "common_relaxation_both_rings"
}
```

Use the exact 38 case IDs in that contract as `expected_case_ids`. Each case also needs:

```json
"marked_support": {
  "support": [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 17],
  "distinguished_hub": 0,
  "affine_map_to_contract": [0, 1, 2, 4, 8, 16]
}
```

The example is the contract representative for `s11_orbit65_hub0`. Points are integers 0–31 encoding vectors in F₂⁵. The six map entries are the offset followed by the five images of basis vectors. The checker verifies invertibility, that the actual distinguished hub maps to zero, and that the support maps exactly to its named representative. It also enforces the pinned contract hash and exact 13+25 inventory. Alternative representatives can obtain their map from the sibling encoding-bridge helper `map_marked_case.py`; the audit checks the map directly and does not need the helper's full enumeration table.

The ring scope is a declared mathematical assertion. A common necessary-condition relaxation may legitimately cover both rings with 38 proofs; its soundness must be established for both rings. If the encoding is ring-specific, use one complete 38-case manifest with `ring_scope: "z4"` and another with `ring_scope: "dual"`. The proof checker does not establish that a common relaxation or a ring-specific interpretation is sound.

**Matching the metadata is not a proof that a CNF encodes that support.** The contract gate does not inspect the meaning of variables or reconstruct conditions (A)–(E). Exact CNF regeneration and a mathematical counterexample-to-satisfying-assignment argument remain necessary. The receipt records these limits explicitly. The independent proof of catalogue completeness is in the sibling encoding-bridge report, not in this checker harness.

## What to obtain from the running session

Keep the existing solver sweep running. Obtain the exact 38 CNFs, original DRAT proofs, encoder source, mathematical statement of (A)–(E), case catalogue, distinguished hubs, and a literal manifest with their hashes. Then run this existing checker pipeline on those files. This targets a different remaining obligation from the ongoing SAT search and requires no repeat of the search itself. `CLAUDE_CHECKER_HANDOFF.txt` contains a concise handoff suitable for the user to paste.

## Primary sources

1. Cruz-Filipe, Heule, Hunt, Kaufmann, Schneider-Kamp, *Efficient Certified RAT Verification*: <https://www.cs.utexas.edu/~marijn/publications/lrat.pdf>.
2. Official DRAT-trim source and documented RAT example: <https://github.com/marijnheule/drat-trim/tree/2e3b2dc0ecf938addbd779d42877b6ed69d9a985>.
3. Official CakeML checker overview and trusted-base discussion: <https://cakeml.org/checkers.html>.
4. Tan, Heule, Myreen, *cake_lpr: Verified Propagation Redundancy Checking in CakeML*, TACAS 2021: <https://cakeml.org/tacas21.pdf>.
5. Pinned `cake_lpr` artifact repository and provenance: <https://github.com/tanyongkiam/cake_lpr/tree/a36874a8b750b43fe4b385b8ddbf5b033e46a3fa>.
