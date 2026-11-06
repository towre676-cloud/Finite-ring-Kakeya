"""Recheck every stored core and regenerate every exact CNF after publication.

This is an integrity/encoding replay, not an additional CakeML invocation.
Each core already has a fresh mandatory CakeML acceptance in its production
receipt. verify_cores.py performs a further full checker replay when requested.
"""
from pathlib import Path
import hashlib
import json
import lzma
import tempfile
import time

import verify_cores as V

HERE = Path(__file__).resolve().parent


def main():
    started = time.monotonic()
    index = json.loads((HERE / "CORE_BATCH_RECEIPT.json").read_text())
    rows, coverage = V.inventory(index)
    results = []
    for row in sorted(rows, key=lambda row: row["case_id"]):
        case_started = time.monotonic()
        folder = HERE / "cases" / row["case_id"]
        cnf = (folder / row["cnf_from_case_folder"]).resolve()
        stored = folder / row["core_file"]
        V.A.require(V.STORAGE.logical_sha(cnf, prefer_compressed=True) == row["cnf_sha256"],
                    "Stored CNF digest mismatch")
        V.A.require(V.A.sha(stored) == row["compressed_sha256"], "Stored compressed digest mismatch")
        with tempfile.TemporaryDirectory(prefix="kakeya_core_regenerate_", dir="/tmp") as temporary:
            V.regenerate_exact_cnf(row, Path(temporary) / "regenerated.cnf")
        digest = hashlib.sha256()
        size = 0
        with lzma.open(stored, "rb") as source:
            for block in iter(lambda: source.read(4 << 20), b""):
                size += len(block)
                V.A.require(size <= row["core_bytes"], "Decoded proof exceeds declared size")
                digest.update(block)
        V.A.require(size == row["core_bytes"] and digest.hexdigest() == row["core_sha256"],
                    "Decoded proof differs from the accepted core")
        results.append({"case_id": row["case_id"], "status": "PASS_STORED_BYTES_AND_EXACT_CNF_REGENERATION",
                        "cnf_sha256": row["cnf_sha256"], "core_sha256": row["core_sha256"],
                        "compressed_sha256": row["compressed_sha256"],
                        "seconds": round(time.monotonic() - case_started, 6)})
        print(row["case_id"], "PASS", flush=True)
    report = {"status": "PASS_ALL_CORE_STORAGE_AND_REGENERATED_CNFS",
              "scope": index["scope"], "cases_checked": len(results), "cases": results,
              "coverage_and_semantic_source_bindings": coverage,
              "new_cakeml_invocations_in_this_integrity_run": 0,
              "prior_mandatory_cakeml_acceptance": "Every case's CORE_RECEIPT.json",
              "compressed_bytes": sum(row["compressed_bytes"] for row in rows),
              "original_lrat_bytes": sum(row["original_lrat_bytes"] for row in rows),
              "core_bytes": sum(row["core_bytes"] for row in rows),
              "seconds": round(time.monotonic() - started, 6)}
    (HERE / "CORE_INTEGRITY_REPLAY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
