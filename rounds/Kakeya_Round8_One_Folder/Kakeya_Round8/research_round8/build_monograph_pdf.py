#!/usr/bin/env python3
"""Render the exact1500-word Round8 account; layout QA is recorded separately."""
from html import escape
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pdfplumber
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "Round8_Monograph_1500.md"
OUTPUT = HERE / "Round8_Monograph_1500.pdf"
QA = ROOT / "tmp/pdfs/round8"


def markup(text):
    parts = re.split(r"(\*\*.*?\*\*)", text)
    return "".join("<b>" + escape(p[2:-2]) + "</b>" if p.startswith("**")
                   else escape(p) for p in parts)


def main():
    source = SOURCE.read_text()
    chunks = source.strip().split("\n\n")
    title = chunks[0].removeprefix("# ")
    plain = "\n\n".join([title] + chunks[1:]).replace("**", "")
    assert len(plain.split()) == 1500
    assert len(chunks[1:]) == 16
    fontdir = Path("/usr/share/fonts/truetype/dejavu")
    pdfmetrics.registerFont(TTFont("R8Serif", str(fontdir / "DejaVuSerif.ttf")))
    pdfmetrics.registerFont(TTFont("R8SerifBold", str(fontdir / "DejaVuSerif-Bold.ttf")))
    pdfmetrics.registerFontFamily("R8Serif", normal="R8Serif", bold="R8SerifBold",
                                 italic="R8Serif", boldItalic="R8SerifBold")
    body = ParagraphStyle("body", fontName="R8Serif", fontSize=10, leading=14.2,
                          textColor=colors.HexColor("#17232c"), spaceAfter=9,
                          splitLongWords=False, allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("heading", parent=body, fontName="R8SerifBold",
                             fontSize=19, leading=24, spaceAfter=18,
                             textColor=colors.HexColor("#153d47"))
    w, h = A4

    def decoration(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#55707a"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(53, h - 31, "KAKEYA RESEARCH  /  ROUND 8")
        canvas.drawRightString(w - 53, h - 31, "29 OCTOBER 2026")
        canvas.setStrokeColor(colors.HexColor("#cbd8db"))
        canvas.setLineWidth(.6)
        canvas.line(53, h - 40, w - 53, h - 40)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(53, 31, "1500 words including the title  |  Current theorem scope and remaining work")
        canvas.drawRightString(w - 53, 31, str(doc.page))
        canvas.restoreState()

    story = [Paragraph(markup(title), heading)]
    for number, paragraph in enumerate(chunks[1:], 1):
        story.append(Paragraph(markup(paragraph), body))
        if number in (5, 11):
            story.append(PageBreak())
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=53, rightMargin=53,
                                 topMargin=57, bottomMargin=52,
                                 title=title, author="Kakeya research checkpoint")
    document.build(story, onFirstPage=decoration, onLaterPages=decoration)
    with pdfplumber.open(OUTPUT) as pdf:
        extracted = "\n".join(page.crop((50, 50, w - 50, h - 48)).extract_text()
                               for page in pdf.pages)
        page_count = len(pdf.pages)
    assert page_count == 3, page_count
    assert len(extracted.split()) == 1500, len(extracted.split())
    assert " ".join(extracted.split()) == " ".join(plain.split()), "PDF text differs from the exact source"
    QA.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", "100", "-png", str(OUTPUT), str(QA / "page")], check=True)
    receipt = {"status": "PASS_TEXT_AND_PAGE_COUNT_PENDING_VISUAL_QA",
               "source": str(SOURCE.relative_to(ROOT)), "pdf": str(OUTPUT.relative_to(ROOT)),
               "rendered_words_including_title": 1500, "pages": page_count,
               "pdf_text_exactly_matches_source": True,
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "pdf_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
               "authoring_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "page_pngs": [str(p) for p in sorted(QA.glob("page-*.png"))]}
    (HERE / "MONOGRAPH_PDF_QA.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
