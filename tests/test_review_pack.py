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
        "episode_capsule": {
            "situation": "A new server still accepts password login.",
            "goal": "Switch safely to public-key authentication.",
            "turning_point": "A second session must succeed before fallback is removed.",
            "next_time": "Start by checking the account and public-key path.",
        },
        "candidates": [
            {
                "id": "ssh-key-login",
                "type": "scenario",
                "review_level": "case",
                "context": "You are replacing password login on a new server and must avoid locking yourself out.",
                "front": "How should key authentication be verified?",
                "back": "Test a new session before disabling passwords.",
                "explanation": "A separate session proves that the public key, file permissions, and account selection work before the fallback is removed.",
                "pitfall": "Do not copy the private key to the server or disable passwords before the new session succeeds.",
                "verification": "The second session connects with the key while the original session remains available.",
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
            self.assertIn("验证", row[1])
            self.assertIn("mode::case", row[2])

    def test_atomic_card_stays_compact_and_uses_a_short_cue(self) -> None:
        atomic = {
            "source": payload()["source"],
            "summary": "Remember the stable key locations.",
            "candidates": [{
                "id": "ssh-key-location",
                "type": "concept",
                "review_level": "atomic",
                "cue": "When setting up key authentication on a familiar Linux account.",
                "front": "Where does each SSH key belong?",
                "back": "Keep the private key on the client; put the public key in the target account's authorized_keys.",
                "tags": ["domain::project-jindian", "type::concept"],
                "memory": True,
                "reference": False,
                "practice": False,
                "reason": "Stable boundary worth fast recall.",
                "source_ref": "runbooks/ssh.md",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            review_pack.append_outputs(atomic, root)
            with (root / "anki" / "AI-Learning-Review.tsv").open(encoding="utf-8") as file:
                row = next(csv.reader(file, delimiter="\t"))
            self.assertIn("使用线索", row[0])
            self.assertNotIn("场景", row[0])
            self.assertNotIn("为什么", row[1])
            self.assertIn("mode::atomic", row[2])

    def test_episode_capsule_is_saved_without_becoming_an_anki_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            output_path, _ = review_pack.append_outputs(payload(), root)

            review_text = output_path.with_suffix(".md").read_text(encoding="utf-8")
            tsv_text = (root / "anki" / "AI-Learning-Review.tsv").read_text(encoding="utf-8")
            self.assertIn("Episode Capsule", review_text)
            self.assertIn("下次入口", review_text)
            self.assertNotIn("A new server still accepts password login.", tsv_text)

    def test_explicit_case_cards_require_context_and_verification(self) -> None:
        invalid = payload()
        invalid["candidates"][0].pop("context")
        invalid["candidates"][0].pop("verification")

        errors = review_pack.validate(invalid)

        self.assertIn("candidate 0 case cards need context", errors)
        self.assertIn("candidate 0 case cards need verification", errors)

    def test_only_one_explicit_case_card_is_allowed(self) -> None:
        invalid = payload()
        second = dict(invalid["candidates"][0])
        second["id"] = "second-case"
        invalid["candidates"].append(second)

        errors = review_pack.validate(invalid)

        self.assertIn("at most one explicit case card is allowed per review unit", errors)

    def test_no_reference_note_does_not_create_a_runbook_directory(self) -> None:
        payload_without_reference = payload()
        payload_without_reference["reference_note"] = ""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "learning-review"
            review_pack.append_outputs(payload_without_reference, root)

            self.assertFalse((root / "runbooks").exists())

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
