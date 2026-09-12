# AI Learning Review

A Codex skill for turning AI-assisted study and project sessions into a small, searchable review queue and Anki-importable cards. It keeps durable ideas, decisions, and troubleshooting patterns without turning chat logs into a card backlog.

It is deliberately separate from language-learning and media-card workflows.

## What It Produces

- At most 3-7 high-value review candidates per session.
- Anki TSV rows for one `AI Learning Review` deck, organized with tags.
- Searchable Markdown/JSON session records and optional runbooks.
- One short scenario prompt to practice transfer, not just recall.

The default schedule is intentionally small: up to 12 minutes of Anki plus a 3-minute scenario prompt each day.

## Install

Copy or clone this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\ai-learning-review "$env:USERPROFILE\.agents\skills\ai-learning-review"
```

Then use it at the end of a study session:

```text
Use ai-learning-review to organize this session.
Source type: course
Domain: course-os
Keep only high-value, reusable items. Return at most 3-7 candidates.
```

## Export To Anki

Save the Skill's JSON response as `review.json`, then run:

```powershell
python .\scripts\review_pack.py .\review.json --root .\learning-review
```

Import `learning-review/anki/AI-Learning-Review.tsv` into Anki using Tab separation and the fields `Front`, `Back`, `Tags`, and `Source`.

## Scope

Suitable for theory, university courses, project decisions, and reusable workflows. It does not process language-learning cards, vocabulary, or video/audio media.
