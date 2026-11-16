---
name: resume-draft
description: >-
  Build a temporary one-page resume PDF from resume edits the user already
  accepted. Delegate from the resume-fit skill only after that acceptance.
  Leave the canonical resume PDF unchanged. Do not run from a ranking alone.
---

You produce a temporary resume the user can submit for this posting. The prompt contains the posting, the submitted PDF text, the ranker's report, `resume-print.html`, the extract script, and an output directory.

The submitted resume is the PDF text. `resume-print.html` is the one-page layout to copy. Do not modify `Sunder-Thyagarajan-Resume.pdf`, `resume-print.html`, or `index.html`.

## What you may change

Apply only the accepted recommendations in the prompt. Use the user's wording when they rewrote an item. Leave every other sentence as it is on the PDF.

You may not add employers, titles, dates, tools, metrics, team sizes, or outcomes that are not in the PDF text. Do not change contact details, education, or dates. If the prompt has no accepted recommendations, write no files and say the user has not accepted a resume yet.

## Files

1. Copy `resume-print.html` to `<output directory>/resume.html`.
2. Edit the text in that copy. Keep its CSS and structure so it still prints as one page.
3. Render:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="<output directory>/Sunder-Thyagarajan-Resume.pdf" \
  "file://<absolute resume.html>"
```

If the sandbox blocks Chrome, rerun that command with full permissions.

4. Confirm one page:

```bash
python3 <extract script> "<output directory>/Sunder-Thyagarajan-Resume.pdf"
```

The first line must be `pages: 1`. If it is more than one page, cut detail from roles before Adobe and render again. Do not shrink the template's font sizes.

5. Write `<output directory>/changes.md`:

```markdown
# Temporary resume

Canonical PDF was not changed.

| Section | Now | Proposed | Serves |
| --- | --- | --- | --- |
| ... | quote | replacement | requirement |

pages: 1
```

If nothing changed, say so and still write the copied PDF so the folder is complete.

Return the three paths and the changelog table. Do not claim the canonical resume was updated.
