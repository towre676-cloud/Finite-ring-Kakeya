#!/usr/bin/env python3
"""Render the frozen monograph without changing its wording or math."""
from pathlib import Path
import hashlib
import html
import json
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"Kakeya_Round7_Monograph.txt"
OUTPUT=HERE/"Kakeya_Round7_Monograph.pdf"
FONTS=Path("/usr/share/fonts/truetype/dejavu")
for name,file in [("Scholarly","DejaVuSerif.ttf"),("ScholarlyBold","DejaVuSerif-Bold.ttf"),("Heading","DejaVuSans-Bold.ttf"),("PageNumber","DejaVuSans.ttf")]:
    pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
pdfmetrics.registerFontFamily("Scholarly",normal="Scholarly",bold="ScholarlyBold")
text=SOURCE.read_text(encoding="utf-8")
assert len(text.split())==1500
plain=text.replace("**","")
missing=sorted({ord(c) for c in plain if not c.isspace() and ord(c) not in pdfmetrics.getFont("Scholarly").face.charToGlyph})
if missing:raise ValueError("Missing Unicode glyphs: "+repr(missing))
body=ParagraphStyle(
    "Body",fontName="Scholarly",fontSize=10.65,leading=15.0,
    textColor=colors.HexColor("#24282C"),alignment=TA_LEFT,
    spaceAfter=8.5,allowWidows=0,allowOrphans=0,splitLongWords=0,
)
heading=ParagraphStyle(
    "Section",parent=body,fontName="Heading",fontSize=11.6,leading=16,
    textColor=colors.HexColor("#182F40"),spaceBefore=10.5,spaceAfter=7.5,
    keepWithNext=True,
)
title=ParagraphStyle(
    "Title",parent=heading,fontSize=19.0,leading=25.5,spaceBefore=0,
    spaceAfter=18,keepWithNext=True,
)

def markup(raw):
    parts=raw.split("**")
    if len(parts)%2!=1:raise ValueError("Unbalanced bold markup")
    return "".join(("<b>"+html.escape(part)+"</b>") if i%2 else html.escape(part) for i,part in enumerate(parts))

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9DDE0"))
    canvas.setLineWidth(.45)
    canvas.line(doc.leftMargin,42,A4[0]-doc.rightMargin,42)
    canvas.setFont("PageNumber",8.5)
    canvas.setFillColor(colors.HexColor("#59636A"))
    canvas.drawCentredString(A4[0]/2,27,str(doc.page))
    canvas.restoreState()

story=[]
for index,raw in enumerate(text.strip().split("\n\n")):
    is_heading=raw.startswith("**") and raw.endswith("**") and raw.count("**")==2
    style=title if index==0 else heading if is_heading else body
    story.append(Paragraph(markup(raw.replace("\n"," ")),style))
doc=SimpleDocTemplate(
    str(OUTPUT),pagesize=A4,leftMargin=54,rightMargin=54,topMargin=51,bottomMargin=58,
    title=text.splitlines()[0].replace("**",""),
    author="",subject="Round7 monograph: the dimension-three theorem and the remaining frontier",pageCompression=1,
)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(OUTPUT)
print(json.dumps({
    "pdf":str(OUTPUT),"pages":len(reader.pages),"source_words":len(text.split()),
    "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "pdf_sha256":hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "pdf_bytes":OUTPUT.stat().st_size,"missing_glyphs":missing,
},indent=2))
