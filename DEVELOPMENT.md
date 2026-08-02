# Development guide

Instructions for updating this resume, written for future Claude Code sessions (and humans).

## Architecture

`resume.md` is the **single source of truth**. Never edit generated output directly.

```
resume.md ──> scripts/resume_parser.py ──┬──> scripts/build_pdf.py  ──> dist/resume.pdf
             (parses + validates)        └──> scripts/build_html.py ──> dist/index.html
```

- `dist/` is gitignored; nothing generated is committed.
- On every push to `main`, GitHub Actions (`.github/workflows/build.yml`) rebuilds both
  outputs and deploys `dist/` to GitHub Pages:
  - Site: https://chayut-t.github.io/chayut-resume/
  - PDF: https://chayut-t.github.io/chayut-resume/resume.pdf
- If a build fails (e.g. malformed markdown), the Actions run goes red and Pages keeps
  serving the last good version.

## Privacy rules (critical)

This is a **public** repo. Phone number, personal email, and current location must NEVER
appear in any tracked file or generated output. Contact info is the LinkedIn link only.

- `legacy/` holds the original PDF **with** private contact info. It is gitignored and
  chmod 444. Never `git add -f` it, never loosen `.gitignore`.
- Before committing, run `scripts/check_pii.sh` — it must print "PII scan clean".
  The scan patterns are themselves private, so they live in `.pii-patterns` (gitignored,
  one regex per line, local machine only — never commit it or paste its contents into
  any tracked file, commit message, or PR). If `.pii-patterns` is missing, ask the user
  to recreate it; the private values can be recovered from `legacy/resume_20260311.pdf`.

## Editing resume.md

The parser (`scripts/resume_parser.py`) enforces this structure and fails with a
line-numbered error on violations:

- `# Name` — exactly one, first.
- One plain line under the name = contact line; following plain lines = summary paragraph.
- `## Section Title` for each section.
- Two-column rows (dates/labels left, text right):
  `- **8/09-5/16** — text here` — bold left label, then space + em dash (`—`, not `-`) + space.
- Plain full-width rows (used for publications): `- text here`.
- Work-experience entries:
  `### 1/22-Present | Organization — Role` (pipe separates dates from heading),
  followed by plain `- ` bullets (rendered italic).
- Markdown links `[label](url)` work everywhere and become real links in PDF and HTML.
- No free text inside sections; no `####` or deeper headings.

Writing style: bullets start with a past-tense action verb (Developed, Built, Improved…),
one sentence, often ending with an outcome clause.

## Build and verify locally

```sh
# one-time setup
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# rebuild
.venv/bin/python scripts/build_pdf.py
.venv/bin/python scripts/build_html.py
```

Then Read `dist/resume.pdf` (Claude Code can render PDFs) and check:
- dates column aligns flush with section headers,
- text wraps inside its column, no overlap/clipping,
- page count is sane (currently 2 pages).

## Deploy

Commit + push to `main`. Then:

```sh
gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId') --exit-status
curl -sI https://chayut-t.github.io/chayut-resume/ | head -1   # expect 200
```

The Pages CDN can serve a stale file for a minute or two after deploy. Note: rebuilt PDFs
never byte-match (reportlab embeds a timestamp) — compare visually, not with `cmp`.

## Gotchas

- `build_pdf.py` uses a zero-padding `Frame` with `BaseDocTemplate` on purpose:
  `SimpleDocTemplate`'s default 6pt frame padding misaligns full-width tables with
  paragraphs (dates column sticks out left of section headers). Don't "simplify" it back.
- Label-less rows render full-width in the PDF via table SPAN commands, matching the
  original resume's publication layout.
- Layout constants (fonts, sizes, column width) live at the top of `build_pdf.py`
  (`STYLES`, `LEFT_COL`, `MARGIN`); the HTML equivalents are in `CSS` in `build_html.py`.
  Keep the two visually in sync when changing one.
