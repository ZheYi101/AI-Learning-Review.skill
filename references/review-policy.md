# Review Policy

Use this reference when deciding whether a session finding should become a card, a searchable reference, or a practice prompt.

## Memory

Recommend `memory=true` only when the item is stable, likely to recur, and costly or risky to rediscover. Good candidates are causal models, decision cues, common diagnostic branches, and compact comparisons.

Reject items that are one-off paths, volatile flags, copied code, full procedures, unverified conclusions, or facts that can be recovered cheaply through search.

## Reference

Recommend `reference=true` for exact commands, version-specific details, complete runbooks, project context, and safety notes. Preserve the source path or URL and the date so future readers can judge freshness.

Runbooks belong in the user's chosen knowledge base, not necessarily beside review data. The default is `learning-review/runbooks/`; use the saved `runbooks_root` configuration when the user has explicitly chosen another location, such as an Obsidian Vault. Never infer an external path.

## Practice

Recommend `practice=true` when recall alone would not test the desired capability. Prefer one bounded scenario that asks for a choice, an ordering, a verification step, or a diagnostic branch. Keep it answerable within three minutes.

## Review Unit

Each session produces an episode capsule plus a small candidate list. The capsule restores the learning episode in Markdown/Runbook; it is not a daily Anki field.

## Card Construction

- `atomic` is the default and should retrieve one claim, distinction, or action. It may have one short `cue` only when the cue changes which answer is correct.
- `case` is a minority tier for decisions, diagnosis, safety, or ordering. Use 2-4 sentences with 3-5 discriminative conditions, then ask for the next action, order, diagnosis, or evidence.
- A case card must include a `verification` signal. It is not successful if the learner only recognizes the story.
- Put the short, checkable answer first; add `explanation` only for a causal model or key distinction.
- Add `pitfall` only for a likely misconception, dangerous action, or meaningful boundary.
- Use `type::concept`, `type::decision`, `type::scenario`, or `type::error-pattern` plus an automatic `mode::atomic` or `mode::case` tag.
- Give each card a stable `id`; reuse it to prevent duplicate TSV rows.
- Remove, pause, split, or rewrite cards that repeatedly fail.

## Daily Budget

The workflow is capped at twelve minutes of atomic Anki review plus three minutes for at most one case card. Do not catch up a backlog in one sitting. The system succeeds only if the budget is sustainable.
