# Round 5 semantic bridge and the complete 38-case support contract

Read ENCODING_AND_SYMMETRY_BRIDGE.md for the mathematical proof and exact
scope. Claude's actual A–E definitions, CNFs, and new DRAT files were not
available in this workspace and have not been checked by this component.

## Main outputs

* M19_MARKED_CASE_CONTRACT.json: the 38 explicit marked support cases,
  comprising 13 at support 11 and 25 at support 12, with hub transport maps.
* NORMALIZED_SUPPORT_TO_CASE.csv: 102,324 explicit linear-map witnesses.
* NORMALIZED_COVER_REPLAY.json: complete independent cover and disjointness
  check over all 296,010 coordinate-basis-containing supports; no inherited
  affine-catalogue completeness dependency.
* CarryBridge.lean and CARRY_LEAN_REPLAY.json: 15 kernel-checked coordinate,
  ring-carry, and line-to-pair statements; actual CNF soundness remains open.
* map_marked_case.py: map any supplied support and distinguished hub to its
  exact contract ID and an explicit affine equivalence witness.

The complete finite coverage checker is:

    python3 research_round5/encoding_bridge/verify_marked_cover.py

It uses Python's standard library, takes approximately 7 seconds, and does
not import the producer or read the inherited 382-class catalogue. The earlier
candidate/automorphism replay is optional for reproducing that discovery
stage:

    python3 research_round5/encoding_bridge/verify_marked_supports.py

Its source catalogue dependency does not apply to the later direct cover
certificate. Both stages are retained with their separate scopes.

## Mapping a Claude case

The Python API is:

    canonical_case_id(support, distinguished_hub)
    map_marked_support(support, distinguished_hub)

The latter returns affine_map_to_contract=[offset,column0,...,column4].
The affine map is evaluated by XORing the columns selected by the input's
bits and then XORing the offset. It sends the supplied hub to 0, has an
invertible linear part, and sends the supplied support to the named target.
The function directly checks those properties. This support mapping does
not itself prove that a named CNF encodes the supplied support.

The CLI reads one JSON object on stdin with fields support (a list of 11 or 12
distinct integers 0..31) and distinguished_hub (one of those integers).

## Lean replay

The adjacent lean-toolchain and lakefile.toml pin Lean and Mathlib. With the
dependencies installed, run from this directory:

    lake update
    lake exe cache get
    python3 verify_carry_lean.py

Or reuse a pinned checkout:

    python3 verify_carry_lean.py --mathlib /path/to/mathlib4 --lean-bin /path/to/lean/bin

The checker invokes the actual Lean compiler, checks all 15 printed theorem
axiom audits, and records source and log hashes. The finite support
enumeration and affine normalization are not part of this Lean module.

Do not include the compiled enumerate_marked_supports or certify_marked_cover
executables in a portable archive; their C++17 sources are supplied. Include
the CSV mapping certificate as well as the JSON and source files.
