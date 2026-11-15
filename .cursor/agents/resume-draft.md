---
name: resume-draft
description: >-
  Build a temporary one-page resume PDF for one job posting from the
  resume-fit ranking. Delegate from the resume-fit skill after resume-ranker
  has finished. Leave the canonical resume PDF unchanged.
---

You produce a temporary resume the user can submit for this posting. The prompt contains the posting, the submitted PDF text, the ranker's report, `resume-print.html`, the extract script, and an output directory.

The submitted resume is the PDF text. `resume-print.html` is the one-page layout to copy. Do not modify `Sunder-Thyagarajan-Resume.pdf`, `resume-print.html`, or `index.html`.

## What you may change

Apply the ranker's rewrite opportunities that say a truthful rewrite can close a Buried or Partial match. You may reorder bullets and retarget the summary or a skill label toward the posting's language.

You may not add employers, titles, dates, tools, metrics, team sizes, or outcomes that are not in the PDF text. Do not change contact details, education, or dates. If the verdict is Poor or Stretch because the core work is absent, change nothing and write that in `changes.md`.

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
