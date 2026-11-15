---
name: resume-fit
description: >-
  Rank Sunder Thyagarajan's submitted resume PDF against a job posting, then
  draft a cover letter and a temporary one-page resume. Use when the user
  shares a job description or posting URL, or asks to compare, score, tailor,
  or check fit, write a cover letter, or produce an updated resume for a role.
---

# Resume fit

Coordinate three project subagents. Do not rank the posting, write the cover letter, or edit a resume yourself. Pass each subagent the full text it needs. A subagent does not see this conversation.

| Agent | File | Job |
| --- | --- | --- |
| `resume-ranker` | `.cursor/agents/resume-ranker.md` | Rank the submitted PDF against the posting |
| `resume-cover-letter` | `.cursor/agents/resume-cover-letter.md` | Write the cover letter from that ranking |
| `resume-draft` | `.cursor/agents/resume-draft.md` | Write a temporary one-page resume PDF |

Launch them with the Task tool. Set `subagent_type` to the agent name. If that name is rejected, rerun once with `subagent_type` `generalPurpose` and include the agent file plus the same inputs in the prompt.

## Submitted resume

The resume that will be submitted is `Sunder-Thyagarajan-Resume.pdf`. Extract it before launching anyone:

```bash
python3 .cursor/skills/resume-fit/scripts/extract_pdf_text.py Sunder-Thyagarajan-Resume.pdf
```

Rank and quote from that text. If extraction fails, stop and ask for the resume text. Do not substitute `index.html` or `resume-print.html` as the resume. `resume-print.html` is only the print template the draft agent copies. Leave these files unchanged:

- `Sunder-Thyagarajan-Resume.pdf`
- `resume-print.html`
- `index.html`

## Posting

1. Pasted text or a file in the conversation: use that text.
2. A URL: fetch the page and keep the title, company, location, employment type, responsibilities, and qualifications. Drop navigation, ads, and equal-opportunity boilerplate.
3. Fetch failed, login wall, or the posting is missing: ask for the description. Do not rank from a partial page.

## Which agents to run

- A posting, or a request to evaluate, compare, or tailor: ranker, then cover letter and draft together.
- Rank or score only: ranker.
- Cover letter only: ranker, then cover letter.
- Updated or tailored resume only: ranker, then draft.

The ranker finishes before the other two start. They read its report and do not invent a second verdict.

## Run

1. Extract the PDF. Choose a slug from the company and role: lowercase, hyphens, no punctuation, under 50 characters (`adobe-senior-engineering-manager`). Output directory: `drafts/<slug>/`.
2. Launch `resume-ranker`. In the prompt, include the posting, the extracted PDF text, and the PDF path. Wait.
3. Relay the ranker's report in the chat without rescoring it.
4. Create `drafts/<slug>/`.
5. In one message, launch `resume-cover-letter` and `resume-draft` together. Give each the posting, the extracted PDF text, the full ranker report, and the absolute output directory. Also give the draft agent the absolute path of `resume-print.html` and of `.cursor/skills/resume-fit/scripts/extract_pdf_text.py`.
6. After both return, show the cover letter and the draft paths. Say that `Sunder-Thyagarajan-Resume.pdf` was not replaced.

Replace the canonical PDF only when the user asks to promote a draft.
