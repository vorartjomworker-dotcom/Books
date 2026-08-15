#!/usr/bin/env python3
"""Validate a translated batch against the immutable registry source."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

try:
    from .extract_batch import read_registry, select_range
except ImportError:  # Direct script execution.
    from extract_batch import read_registry, select_range

IMMUTABLE = ["chapter_id", "block_id", "sequence_number", "element_type", "section_path", "xhtml_path", "source_element_id", "english_text", "source_html", "asset_ids", "table_id", "formula_id", "code_id", "link_ids", "formatting_markers"]
TOKEN_RE = re.compile(r"https?://\S+|\b\d+(?:[.,]\d+)?%?\b|\b[A-Za-z0-9_./-]+\.(?:py|ipynb|csv|json|xlsx)\b")


def load_batch(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def validate_batch(registry: Path, batch: Path, chapter: str, start: int, end: int) -> list[str]:
    _, records = read_registry(registry)
    source = select_range(records, chapter, start, end)
    translated = load_batch(batch)
    errors: list[str] = []
    if len(translated) != end - start + 1:
        errors.append(f"batch count {len(translated)} != {end-start+1}")
        return errors
    for original, target in zip(source, translated):
        block = str(original["block_id"])
        if target.get("block_id") != block:
            errors.append(f"{block}: order or identifier changed")
            continue
        for field in IMMUTABLE:
            left = "" if original.get(field) is None else str(original.get(field))
            right = target.get(field, "")
            if left != right:
                errors.append(f"{block}: immutable field changed: {field}")
        russian = (target.get("russian_text") or "").strip()
        if not russian:
            errors.append(f"{block}: russian_text is empty")
        if target.get("translation_status") not in {"TRANSLATED", "QA_IN_PROGRESS", "READY_FOR_RECHECK", "QA_PASS"}:
            errors.append(f"{block}: invalid translated status {target.get('translation_status')!r}")
        source_tokens = TOKEN_RE.findall(str(original.get("english_text") or ""))
        missing_tokens = [token for token in source_tokens if token not in russian]
        if missing_tokens:
            errors.append(f"{block}: source tokens missing in Russian: {missing_tokens}")
        if original.get("asset_ids") and not target.get("source_html"):
            errors.append(f"{block}: raster formula/asset source_html missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--start", required=True, type=int)
    parser.add_argument("--end", required=True, type=int)
    args = parser.parse_args()
    errors = validate_batch(args.registry, args.batch, args.chapter, args.start, args.end)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Batch validation: PASS ({args.chapter}-B{args.start:04d}..B{args.end:04d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
