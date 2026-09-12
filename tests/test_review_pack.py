from __future__ import annotations

import importlib.util
import json
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
                "front": "How should key authentication be verified?",
                "back": "Test a new session before disabling passwords.",
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


if __name__ == "__main__":
    unittest.main()
