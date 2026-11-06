#!/usr/bin/env python3
"""Compile the shear bridge with pinned Lean/mathlib and audit all axioms."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMMIT = "f897ebcf72cd16f89ab4577d0c826cd14afaafc7"
THEOREMS = {
    "xor_cancel_right", "shear_involution", "shearEquiv", "shear_pair_vector",
    "shear_pair_iff", "shear_endpoint", "lineContained_shear_iff",
    "line_exists_shear_iff", "binaryKakeya_shear_iff", "shear_anchor",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    started = time.monotonic()
    target = HERE / "SHEAR_LEAN_REPLAY.json"
    target.write_text(json.dumps({"status": "RUNNING"}) + "\n")
    source = HERE / "ShearBridge.lean"
    carry = ROOT / "research_round5/encoding_bridge/CarryBridge.lean"
    try:
        work = args.mathlib.resolve()
        binary = args.lean_bin.resolve()
        env = dict(os.environ)
        env["PATH"] = str(binary) + os.pathsep + env.get("PATH", "")
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work,
                                capture_output=True, text=True, check=True).stdout.strip()
        assert commit == COMMIT, commit
        version = subprocess.run([str(binary / "lean"), "--version"], env=env,
                                 capture_output=True, text=True, check=True).stdout.strip()
        assert "version 4.24.0," in version, version
        for p in (source, carry):
            text = p.read_text()
            assert not re.search(r"\b(sorry|admit|native_decide)\b", text), str(p)
            assert not re.search(r"^\s*axiom\s", text, re.MULTILINE), str(p)
        with tempfile.TemporaryDirectory(prefix="kakeya_r7_lean_") as temporary:
            output = Path(temporary)
            old = subprocess.run([str(binary / "lake"), "env", str(binary / "lean"),
                                  "--root=" + str(carry.parent),
                                  "-o", str(output / "CarryBridge.olean"), str(carry)],
                                 cwd=work, env=env, capture_output=True, text=True)
            (HERE / "CARRY_DEPENDENCY_COMPILE_LOG.txt").write_text(old.stdout + old.stderr)
            assert old.returncode == 0, old.stdout + old.stderr
            paths = subprocess.run([str(binary / "lake"), "env", "printenv", "LEAN_PATH"],
                                   cwd=work, env=env, capture_output=True, text=True, check=True)
            env["LEAN_PATH"] = str(output) + os.pathsep + paths.stdout.strip()
            new = subprocess.run([str(binary / "lean"), "--root=" + str(HERE), str(source)], cwd=work,
                                 env=env, capture_output=True, text=True)
        log = new.stdout + new.stderr
        (HERE / "SHEAR_LEAN_COMPILE_LOG.txt").write_text(log)
        assert new.returncode == 0, log
        assert "sorryAx" not in log and "error:" not in log
        audits = {}
        for name, raw in re.findall(r"'KakeyaRound7\.([^']+)' depends on axioms: \[([^\]]*)\]", log):
            axioms = [x.strip() for x in raw.split(",") if x.strip()]
            assert name not in audits
            assert set(axioms) <= {"propext", "Quot.sound", "Classical.choice"}
            audits[name] = axioms
        for name in re.findall(r"'KakeyaRound7\.([^']+)' does not depend on any axioms", log):
            assert name not in audits
            audits[name] = []
        assert set(audits) == THEOREMS, (set(audits), THEOREMS)
        result = {
            "status": "PASS_PINNED_LEAN_AFFINE_TANGENT_SHEAR_BRIDGE",
            "lean_version": version, "mathlib_commit": commit,
            "theorem_and_equivalence_count": len(audits), "axiom_audits": audits,
            "formalized": [
                "Every fibre tangent translation is an involution/equivalence.",
                "Common affine tangent shear transports pair and carried line witnesses exactly.",
                "For every index type and both coordinate ring kinds, primitive Kakeya coverage is invariant under any XOR-linear shear with common tangent translation.",
                "A specified interpolation value puts a chosen fibre point at tangent zero.",
            ],
            "not_formalized": [
                "Existence of the linear interpolant on five independent residue vectors.",
                "The Python encoders, their emitted CNFs, exact quotient enumeration, or support-orbit completeness.",
                "Any unrestricted dimension-five lower bound.",
            ],
            "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [source, carry, Path(__file__)]},
            "compile_log_sha256": sha(HERE / "SHEAR_LEAN_COMPILE_LOG.txt"),
            "seconds": round(time.monotonic() - started, 6),
        }
        target.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0
    except Exception as error:
        target.write_text(json.dumps({"status": "FAIL", "error": repr(error)}, indent=2) + "\n")
        print(repr(error))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mathlib", type=Path, required=True)
    parser.add_argument("--lean-bin", type=Path, required=True)
    raise SystemExit(run(parser.parse_args()))
