import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_pipeline_state import validate


class PipelineStateTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_repository_state_is_valid(self):
        self.assertEqual(validate(self.root), [])

    def test_overlap_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            for relative in [
                "automation/pipeline_config.json",
                "automation/state.json",
                "config/registry_expectations.json",
            ]:
                source = self.root / relative
                target = temp_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            state_path = temp_root / "automation/state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["queue"].append(
                {"chapter": "CH05", "start": 150, "end": 170,
                 "branch": "translation/ch05-b0150-b0170", "status": "READY"}
            )
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertTrue(any("overlaps" in error for error in validate(temp_root)))

    def test_automatic_merge_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            for relative in [
                "automation/pipeline_config.json",
                "automation/state.json",
                "config/registry_expectations.json",
            ]:
                source = self.root / relative
                target = temp_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            state_path = temp_root / "automation/state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["merge_policy"] = "automatic"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertIn("pilot requires manual merge policy", validate(temp_root))


if __name__ == "__main__":
    unittest.main()
