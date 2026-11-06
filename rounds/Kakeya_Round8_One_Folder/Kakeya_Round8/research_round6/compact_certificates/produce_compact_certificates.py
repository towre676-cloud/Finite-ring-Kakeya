"""Convert accepted LRAT cores to smaller standard DRAT storage certificates.

Every generated DRAT is independently checked by pinned DRAT-trim -> LRAT ->
CakeML on the unchanged exact CNF. All live streams remain in private /tmp
workspaces. The final compressed DRATs are sufficient for portable replay;
the original dense LRATs are provenance only.
"""
from pathlib import Path
import argparse
import concurrent.futures
import errno
import hashlib
import importlib.util
import json
import lzma
import os
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "compact_core_semantics", ROOT / "research_round6/proof_core/verify_cores.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
A, STORAGE = V.A, V.STORAGE
JOINT_MANIFEST = ROOT / "research_round6/joint_maxima/JOINT_CERTIFICATE_MANIFEST.json"


def dump(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def publish(source, destination):
    source, destination = Path(source), Path(destination)
    try:
        source.replace(destination)
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
        candidate = destination.with_suffix(destination.suffix + ".tmp")
        shutil.copyfile(source, candidate)
        if A.sha(candidate) != A.sha(source):
            raise ValueError("Publication copy changed")
        candidate.replace(destination)
        source.unlink()


def inputs():
    index = json.loads((ROOT / "research_round6/proof_core/CORE_BATCH_RECEIPT.json").read_text())
    rows, coverage = V.inventory(index)
    if index["scope"] != "joint" or len(rows) != 38:
        raise ValueError("Expected the complete38 joint source-core cases")
    return rows, coverage


def convert_stream(row, cnf, work):
    source_folder = ROOT / "research_round6/proof_core/cases" / row["case_id"]
    source = source_folder / row["core_file"]
    if A.sha(source) != row["compressed_sha256"]:
        raise ValueError("Source core archive hash mismatch")
    target = work / "proof.drat"
    digest = hashlib.sha256()
    count = 0
    started = time.monotonic()
    with (work / "conversion.stderr.txt").open("wb") as errors:
        child = subprocess.Popen(
            [HERE / "bin/lrat_to_drat", cnf, "/dev/stdin", target],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors)
        try:
            with lzma.open(source, "rb") as stream:
                for block in iter(lambda: stream.read(4 << 20), b""):
                    count += len(block)
                    if count > row["core_bytes"]:
                        raise ValueError("Source core exceeds declared size")
                    digest.update(block)
                    child.stdin.write(block)
            child.stdin.close()
            stdout = child.stdout.read().decode()
            code = child.wait(timeout=120)
        except BaseException:
            child.kill()
            child.wait()
            raise
    (work / "conversion.stdout.txt").write_text(stdout)
    if code != 0:
        raise RuntimeError("LRAT-to-DRAT conversion failed: " +
                           (work / "conversion.stderr.txt").read_text())
    if count != row["core_bytes"] or digest.hexdigest() != row["core_sha256"]:
        raise ValueError("Expanded source core hash/size mismatch")
    if A.sha(source) != row["compressed_sha256"]:
        raise ValueError("Source core changed during conversion")
    return target, json.loads(stdout), round(time.monotonic() - started, 6)


def one(task):
    row, timeout, heap_mb = task
    started = time.monotonic()
    folder = HERE / "cases" / row["case_id"]
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / "CASE_RECEIPT.json"
    stored = folder / "proof.drat.xz"
    old_folder = ROOT / "research_round6/proof_core/cases" / row["case_id"]
    logical_cnf = (old_folder / row["cnf_from_case_folder"]).resolve()
    manifest_sha = A.sha(JOINT_MANIFEST)
    if receipt.exists() and stored.exists():
        old = json.loads(receipt.read_text())
        if (old.get("status") == "PASS_COMPACT_DRAT_VIA_CAKEML"
                and old.get("joint_manifest_sha256") == manifest_sha
                and old.get("cnf_sha256") == row["cnf_sha256"]
                and A.sha(stored) == old.get("compressed_sha256")
                and STORAGE.logical_sha(logical_cnf, prefer_compressed=True) == row["cnf_sha256"]):
            return old
    record = {
        "status": "CONVERTING", "case_id": row["case_id"],
        "source_kind": "joint", "maximum_interval": [2, 18], "total_upper_bound": 93,
        "marked_support": row["marked_support"], "cnf_sha256": row["cnf_sha256"],
        "expected_lrat_sha256": row["expected_lrat_sha256"],
        "joint_manifest_sha256": manifest_sha,
        "source_core_sha256": row["core_sha256"], "source_core_bytes": row["core_bytes"],
        "source_core_compressed_sha256": row["compressed_sha256"],
        "source_core_receipt_sha256": A.sha(old_folder / "CORE_RECEIPT.json"),
        "cnf_from_case_folder": os.path.relpath(logical_cnf, folder),
        "converter_trusted_for_unsat": False, "original_files_modified": False,
    }
    dump(receipt, record)
    try:
        with tempfile.TemporaryDirectory(prefix="kakeya_compact_drat_", dir="/tmp") as temporary:
            work = Path(temporary)
            with STORAGE.materialized(logical_cnf, row["cnf_sha256"], directory=temporary,
                                      prefer_compressed=True) as cnf:
                proof, stats, seconds = convert_stream(row, cnf, work)
                record.update(status="CHECKING", conversion=stats, conversion_seconds=seconds,
                              drat_sha256=A.sha(proof), drat_bytes=proof.stat().st_size)
                dump(receipt, record)
                binaries = {name: HERE / "bin" / name for name in ("drat-trim", "lrat-check", "cake_lpr")}
                audit = A.check_pair(cnf, proof, work / "audit", binaries,
                                     timeout, heap_mb, 256, False)
                record["audit"] = audit
                if audit["status"] != "PASS_CNF_UNSAT_VIA_CAKEML_LRAT":
                    raise RuntimeError("Required DRAT-trim and CakeML route did not accept")
                # The checked regenerated LRAT is now provenance, not payload.
                (work / "audit/converted.lrat").unlink()
                record["status"] = "COMPRESSING_ACCEPTED_DRAT"
                dump(receipt, record)
                compressed = work / "proof.drat.xz"
                t = time.monotonic()
                with proof.open("rb") as source, lzma.open(compressed, "wb", preset=3) as destination:
                    shutil.copyfileobj(source, destination, 4 << 20)
                record.update(compression_seconds=round(time.monotonic() - t, 6),
                              compressed_bytes=compressed.stat().st_size,
                              compressed_sha256=A.sha(compressed))
                digest = hashlib.sha256()
                decoded = 0
                with lzma.open(compressed, "rb") as source:
                    for block in iter(lambda: source.read(4 << 20), b""):
                        decoded += len(block)
                        digest.update(block)
                if decoded != record["drat_bytes"] or digest.hexdigest() != record["drat_sha256"]:
                    raise ValueError("Stored DRAT does not decode to accepted proof")
                if A.sha(cnf) != record["cnf_sha256"] or A.sha(proof) != record["drat_sha256"]:
                    raise ValueError("Accepted input changed before publication")
                (folder / "audit").mkdir(exist_ok=True)
                for p in (work / "audit").glob("*.txt"):
                    publish(p, folder / "audit" / p.name)
                for name in ("conversion.stdout.txt", "conversion.stderr.txt"):
                    publish(work / name, folder / name)
                publish(compressed, stored)
                if A.sha(stored) != record["compressed_sha256"]:
                    raise ValueError("Published DRAT archive changed")
                if STORAGE.logical_sha(logical_cnf, prefer_compressed=True) != record["cnf_sha256"]:
                    raise ValueError("Original CNF archive changed")
            record.update(status="PASS_COMPACT_DRAT_VIA_CAKEML",
                          proof_file="proof.drat.xz", exact_compression_roundtrip=True,
                          seconds=round(time.monotonic() - started, 6))
            dump(receipt, record)
            return record
    except Exception as error:
        record.update(status="COMPACT_CERTIFICATE_NOT_ACCEPTED", error=repr(error),
                      seconds=round(time.monotonic() - started, 6))
        dump(receipt, record)
        return record


def manifest(results):
    original = json.loads(JOINT_MANIFEST.read_text())
    cases = []
    for row in sorted(results, key=lambda r: r["case_id"]):
        case_folder = HERE / "cases" / row["case_id"]
        cnf = (case_folder / row["cnf_from_case_folder"]).resolve()
        entry = {key: row[key] for key in
                 ("case_id", "source_kind", "maximum_interval", "total_upper_bound",
                  "marked_support", "cnf_sha256", "expected_lrat_sha256",
                  "source_core_sha256", "source_core_bytes", "source_core_compressed_sha256",
                  "drat_sha256", "drat_bytes", "compressed_sha256", "compressed_bytes")}
        entry.update(cnf=os.path.relpath(cnf, HERE),
                     proof=f"cases/{row['case_id']}/proof.drat.xz",
                     receipt=f"cases/{row['case_id']}/CASE_RECEIPT.json",
                     receipt_sha256=A.sha(case_folder / "CASE_RECEIPT.json"))
        cases.append(entry)
    return {
        "schema": "kakeya-compact-drat-v1",
        "status": "PASS_COMPLETE_38_COMPACT_DRAT_CERTIFICATES",
        "scope": "joint_maximum_2_18", "maximum_interval": [2, 18], "total_upper_bound": 93,
        "ring_scope": "common_necessary_relaxation_both_rings",
        "original_joint_manifest": {"path": os.path.relpath(JOINT_MANIFEST, HERE),
                                    "sha256": A.sha(JOINT_MANIFEST)},
        "semantic_input_hashes": original["semantic_input_hashes"],
        "coverage_contract": {"path": "../../research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json",
                              "sha256": A.M19_CONTRACT_SHA256,
                              "ring_scope": "common_relaxation_both_rings"},
        "expected_case_ids": original["expected_case_ids"], "cases": cases,
        "original_dense_lrat_required_for_replay": False,
        "converter_trusted_for_unsat": False,
        "compressed_proof_bytes": sum(r["compressed_bytes"] for r in cases),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--heap-mb", type=int, default=1024)
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()
    if args.jobs not in (1, 2):
        raise ValueError("Use one or two workers; coordinate with other proof batches")
    rows, coverage = inputs()
    if args.case:
        rows = [r for r in rows if r["case_id"] in args.case]
        if len(rows) != len(set(args.case)):
            raise ValueError("Unknown selected case")
    rows.sort(key=lambda r: r["core_bytes"], reverse=True)
    (HERE / "bin").mkdir(exist_ok=True)
    compiled = subprocess.run(
        ["g++", "-O3", "-std=c++17", "-Wall", "-Wextra", "-pedantic",
         str(HERE / "lrat_to_drat.cpp"), "-o", str(HERE / "bin/lrat_to_drat")],
        capture_output=True, text=True, check=True)
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / "bin", HERE / "build_logs")
    dump(HERE / "BUILD_RECEIPT.json",
         {"pinned_sources": pins, "checker_build": build,
          "converter_source_sha256": A.sha(HERE / "lrat_to_drat.cpp"),
          "converter_build_stdout": compiled.stdout, "converter_build_stderr": compiled.stderr})
    started = time.monotonic()
    results = []
    target = HERE / ("SELECTED_COMPACT_BATCH_RECEIPT.json" if args.case else "COMPACT_BATCH_RECEIPT.json")
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(one, (row, args.timeout, args.heap_mb)) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps({k: result.get(k) for k in
                              ("case_id", "status", "drat_bytes", "compressed_bytes", "seconds")}), flush=True)
            dump(target, {"status": "RUNNING", "expected_cases": len(rows),
                          "completed_cases": len(results), "cases": results})
    good = len(results) == len(rows) and all(
        r["status"] == "PASS_COMPACT_DRAT_VIA_CAKEML" for r in results)
    dump(target, {"status": "PASS_ALL_REQUESTED_COMPACT_CERTIFICATES" if good else "INCOMPLETE_OR_FAILED",
                  "expected_cases": len(rows), "completed_cases": len(results), "cases": results,
                  "complete_scope": not args.case, "coverage": coverage,
                  "seconds": round(time.monotonic() - started, 6),
                  "compressed_bytes": sum(r.get("compressed_bytes", 0) for r in results)})
    if good and not args.case:
        dump(HERE / "COMPACT_CERTIFICATE_MANIFEST.json", manifest(results))
    print("PASS_ALL_REQUESTED_COMPACT_CERTIFICATES" if good else "INCOMPLETE_OR_FAILED", flush=True)
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
