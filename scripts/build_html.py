"""Build dist/index.html from resume.md — the GitHub Pages front page.

Mirrors the PDF's structure (serif name, ruled section titles, dates in a
left column, italic work bullets) as a responsive, print-friendly page with
a download link to resume.pdf.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from resume_parser import Resume, Section, links_to_html, parse_resume

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem 1rem; background: #e9e7e2;
  font: 15px/1.55 Helvetica, Arial, sans-serif; color: #1d1d1f;
}
.page {
  max-width: 850px; margin: 0 auto; background: #fff;
  padding: clamp(1.5rem, 5vw, 4rem); box-shadow: 0 1px 8px rgba(0,0,0,.15);
}
h1 { font: 400 2.1rem/1.2 Times, 'Times New Roman', serif; margin: 0 0 .3rem; }
.contact { margin: 0 0 1.2rem; font-size: .92rem; color: #444; }
.summary { margin: 0 0 1.4rem; }
h2 {
  font: 700 1.05rem/1.3 Times, 'Times New Roman', serif; margin: 1.6rem 0 .2rem;
  padding-bottom: .25rem; border-bottom: 1px solid #999;
}
a { color: #1a0dab; }
.row { display: grid; grid-template-columns: 7.5em 1fr; gap: .25rem 1rem; margin-top: .55rem; }
.row .dates { color: #555; font-size: .92rem; white-space: nowrap; }
.row.plain { grid-template-columns: 1fr; }
ul.bullets { margin: .25rem 0 0; padding-left: 1.1rem; font-style: italic; color: #333; }
ul.bullets li { margin: .2rem 0; }
.download {
  display: inline-block; margin: 0 0 1.4rem; padding: .45rem .9rem;
  border: 1px solid #1a0dab; border-radius: 4px; font-size: .9rem;
  text-decoration: none;
}
.download:hover { background: #1a0dab; color: #fff; }
@media (max-width: 560px) { .row { grid-template-columns: 1fr; gap: 0 } .row .dates { font-weight: 600 } }
@media print {
  body { background: #fff; padding: 0; font-size: 11px; }
  .page { box-shadow: none; padding: 0; max-width: none; }
  .download { display: none; }
}
"""


def section_html(section: Section) -> str:
    parts = [f"<h2>{links_to_html(section.title)}</h2>"]

    for row in section.rows:
        if row.left:
            parts.append(
                f'<div class="row"><div class="dates">{links_to_html(row.left)}</div>'
                f"<div>{links_to_html(row.text)}</div></div>"
            )
        else:
            parts.append(f'<div class="row plain"><div>{links_to_html(row.text)}</div></div>')

    for entry in section.entries:
        bullets = "".join(f"<li>{links_to_html(b)}</li>" for b in entry.bullets)
        parts.append(
            f'<div class="row"><div class="dates">{links_to_html(entry.dates)}</div>'
            f"<div><strong>{links_to_html(entry.heading)}</strong>"
            f'<ul class="bullets">{bullets}</ul></div></div>'
        )

    return "\n".join(parts)


def build(resume: Resume) -> str:
    sections = "\n".join(section_html(s) for s in resume.sections)
    name = html.escape(resume.name)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Resume</title>
<meta name="description" content="Resume of {name}">
<style>{CSS}</style>
</head>
<body>
<main class="page">
  <h1>{name}</h1>
  <p class="contact">{links_to_html(resume.contact)}</p>
  <a class="download" href="resume.pdf">Download PDF</a>
  <p class="summary">{links_to_html(resume.summary)}</p>
{sections}
</main>
</body>
</html>
"""


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "dist"
    out_dir.mkdir(exist_ok=True)
    resume = parse_resume(root / "resume.md")
    (out_dir / "index.html").write_text(build(resume), encoding="utf-8")
    print(f"wrote {out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
