#!/usr/bin/env python3
"""Bind the previously visually checked report to its exact1500-word source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round8"
qa = json.loads((HERE / "MONOGRAPH_PDF_QA.json").read_text())
assert qa["status"] == "PASS_EXACT_1500_WORD_TEXT_AND_THREE_PAGE_VISUAL_QA"
source, pdf = ROOT / qa["source"], ROOT / qa["pdf"]
assert hashlib.sha256(source.read_bytes()).hexdigest() == qa["source_sha256"]
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == qa["pdf_sha256"]
text = source.read_text().replace("**", "")
text = "\n".join(line[2:] if line.startswith("# ") else line for line in text.splitlines())
assert len(text.split()) == qa["rendered_words_including_title"] == 1500
assert qa["pages"] == 3 and qa["pdf_text_exactly_matches_source"] is True
assert qa["visual_pages_inspected"] == [1, 2, 3] and qa["visual_defects_observed"] == []
print(json.dumps({"status": "PASS_BOUND_VISUALLY_CHECKED_MONOGRAPH", "words": 1500, "pages": 3}, indent=2))
