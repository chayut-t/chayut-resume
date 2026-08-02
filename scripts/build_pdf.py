"""Build dist/resume.pdf from resume.md, matching the original resume's look:

Times-Roman name header, Helvetica body, bold serif section titles over a
thin rule, a narrow left column for dates/labels, and italic bullets for
work-experience entries. All content flows through Platypus paragraphs and
tables, so long edits wrap and paginate instead of breaking the layout.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, str(Path(__file__).parent))
from resume_parser import LINK_RE, Resume, Section, parse_resume

MARGIN = 0.75 * inch
BODY_WIDTH = letter[0] - 2 * MARGIN
LEFT_COL = 80  # pt, the dates/labels column
RIGHT_COL = BODY_WIDTH - LEFT_COL

STYLES = {
    "name": ParagraphStyle("name", fontName="Times-Roman", fontSize=18, leading=22, spaceAfter=4),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9, leading=12, spaceAfter=10),
    "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=9, leading=12.5),
    "section": ParagraphStyle(
        "section", fontName="Times-Bold", fontSize=11.5, leading=14, spaceBefore=12, spaceAfter=1
    ),
    "left": ParagraphStyle("left", fontName="Helvetica", fontSize=9, leading=12),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12),
    "bullet": ParagraphStyle(
        "bullet",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=11.5,
        alignment=TA_LEFT,
        leftIndent=8,
        firstLineIndent=-8,
    ),
}


def md(text: str) -> str:
    """Markdown links -> reportlab inline markup; everything else escaped."""
    out: list[str] = []
    pos = 0
    for m in LINK_RE.finditer(text):
        out.append(escape(text[pos : m.start()]))
        out.append(
            f'<a href="{escape(m.group("url"))}" color="#1a0dab"><u>{escape(m.group("label"))}</u></a>'
        )
        pos = m.end()
    out.append(escape(text[pos:]))
    return "".join(out)


TABLE_STYLE = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 6),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]
)


def section_flowables(section: Section) -> list:
    flow: list = [
        Paragraph(md(section.title), STYLES["section"]),
        HRFlowable(width="100%", thickness=0.6, color=colors.grey, spaceAfter=5),
    ]

    data: list[list] = []
    spans: list[tuple] = []
    for row in section.rows:
        if row.left:
            data.append([Paragraph(md(row.left), STYLES["left"]), Paragraph(md(row.text), STYLES["body"])])
        else:
            # Label-less rows (publications etc.) run full-width from the
            # left margin, as in the original resume.
            r = len(data)
            spans.append(("SPAN", (0, r), (1, r)))
            spans.append(("BOTTOMPADDING", (0, r), (1, r), 4))
            data.append([Paragraph(md(row.text), STYLES["body"]), ""])

    for entry in section.entries:
        data.append([Paragraph(md(entry.dates), STYLES["left"]), Paragraph(md(entry.heading), STYLES["body"])])
        for bullet in entry.bullets:
            data.append(["", Paragraph(f"-  {md(bullet)}", STYLES["bullet"])])

    style = TableStyle(TABLE_STYLE.getCommands() + spans)
    table = Table(data, colWidths=[LEFT_COL, RIGHT_COL], style=style)
    flow.append(table)
    return flow


def build(resume: Resume, out_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{resume.name} - Resume",
        author=resume.name,
    )
    story: list = [
        Paragraph(md(resume.name), STYLES["name"]),
        Paragraph(md(resume.contact), STYLES["contact"]),
        Paragraph(md(resume.summary), STYLES["summary"]),
        Spacer(1, 2),
    ]
    for section in resume.sections:
        story.extend(section_flowables(section))
    doc.build(story)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "dist"
    out_dir.mkdir(exist_ok=True)
    resume = parse_resume(root / "resume.md")
    build(resume, out_dir / "resume.pdf")
    print(f"wrote {out_dir / 'resume.pdf'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
