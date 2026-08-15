import csv
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from scripts.apply_batch_updates import apply_updates
from scripts.extract_batch import read_registry, select_range, write_csv
from scripts.validate_batch import validate_batch


HEADER = ["chapter_id", "block_id", "sequence_number", "element_type", "section_path", "xhtml_path", "source_element_id", "pdf_physical_page", "pdf_printed_page", "english_text", "russian_text", "source_html", "target_html", "asset_ids", "table_id", "formula_id", "code_id", "link_ids", "term_candidates", "formatting_markers", "translation_status", "qa_semantic", "qa_terminology", "qa_numbers_code_links", "qa_structure_formatting", "qa_status", "batch_id", "notes", "version"]


class BatchToolsTests(unittest.TestCase):
    def make_registry(self, root: Path) -> Path:
        path = root / "registry.xlsx"
        wb = Workbook(); ws = wb.active; ws.title = "Блоки"; ws.append(HEADER)
        for number in range(1, 4):
            row = {field: None for field in HEADER}
            row.update(chapter_id="CH05", block_id=f"CH05-B{number:04d}", sequence_number=number, element_type="p", english_text=f"Value {number}% file.py", source_html=f"<p>Value {number}% file.py</p>", translation_status="PENDING_TRANSLATION")
            ws.append([row[field] for field in HEADER])
        wb.save(path)
        return path

    def test_extract_apply_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); registry = self.make_registry(root); batch = root / "batch.csv"
            header, records = read_registry(registry); write_csv(batch, header, select_range(records, "CH05", 1, 3))
            updates = {f"CH05-B{n:04d}": {"russian_text": f"Значение {n}% file.py", "translation_status": "TRANSLATED"} for n in range(1, 4)}
            update_path = root / "updates.json"; update_path.write_text(json.dumps(updates, ensure_ascii=False), encoding="utf-8")
            output = root / "translated.csv"; self.assertEqual(apply_updates(batch, update_path, output), 3)
            self.assertEqual(validate_batch(registry, output, "CH05", 1, 3), [])

    def test_forbidden_source_edit_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); registry = self.make_registry(root); batch = root / "batch.csv"
            header, records = read_registry(registry); write_csv(batch, header, select_range(records, "CH05", 1, 1))
            update_path = root / "updates.json"; update_path.write_text(json.dumps({"CH05-B0001": {"english_text": "changed"}}), encoding="utf-8")
            with self.assertRaises(ValueError): apply_updates(batch, update_path, root / "out.csv")


if __name__ == "__main__":
    unittest.main()
