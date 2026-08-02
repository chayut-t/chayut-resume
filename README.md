# chayut-resume

Resume-as-code: [`resume.md`](resume.md) is the single source of truth. Python scripts rebuild the PDF and the website from it, and GitHub Actions deploys both to GitHub Pages on every push to `main`.

**Live resume:** https://chayut-t.github.io/chayut-resume/ ([PDF](https://chayut-t.github.io/chayut-resume/resume.pdf))

## How it works

- `resume.md` — edit this file only.
- `scripts/resume_parser.py` — parses and validates the markdown (a malformed edit fails the build with a line-numbered error instead of producing a broken document).
- `scripts/build_pdf.py` — renders `dist/resume.pdf` with reportlab, matching the original resume's formatting.
- `scripts/build_html.py` — renders `dist/index.html`, the GitHub Pages front page.
- `.github/workflows/build.yml` — rebuilds and deploys on push.

Built artifacts (`dist/`) are not committed; Pages serves them.

## Editing conventions in resume.md

- `# Name`, then a contact line, then the summary paragraph.
- `## Section` for each section.
- Two-column rows: `- **left label** — text` (note the em dash `—`).
- Work experience entries: `### dates | Organization — Role`, followed by `- ` bullets.

## Build locally

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_pdf.py
.venv/bin/python scripts/build_html.py
open dist/index.html dist/resume.pdf
```
