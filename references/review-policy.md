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

## Card Construction

- Write a 1-3 sentence `context` that restores the concrete task, goal, and decision point without giving away the answer.
- Ask one question with a concrete retrieval target after the context.
- Put the short, checkable answer first; then add an `explanation` for the causal model or key distinction.
- Add a `pitfall` only for a likely misconception, dangerous action, or meaningful boundary.
- Keep the answer itself short enough to check in roughly ten seconds. Context and explanation may be longer, but must not become a tutorial.
- Use `type::concept`, `type::decision`, `type::scenario`, or `type::error-pattern`.
- Give each card a stable `id`; reuse it to prevent duplicate TSV rows.
- Remove, pause, split, or rewrite cards that repeatedly fail.

## Daily Budget

The workflow is capped at twelve minutes of Anki plus three minutes of application review. Do not catch up a backlog in one sitting. The system succeeds only if the budget is sustainable.
