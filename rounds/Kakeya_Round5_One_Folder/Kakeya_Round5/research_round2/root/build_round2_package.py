"""Build the self-contained new-work replay supplement and its payload hashes."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
selected = set()
allowed = {".py", ".cpp", ".hpp", ".json", ".jsonl", ".md", ".txt", ".csv"}
excluded_names = {"MIDDLE_RESEARCH_MANIFEST.json", "GLOBAL_SPECTRUM_15_18.jsonl", "GLOBAL_SPECTRUM_19_25.jsonl", "PORTABLE_REPLAY_DIRECTORY.txt"}
for path in (ROOT / "research_round2").rglob("*"):
    if path.is_file() and path.suffix in allowed and "library_transfer" not in path.parts and "__pycache__" not in path.parts and path.name not in excluded_names:
        selected.add(path.relative_to(ROOT).as_posix())

required = [
    "VERIFY_ALL.py", "README_Round2.txt", "Kakeya_Research_Round2_Report.txt", "Kakeya_Research_Frontier_Round2.json",
    "ROOT_VERIFIED_M19_PROFILE_EXCLUSIONS.json", "ROOT_VERIFIED_M19_HEAVY_BUDGET_EXCLUSIONS.json",
    "ROOT_VERIFIED_M19_PRICE_EXCLUSIONS.json", "ROOT_VERIFIED_M19_QUOTA_EXCLUSIONS.json",
    "research_external/m19/sumset_resource.cpp",
    "research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/M11_DIRECTIONAL_FRONTIER.json",
    "research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json",
    "research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/halfspace_extension/M11_BOUNDED_GEOMETRIC_REDUCTION.json",
]
for s in (11,12):
    required += [f"research_external/m19/s{s}_{stem}" for stem in ("current.txt", "after_bank.txt", "quota_certificates.jsonl", "plain_certificates.jsonl", "heavy_certificates.jsonl")]
    required.append(f"frontier_audit_work/m19_lagrange/S{s}_PRICE_BANK_CERTIFICATES.jsonl")
for relative in required:
    if not (ROOT / relative).is_file():
        raise FileNotFoundError(relative)
    selected.add(relative)

files = [{"path": relative, "bytes": (ROOT / relative).stat().st_size, "sha256": sha(ROOT / relative)} for relative in sorted(selected)]
manifest = {
    "title": "Kakeya round-2 proof and verification supplement",
    "version": 1,
    "scope": "All new work with frozen prior inputs. Inherited full results are anchored to the prior checkpoint identified in the frontier.",
    "entry_point": "VERIFY_ALL.py",
    "payload_count": len(files),
    "payload_bytes": sum(row["bytes"] for row in files),
    "files": files,
}
manifest_path = ROOT / "MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
target = ROOT / "Kakeya_Research_Round2_Proofs.zip"
with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in sorted(selected | {"MANIFEST.json"}):
        archive.write(ROOT / relative, relative)
print(json.dumps({"archive": target.name, "bytes": target.stat().st_size, "sha256": sha(target), "payload_files": len(files), "payload_bytes": manifest["payload_bytes"], "manifest_sha256": sha(manifest_path)}, indent=2))
