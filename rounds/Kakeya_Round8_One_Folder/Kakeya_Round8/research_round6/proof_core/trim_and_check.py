"""Produce compact, independently accepted LRAT cores from saved certificates.

All producers here are untrusted. Every credited core is checked by the pinned
upstream CakeML executable against the exact original CNF. Original files are
never modified or deleted. Only closed, checked XZ artifacts and receipts are
published. Temporary raw files are removed when their per-case workspace closes.
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
    "core_pinned_audit", ROOT / "research_round5/proof_audit/audit_certificates.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


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
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        shutil.copy2(source, temporary)
        temporary.replace(destination)
        source.unlink()


def discover(scope):
    result = []
    for kind, folder in (("joint", "joint_maxima"), ("m19", "certification")):
        if scope != "both" and scope != kind:
            continue
        cases = ROOT / "research_round6" / folder / "cases"
        rows = []
        for receipt in sorted(cases.glob("*/CASE_RECEIPT.json")):
            record = json.loads(receipt.read_text())
            if record.get("status") != "PASS_CNF_UNSAT_VIA_CAKEML_LRAT":
                continue
            cnf = receipt.parent / "input.cnf"
            proof = receipt.parent / ("proof.lrat" if kind == "joint" else "audit/converted.lrat")
            expected = record["lrat_sha256"] if kind == "joint" else record["audit"]["lrat_sha256"]
            if not proof.is_file():
                proof = proof.with_suffix(proof.suffix + ".xz")
            if not proof.is_file() or not cnf.is_file():
                raise FileNotFoundError(f"Missing exact certificate input for {record['case_id']}")
            case_id = record["case_id"] if kind == "joint" else "m19_" + record["case_id"]
            rows.append({
                "case_id": case_id, "source_kind": kind,
                "cnf": str(cnf), "source_lrat": str(proof),
                "expected_cnf_sha256": record["cnf_sha256"],
                "expected_lrat_sha256": expected,
                "source_receipt": str(receipt),
                "source_receipt_sha256": A.sha(receipt),
                "original_case_id": record["case_id"],
                "marked_support": record["marked_support"],
                "maximum_interval": record.get("maximum_interval", [19, 19]),
                "original_lrat_bytes": record.get("lrat_bytes", record.get("audit", {}).get("lrat_bytes")),
            })
        if len(rows) != 38:
            raise ValueError(f"Expected38 accepted {kind} cases, found {len(rows)}")
        result.extend(rows)
    return result


def materialize(proof, destination, expected):
    proof = Path(proof)
    if proof.suffix != ".xz":
        if A.sha(proof) != expected:
            raise ValueError("Original LRAT hash disagrees with accepted receipt")
        return proof, False
    digest = hashlib.sha256()
    with lzma.open(proof, "rb") as source, destination.open("wb") as out:
        for block in iter(lambda: source.read(4 << 20), b""):
            digest.update(block)
            out.write(block)
    if digest.hexdigest() != expected:
        raise ValueError("Decompressed original LRAT hash disagrees with receipt")
    return destination, True


def one(task):
    row, timeout, heap_mb, dictionary_mib, adopted_core = task
    started = time.monotonic()
    folder = HERE / "cases" / row["case_id"]
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / "CORE_RECEIPT.json"
    cnf = Path(row["cnf"])
    compressed = folder / "core.lrat.xz"
    if receipt.is_file() and compressed.is_file():
        old = json.loads(receipt.read_text())
        if (old.get("status") == "PASS_CORE_LRAT_VIA_CAKEML"
                and old.get("cnf_sha256") == row["expected_cnf_sha256"]
                and A.sha(cnf) == row["expected_cnf_sha256"]
                and A.sha(compressed) == old.get("compressed_sha256")):
            return old
    record = dict(row)
    record.update(status="PREPARING", trimmer_trusted_for_unsat=False,
                  checker="pinned upstream CakeML cake_lpr",
                  original_files_modified=False)
    dump(receipt, record)
    try:
        if A.sha(cnf) != row["expected_cnf_sha256"]:
            raise ValueError("Original CNF hash disagrees with accepted receipt")
        record["cnf_sha256"] = row["expected_cnf_sha256"]
        with tempfile.TemporaryDirectory(prefix="kakeya_lrat_core_", dir="/tmp") as temporary:
            work = Path(temporary)
            original, copied = materialize(
                row["source_lrat"], work / "original.lrat", row["expected_lrat_sha256"])
            if adopted_core:
                core = Path(adopted_core).resolve()
                record["trimming"] = {"status": "EXISTING_CANDIDATE_REQUIRES_FRESH_CHECK",
                                      "source_candidate": str(core)}
            else:
                core = work / "core.lrat"
                command = [HERE / "bin/lrat_core", cnf, original, core]
                trimmed = subprocess.run([str(p) for p in command],
                                         capture_output=True, text=True, timeout=timeout)
                (work / "trim.stdout.txt").write_text(trimmed.stdout)
                (work / "trim.stderr.txt").write_text(trimmed.stderr)
                if trimmed.returncode != 0:
                    raise RuntimeError("Untrusted trimmer failed: " + trimmed.stderr)
                record["trimming"] = json.loads(trimmed.stdout)
            record.update(status="CHECKING", core_bytes=core.stat().st_size,
                          core_sha256=A.sha(core))
            dump(receipt, record)
            checked = A.run_checker(
                [HERE / "bin/cake_lpr", f"--CML_HEAP_SIZE={heap_mb}",
                 "--CML_STACK_SIZE=256", cnf, core],
                work, "cake_lpr", timeout, "s VERIFIED UNSAT", True)
            record["cake_lpr"] = checked
            if not checked["accepted"]:
                for name in ("cake_lpr.stdout.txt", "cake_lpr.stderr.txt"):
                    shutil.copy2(work / name, folder / name)
                raise RuntimeError("CakeML rejected or did not complete")
            if A.sha(core) != record["core_sha256"] or A.sha(cnf) != record["cnf_sha256"]:
                raise RuntimeError("CNF or candidate core changed during checking")
            # The original input is not needed after this point. A decompressed
            # copy belongs only to this private temporary workspace.
            if copied:
                original.unlink()
            record["status"] = "COMPRESSING_ACCEPTED_CORE"
            dump(receipt, record)
            candidate = work / "core.lrat.xz"
            filters = [{"id": lzma.FILTER_LZMA2, "preset": 3,
                        "dict_size": dictionary_mib << 20}]
            compress_started = time.monotonic()
            with core.open("rb") as source, lzma.open(candidate, "wb", filters=filters) as out:
                shutil.copyfileobj(source, out, 4 << 20)
            record.update(compression_seconds=round(time.monotonic() - compress_started, 6),
                          compression={"format": "xz", "lzma2_preset": 3,
                                       "dictionary_mib": dictionary_mib},
                          compressed_bytes=candidate.stat().st_size,
                          compressed_sha256=A.sha(candidate))
            # Verify the archived bytes decode to the exact accepted ASCII proof.
            digest = hashlib.sha256()
            with lzma.open(candidate, "rb") as source:
                for block in iter(lambda: source.read(4 << 20), b""):
                    digest.update(block)
            if digest.hexdigest() != record["core_sha256"]:
                raise RuntimeError("Compressed artifact fails exact roundtrip hash")
            for name in ("cake_lpr.stdout.txt", "cake_lpr.stderr.txt",
                         "trim.stdout.txt", "trim.stderr.txt"):
                if (work / name).is_file():
                    publish(work / name, folder / name)
            publish(candidate, compressed)
            if A.sha(compressed) != record["compressed_sha256"]:
                raise RuntimeError("Published compressed proof differs from accepted artifact")
            if A.sha(cnf) != record["cnf_sha256"]:
                raise RuntimeError("Original CNF changed before publication")
            record.update(status="PASS_CORE_LRAT_VIA_CAKEML",
                          exact_compression_roundtrip=True,
                          cnf_from_case_folder=os.path.relpath(cnf, folder),
                          core_file="core.lrat.xz",
                          seconds=round(time.monotonic() - started, 6))
            dump(receipt, record)
            return record
    except Exception as error:
        record.update(status="CORE_NOT_ACCEPTED", error=repr(error),
                      seconds=round(time.monotonic() - started, 6))
        dump(receipt, record)
        return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["joint", "m19", "both"], default="joint")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--heap-mb", type=int, default=1024)
    parser.add_argument("--dictionary-mib", type=int, default=64)
    parser.add_argument("--adopt-core")
    args = parser.parse_args()
    if args.jobs not in (1, 2):
        raise ValueError("Use one or two workers")
    rows = discover(args.scope)
    if args.case:
        rows = [row for row in rows if row["case_id"] in args.case]
        if len(rows) != len(set(args.case)):
            raise ValueError("Unknown requested case")
    if args.adopt_core and len(rows) != 1:
        raise ValueError("--adopt-core requires exactly one case")
    rows.sort(key=lambda row: row["original_lrat_bytes"], reverse=True)
    (HERE / "bin").mkdir(exist_ok=True)
    build = subprocess.run(
        ["g++", "-O3", "-std=c++17", "-Wall", "-Wextra", "-pedantic",
         str(HERE / "lrat_core.cpp"), "-o", str(HERE / "bin/lrat_core")],
        capture_output=True, text=True, check=True)
    pins = A.verify_sources()
    binaries, checker_build = A.build_checkers(HERE / "bin", HERE / "build_logs")
    dump(HERE / "BUILD_RECEIPT.json", {"pinned_sources": pins,
                                      "checker_build": checker_build,
                                      "trimmer_source_sha256": A.sha(HERE / "lrat_core.cpp"),
                                      "trimmer_build_stdout": build.stdout,
                                      "trimmer_build_stderr": build.stderr})
    results = []
    started = time.monotonic()
    batch_file = HERE / ("SELECTED_CORE_RECEIPT.json" if args.case else "CORE_BATCH_RECEIPT.json")
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(one, (row, args.timeout, args.heap_mb,
                                     args.dictionary_mib, args.adopt_core)) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            results.append(row)
            print(json.dumps({k: row.get(k) for k in
                              ["case_id", "status", "original_lrat_bytes",
                               "core_bytes", "compressed_bytes", "seconds"]}), flush=True)
            dump(batch_file, {"status": "RUNNING", "expected_cases": len(rows),
                              "completed_cases": len(results), "cases": results})
    good = len(results) == len(rows) and all(
        row["status"] == "PASS_CORE_LRAT_VIA_CAKEML" for row in results)
    dump(batch_file, {"status": "PASS_ALL_REQUESTED_CORES" if good else "INCOMPLETE_OR_FAILED",
                      "expected_cases": len(rows), "completed_cases": len(results),
                      "scope": args.scope, "selection_complete_for_scope": not args.case,
                      "cases": results,
                      "compressed_bytes": sum(row.get("compressed_bytes", 0) for row in results),
                      "seconds": round(time.monotonic() - started, 6)})
    print("PASS_ALL_REQUESTED_CORES" if good else "INCOMPLETE_OR_FAILED", flush=True)
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
