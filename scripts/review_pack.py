#!/usr/bin/env python3
"""Validate review JSON and append safe Anki TSV/reference files."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from datetime import date
from pathlib import Path

MAX_CANDIDATES = 7
SETTINGS_FILENAME = "settings.json"
ALLOWED_TYPES = {"concept", "decision", "scenario", "error-pattern"}
OPTIONAL_DETAIL_FIELDS = {"context", "explanation", "pitfall"}
DOMAIN_TAGS = {
    "robotics", "course-ai", "course-os", "course-javaee", "course-db",
    "course-se", "project-lingualoop", "project-jindian"
}


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip().lower())
    return value.strip("-") or "review"


def validate(payload: dict) -> list[str]:
    errors = []
    source = payload.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    elif source.get("kind") not in {"theory", "course", "project", "workflow"}:
        errors.append("source.kind must be theory, course, project, or workflow")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or len(candidates) > MAX_CANDIDATES:
        errors.append("candidates must contain at most 7 items")
        candidates = candidates if isinstance(candidates, list) else []
    seen = set()
    for i, card in enumerate(candidates):
        if not isinstance(card, dict):
            errors.append(f"candidate {i} must be an object")
            continue
        cid = card.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"candidate {i} needs id")
        elif cid in seen:
            errors.append(f"duplicate candidate id: {cid}")
        seen.add(cid)
        if card.get("type") not in ALLOWED_TYPES:
            errors.append(f"candidate {i} has invalid type")
        for field in ("front", "back", "reason"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                errors.append(f"candidate {i} needs non-empty {field}")
        for field in OPTIONAL_DETAIL_FIELDS:
            if field in card and not isinstance(card[field], str):
                errors.append(f"candidate {i}.{field} must be a string when provided")
        if not isinstance(card.get("tags"), list) or not card["tags"]:
            errors.append(f"candidate {i} needs tags")
        for flag in ("memory", "reference", "practice"):
            if not isinstance(card.get(flag), bool):
                errors.append(f"candidate {i}.{flag} must be boolean")
    return errors


def read_settings(root: Path) -> dict:
    path = root / SETTINGS_FILENAME
    if not path.exists():
        return {}
    settings = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(settings, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return settings


def write_settings(root: Path, runbooks_root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    settings = read_settings(root)
    settings["runbooks_root"] = str(runbooks_root)
    path = root / SETTINGS_FILENAME
    path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_runbooks_root(root: Path, override: Path | None = None) -> Path:
    configured = override or read_settings(root).get("runbooks_root")
    if not configured:
        return root / "runbooks"
    configured_path = Path(configured)
    return configured_path if configured_path.is_absolute() else root / configured_path


def html_text(value: str) -> str:
    return html.escape(value).replace("\n", "<br>")


def format_front(card: dict) -> str:
    context = card.get("context", "").strip()
    question = html_text(card["front"])
    if not context:
        return question
    return (
        f'<div class="review-context"><strong>场景</strong><br>{html_text(context)}</div>'
        f'<hr><div class="review-question">{question}</div>'
    )


def format_back(card: dict) -> str:
    sections = [
        f'<div class="review-answer"><strong>答案</strong><br>{html_text(card["back"])}</div>'
    ]
    labels = (("explanation", "为什么", "review-explanation"), ("pitfall", "注意", "review-pitfall"))
    for field, label, css_class in labels:
        value = card.get(field, "").strip()
        if value:
            sections.append(
                f'<div class="{css_class}"><strong>{label}</strong><br>{html_text(value)}</div>'
            )
    return "<br>".join(sections)


def append_outputs(
    payload: dict, root: Path, runbooks_root: Path | None = None
) -> tuple[Path, int]:
    source = payload["source"]
    stamp = source.get("date") or date.today().isoformat()
    stem = f"{stamp}-{slug(source.get('title', 'review'))}"
    reviews = root / "reviews"
    anki = root / "anki"
    runbooks = resolve_runbooks_root(root, runbooks_root)
    reviews.mkdir(parents=True, exist_ok=True)
    anki.mkdir(parents=True, exist_ok=True)
    runbooks.mkdir(parents=True, exist_ok=True)
    json_path = reviews / f"{stem}.json"
    md_path = reviews / f"{stem}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = [f"# {source.get('title', 'Review')}", "", payload.get("summary", "")]
    if payload.get("practice_prompt"):
        md_lines += ["", "## Practice", payload["practice_prompt"]]
    md_lines += ["", "## Candidates"]
    for card in payload["candidates"]:
        md_lines += [f"- **{card['type']}** {card['front']}"]
        if card.get("context"):
            md_lines.append(f"  - 场景：{card['context']}")
        md_lines.append(f"  - 答案：{card['back']}")
        if card.get("explanation"):
            md_lines.append(f"  - 为什么：{card['explanation']}")
        if card.get("pitfall"):
            md_lines.append(f"  - 注意：{card['pitfall']}")
        md_lines.append(
            f"  - memory={card['memory']} reference={card['reference']} practice={card['practice']}"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    tsv_path = anki / "AI-Learning-Review.tsv"
    added = 0
    existing = set()
    if tsv_path.exists():
        with tsv_path.open(encoding="utf-8", newline="") as f:
            existing = {row[3] for row in csv.reader(f, delimiter="\t") if len(row) >= 4}
    with tsv_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        for card in payload["candidates"]:
            if not card["memory"] or card["id"] in existing:
                continue
            tags = " ".join(card["tags"])
            writer.writerow([format_front(card), format_back(card), tags, card["id"]])
            added += 1
    if payload.get("reference_note"):
        (runbooks / f"{slug(source.get('title', 'review'))}.md").write_text(
            f"# {source.get('title', 'Review')}\n\n{payload['reference_note']}\n\nSource: {source.get('path_or_url', '')}\nDate: {stamp}\n", encoding="utf-8"
        )
    return json_path, added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, nargs="?", help="review JSON produced by ai-learning-review")
    parser.add_argument("--root", type=Path, default=Path("learning-review"), help="review root directory")
    parser.add_argument(
        "--runbooks-root", type=Path,
        help="one-off Runbook output directory; overrides saved configuration",
    )
    parser.add_argument(
        "--configure-runbooks-root", type=Path, metavar="PATH",
        help="save the default Runbook output directory in root/settings.json",
    )
    args = parser.parse_args()
    if args.configure_runbooks_root:
        settings_path = write_settings(args.root, args.configure_runbooks_root)
        print(f"saved_runbooks_root={settings_path}")
        return 0
    if args.payload is None:
        parser.error("payload is required unless --configure-runbooks-root is used")
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    path, added = append_outputs(payload, args.root, args.runbooks_root)
    print(f"saved={path}")
    print(f"anki_cards_added={added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
