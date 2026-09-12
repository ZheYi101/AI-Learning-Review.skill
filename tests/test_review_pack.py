from __future__ import annotations

import importlib.util
import json
import csv
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "review_pack.py"
SPEC = importlib.util.spec_from_file_location("review_pack", SCRIPT)
review_pack = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(review_pack)


def payload() -> dict:
    return {
        "source": {
            "title": "SSH Public Key Login",
            "kind": "workflow",
            "domain": "project-jindian",
            "path_or_url": "runbooks/ssh.md",
            "date": "2026-09-12",
        },
        "summary": "Verify key authentication before disabling passwords.",
        "candidates": [
            {
                "id": "ssh-key-login",
                "type": "scenario",
                "context": "You are replacing password login on a new server and must avoid locking yourself out.",
                "front": "How should key authentication be verified?",
                "back": "Test a new session before disabling passwords.",
                "explanation": "A separate session proves that the public key, file permissions, and account selection work before the fallback is removed.",
                "pitfall": "Do not copy the private key to the server or disable passwords before the new session succeeds.",
                "tags": ["domain::project-jindian", "type::scenario"],
                "memory": True,
                "reference": True,
                "practice": True,
                "reason": "Avoids a high-cost lockout.",
                "source_ref": "runbooks/ssh.md",
            }
        ],
        "reference_note": "Keep the complete validation sequence here.",
        "practice_prompt": "Name the safe order of operations.",
    }


class ReviewPackTests(unittest.TestCase):
    def test_runbook_stays_under_review_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            output_path, added = review_pack.append_outputs(payload(), root)

            self.assertEqual(added, 1)
            self.assertTrue(output_path.exists())
            self.assertTrue((root / "runbooks" / "ssh-public-key-login.md").exists())
            self.assertFalse((root.parent / "runbooks").exists())

    def test_duplicate_card_id_is_not_appended_twice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            review_pack.append_outputs(payload(), root)
            _, added = review_pack.append_outputs(payload(), root)

            self.assertEqual(added, 0)

    def test_tsv_includes_context_explanation_and_pitfall(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            review_pack.append_outputs(payload(), root)

            with (root / "anki" / "AI-Learning-Review.tsv").open(encoding="utf-8") as file:
                row = next(csv.reader(file, delimiter="\t"))
            self.assertIn("场景", row[0])
            self.assertIn("locking yourself out", row[0])
            self.assertIn("答案", row[1])
            self.assertIn("为什么", row[1])
            self.assertIn("注意", row[1])

    def test_saved_runbooks_root_can_point_to_an_external_knowledge_base(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "learning-review"
            vault_runbooks = base / "obsidian-vault" / "Runbooks"
            review_pack.write_settings(root, vault_runbooks)

            review_pack.append_outputs(payload(), root)

            self.assertTrue((vault_runbooks / "ssh-public-key-login.md").exists())
            self.assertFalse((root / "runbooks").exists())

    def test_explicit_runbooks_root_overrides_saved_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "learning-review"
            review_pack.write_settings(root, base / "saved")
            override = base / "override"

            review_pack.append_outputs(payload(), root, override)

            self.assertTrue((override / "ssh-public-key-login.md").exists())
            self.assertFalse((base / "saved").exists())


if __name__ == "__main__":
    unittest.main()
