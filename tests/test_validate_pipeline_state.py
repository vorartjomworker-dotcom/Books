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
            self.assertIn("manual merge policy is required", validate(temp_root))


    def test_mode_mismatch_is_rejected(self):
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
            state["mode"] = "pilot" if state["mode"] == "autonomous" else "autonomous"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertIn("config and state modes must match", validate(temp_root))

    def test_autonomous_requires_auto_advance(self):
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
            config_path = temp_root / "automation/pipeline_config.json"
            state_path = temp_root / "automation/state.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            state = json.loads(state_path.read_text(encoding="utf-8"))
            config["mode"] = state["mode"] = "autonomous"
            config["auto_advance"] = state["auto_advance"] = False
            config_path.write_text(json.dumps(config), encoding="utf-8")
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertIn("autonomous mode requires auto_advance", validate(temp_root))


    def test_parallel_slots_are_five_chapters(self):
        config = json.loads((self.root / "automation/pipeline_config.json").read_text(encoding="utf-8"))
        state = json.loads((self.root / "automation/state.json").read_text(encoding="utf-8"))
        self.assertEqual(config["max_parallel_chapters"], 5)
        self.assertEqual(
            set(state["active_by_chapter"]),
            {"CH05", "CH06", "CH07", "CH08", "CH09"},
        )

    def test_parallel_slot_chapter_mismatch_is_rejected(self):
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
            state["active_by_chapter"]["CH05"]["chapter"] = "CH06"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertTrue(any("chapter does not match slot" in error for error in validate(temp_root)))

    def test_translation_auto_merge_is_rejected(self):
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
            config_path = temp_root / "automation/pipeline_config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["translation_merge_to_main"] = True
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertTrue(any("must not merge automatically" in error for error in validate(temp_root)))


if __name__ == "__main__":
    unittest.main()
