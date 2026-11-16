---
name: resume-fit
description: >-
  Rank Sunder Thyagarajan's submitted resume PDF against a job posting, write
  a cover letter, and recommend resume edits. Generate a temporary resume
  only after the user accepts recommendations in a follow-up. Use when the
  user shares a job description or posting URL, or asks to compare, score,
  tailor, or check fit, write a cover letter, or produce an updated resume.
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

- A posting, or a request to evaluate, compare, or tailor: ranker, then cover letter. Stop before `resume-draft`.
- Rank or score only: ranker. Stop before the cover letter and `resume-draft`.
- Cover letter only: ranker, then cover letter. Stop before `resume-draft`.
- The user has already answered the recommendation loop and accepted one or more edits, or explicitly asked to generate the resume from those accepted edits: `resume-draft` only. Do not rank again unless the posting changed.

A request to tailor or update the resume is not acceptance. Show recommendations and wait.

The ranker finishes before the cover letter starts. The cover letter reads its report and does not invent a second verdict.

## Recommendation loop

After the rank report and the cover letter, present recommendations and stop. Do not create `drafts/`, do not launch `resume-draft`, and do not render a PDF.

Number every truthful rewrite from the ranker's Rewrite opportunities. For each item show the target, the current PDF sentence, the proposed sentence, and the requirement it serves. Then list gaps the ranker said wording cannot close, with no proposed sentence.

Ask which items to apply, rewrite, or drop. Wait for the user's reply.

On the next reply:

- Acceptance of specific items, or acceptance plus the user's own wording: launch `resume-draft` with only those items, using the user's wording where they changed it.
- A revision, a question, or a partial answer: update the list and ask again. Do not generate.
- Rejection of every item: do not generate a resume.

## Run

1. Extract the PDF. Choose a slug from the company and role: lowercase, hyphens, no punctuation, under 50 characters (`adobe-senior-engineering-manager`). Output directory, used only after acceptance: `drafts/<slug>/`.
2. Launch `resume-ranker`. In the prompt, include the posting, the extracted PDF text, and the PDF path. Wait.
3. Relay the ranker's report in the chat without rescoring it.
4. Launch `resume-cover-letter` unless the user asked for a rank only. Give it the posting, the extracted PDF text, and the full ranker report. Tell it to return the letter and not to write a file. Show the letter in the chat.
5. Present the recommendation list and wait.
6. After acceptance, create `drafts/<slug>/` and launch `resume-draft`. Give it the posting, the extracted PDF text, the full ranker report, the accepted items only, and the absolute paths of the output directory, `resume-print.html`, and `.cursor/skills/resume-fit/scripts/extract_pdf_text.py`.
7. Show the draft paths and the changelog. Say that `Sunder-Thyagarajan-Resume.pdf` was not replaced.

Replace the canonical PDF only when the user asks to promote a draft.
