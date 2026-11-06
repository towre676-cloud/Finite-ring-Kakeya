#!/usr/bin/env python3
"""List archive-only omissions after successful full compact proof replay.

No certificate or original workspace file is deleted or modified.
"""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
import compact_certificates as C


def main():
    compact, source = C.load()
    replay_path = C.HERE / "COMPACT_CERTIFICATE_REPLAY.json"
    replay = json.loads(replay_path.read_text())
    C.A.require(replay["status"] == "PASS_ALL_ROUND8_OUTCOMES_VIA_COMPACT_EXACT_CNF_CAKEML_PROOFS" and
                replay["full_inventory_replayed"] and replay["compact_manifest_sha256"] == C.A.sha(C.MANIFEST),
                "Successful complete compact replay is required")
    rows = {r["case_id"]: r for r in replay["cases"]}
    C.A.require(len(rows) == len(replay["cases"]) == len(compact["cases"]) and
                set(rows) == set(compact["case_ids"]), "Full replay omitted an outcome")
    omitted = []
    for case in compact["cases"]:
        original = case["original_case"]
        if case["representation"] != "COMPACT_DRAT":
            C.A.require(rows[case["case_id"]]["exclusion_credited"] is False, "Uncertified case acquired credit")
            continue
        checked = rows[case["case_id"]]
        C.A.require(checked["status"] == C.V.PASS and checked["audit"]["input_sha256"] ==
                    {"cnf": original["cnf_sha256"], "drat": case["core_sha256"]}, "Replacement input binding differs")
        path = C.SOURCE_DIR / "cases" / case["case_id"] / "proof.drat.xz"
        metadata = original["storage"]["proof.drat"]
        if path.exists():
            C.A.require(C.A.sha(path) == metadata["xz_sha256"], "Existing original payload changed")
        omitted.append({"path": str(path.relative_to(C.ROOT)), "sha256": metadata["xz_sha256"],
                        "bytes": metadata["xz_bytes"], "replacement_core_sha256": case["core_sha256"],
                        "replacement_xz_path": str((C.HERE / "cases" / case["case_id"] / "core.drat.xz").relative_to(C.ROOT))})
    plan = {"status": "PASS_ARCHIVE_ONLY_ROUND8_PROOF_OMISSION_PLAN",
            "compact_manifest_sha256": C.A.sha(C.MANIFEST), "full_replay_receipt_sha256": C.A.sha(replay_path),
            "omit_from_archive_only": omitted, "original_workspace_files_deleted": False,
            "original_proof_xz_bytes": sum(r["bytes"] for r in omitted),
            "replacement_core_xz_bytes": compact["compact_proof_bytes"],
            "retain": "Every original CNF, CASE_RECEIPT, semantic source/freeze, source manifest, RUP provenance, core and core receipt."}
    C.dump(C.HERE / "ARCHIVE_PAYLOAD_PLAN.json", plan)
    print(json.dumps({k: plan[k] for k in ("status", "original_proof_xz_bytes", "replacement_core_xz_bytes")}))


if __name__ == "__main__":
    main()
