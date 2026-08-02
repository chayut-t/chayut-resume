"""Parse resume.md (the source of truth) into a structured document.

Both build_pdf.py and build_html.py consume the structure returned by
parse_resume(), so the two outputs can never drift apart.

Expected markdown structure (validated; a violation raises ResumeParseError
with the offending line number):

    # Name
    <contact line(s): plain text with optional [label](url) links>
    <summary paragraph(s)>

    ## Section title
    - **left column** — right column        (two-column rows)
    - plain bullet                          (full-width rows)

    ## Section title
    ### date-range | Organization — Role    (work-experience entry)
    - bullet
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class ResumeParseError(Exception):
    def __init__(self, line_no: int, message: str):
        super().__init__(f"resume.md line {line_no}: {message}")
        self.line_no = line_no


@dataclass
class Row:
    """One bullet in a section: optional bold left column + text."""

    left: str  # "" for plain bullets
    text: str


@dataclass
class Entry:
    """A work-experience entry: '### dates | heading' plus its bullets."""

    dates: str
    heading: str
    bullets: list[str] = field(default_factory=list)


@dataclass
class Section:
    title: str
    rows: list[Row] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)


@dataclass
class Resume:
    name: str
    contact: str
    summary: str
    sections: list[Section] = field(default_factory=list)


ROW_RE = re.compile(r"^- \*\*(?P<left>.+?)\*\*\s+—\s+(?P<text>.+)$")
PLAIN_ROW_RE = re.compile(r"^- (?P<text>.+)$")
ENTRY_RE = re.compile(r"^### (?P<dates>.+?)\s*\|\s*(?P<heading>.+)$")


def parse_resume(path: str | Path) -> Resume:
    lines = Path(path).read_text(encoding="utf-8").splitlines()

    name = ""
    contact_parts: list[str] = []
    summary_parts: list[str] = []
    sections: list[Section] = []
    section: Section | None = None
    entry: Entry | None = None

    for line_no, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if not line.strip():
            continue

        if line.startswith("# ") and not line.startswith("## "):
            if name:
                raise ResumeParseError(line_no, "second '# ' heading; only one name heading is allowed")
            name = line[2:].strip()
            continue

        if line.startswith("## ") and not line.startswith("### "):
            section = Section(title=line[3:].strip())
            if not section.title:
                raise ResumeParseError(line_no, "empty section title")
            sections.append(section)
            entry = None
            continue

        if line.startswith("### "):
            if section is None:
                raise ResumeParseError(line_no, "'### ' entry before any '## ' section")
            m = ENTRY_RE.match(line)
            if not m:
                raise ResumeParseError(
                    line_no, "entry heading must look like '### dates | Organization — Role'"
                )
            entry = Entry(dates=m.group("dates").strip(), heading=m.group("heading").strip())
            section.entries.append(entry)
            continue

        if line.startswith("- "):
            if section is None:
                raise ResumeParseError(line_no, "bullet before any '## ' section")
            if entry is not None:
                entry.bullets.append(PLAIN_ROW_RE.match(line).group("text").strip())
                continue
            m = ROW_RE.match(line)
            if m:
                section.rows.append(Row(left=m.group("left").strip(), text=m.group("text").strip()))
            else:
                section.rows.append(Row(left="", text=PLAIN_ROW_RE.match(line).group("text").strip()))
            continue

        if line.startswith("#"):
            raise ResumeParseError(line_no, f"unsupported heading level: {line.split(' ')[0]!r}")

        # Plain text before the first section: contact line(s), then summary.
        if section is not None:
            raise ResumeParseError(
                line_no,
                "free text inside a section; use '- ' bullets or '### ' entries",
            )
        if not name:
            raise ResumeParseError(line_no, "text before the '# Name' heading")
        if not contact_parts:
            contact_parts.append(line.strip())
        else:
            summary_parts.append(line.strip())

    if not name:
        raise ResumeParseError(1, "missing '# Name' heading")
    if not contact_parts:
        raise ResumeParseError(1, "missing contact line under the name")
    if not summary_parts:
        raise ResumeParseError(1, "missing summary paragraph")
    if not sections:
        raise ResumeParseError(1, "no '## ' sections found")
    for s in sections:
        if not s.rows and not s.entries:
            raise ResumeParseError(1, f"section '{s.title}' is empty")

    return Resume(
        name=name,
        contact=" ".join(contact_parts),
        summary=" ".join(summary_parts),
        sections=sections,
    )


LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<url>[^)\s]+)\)")


def links_to_html(text: str) -> str:
    """Convert markdown links to <a> tags, escaping everything else."""
    import html

    out: list[str] = []
    pos = 0
    for m in LINK_RE.finditer(text):
        out.append(html.escape(text[pos : m.start()]))
        out.append(f'<a href="{html.escape(m.group("url"), quote=True)}">{html.escape(m.group("label"))}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)
