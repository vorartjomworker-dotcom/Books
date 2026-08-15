from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook


PROJECT = Path(__file__).resolve().parents[1]
VALIDATOR = PROJECT / "scripts" / "validate_registries.py"
CONFIG = json.loads((PROJECT / "config" / "registry_expectations.json").read_text(encoding="utf-8"))


def save_chapter(path: Path, chapter: str, count: int, passed: int, duplicate: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Блоки"
    sheet.append(["chapter_id", "block_id", "english_text", "russian_text", "qa_status"])
    for number in range(1, count + 1):
        block_number = number if not (duplicate and number == count) else count - 1
        status = "QA_PASS" if number <= passed else "PENDING"
        sheet.append(
            [chapter, f"{chapter}-B{block_number:04d}", "source", "перевод" if status == "QA_PASS" else "", status]
        )
    workbook.save(path)


def save_issues_xlsx(path: Path, chapter: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["error_id", "status"])
    sheet.append([f"{chapter}-ERR-001", "CLOSED"])
    workbook.save(path)


class ValidatorTests(unittest.TestCase):
    def make_tree(self, root: Path, duplicate_ch05: bool = False) -> None:
        for spec in CONFIG["chapters"]:
            save_chapter(
                root / spec["path"],
                spec["chapter"],
                spec["expected_count"],
                spec["qa_pass_through"],
                duplicate=duplicate_ch05 and spec["chapter"] == "CH05",
            )
        for chapter in ("CH06", "CH07", "CH08"):
            save_issues_xlsx(root / f"qa/issues/{chapter}/errors.xlsx", chapter)
        csv_path = root / "qa/issues/CH09/errors.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerows([["error_id", "status"], ["CH09-ERR-001", "CLOSED"]])
        checksum_targets = [
            root / "qa/issues/CH06/errors.xlsx",
            root / "qa/issues/CH07/errors.xlsx",
            root / "qa/issues/CH08/errors.xlsx",
            csv_path,
        ]
        manifest = root / "manifests/SHA256SUMS_ERRORS_2026-08-16.txt"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            "".join(
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}\n"
                for path in checksum_targets
            ),
            encoding="utf-8",
        )

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--root",
                str(root),
                "--config",
                str(PROJECT / "config" / "registry_expectations.json"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_snapshot_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_tree(root)
            result = self.run_validator(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("0 errors", result.stdout)

    def test_duplicate_block_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_tree(root, duplicate_ch05=True)
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("повторяющиеся block_id", result.stdout)


if __name__ == "__main__":
    unittest.main()
