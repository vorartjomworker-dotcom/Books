#!/usr/bin/env python3
"""Validate a translated batch against the immutable registry source."""

from __future__ import annotations

import argparse
import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

try:
    from .extract_batch import read_registry, select_range
except ImportError:  # Direct script execution.
    from extract_batch import read_registry, select_range

IMMUTABLE = ["chapter_id", "block_id", "sequence_number", "element_type", "section_path", "xhtml_path", "source_element_id", "english_text", "source_html", "asset_ids", "table_id", "formula_id", "code_id", "link_ids", "formatting_markers"]
URL_RE = re.compile(r"https?://[^\s<>]+")
FILE_RE = re.compile(r"\b[A-Za-z0-9_./-]+\.(?:py|ipynb|csv|json|xlsx)\b")
NUMBER_RE = re.compile(r"(?<!\w)\d+(?:[.,\s\u00a0]\d+)*(?:%)?")
INTERVAL_RE = re.compile(r"([\[(])\s*(\d+(?:[.,]\d+)?)\s*,\s*(\d+(?:[.,]\d+)?)\s*([\])])")


def canonical_number(token: str) -> tuple[Decimal, bool] | None:
    """Normalize localized decimal/thousands separators for comparison."""
    value = token.strip()
    percent = value.endswith("%")
    if percent:
        value = value[:-1]
    value = value.replace("\u00a0", "").replace(" ", "")
    if "," in value and "." in value:
        decimal_separator = "," if value.rfind(",") > value.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        value = value.replace(thousands_separator, "").replace(decimal_separator, ".")
    elif "," in value or "." in value:
        separator = "," if "," in value else "."
        parts = value.split(separator)
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and parts[0] != "0"):
            value = "".join(parts)
        else:
            value = ".".join(parts)
    try:
        return Decimal(value), percent
    except InvalidOperation:
        return None


def missing_source_tokens(source: str, target: str) -> list[str]:
    """Return protected URLs, filenames, and numeric values absent from target."""
    missing: list[str] = []
    for token in URL_RE.findall(source):
        clean = token.rstrip(".,;:!?)\"]}")
        if clean not in target:
            missing.append(clean)
    for token in FILE_RE.findall(source):
        if token not in target:
            missing.append(token)
    def numeric_tokens(text: str) -> list[str]:
        interval_values: list[str] = []
        def remove_interval(match: re.Match[str]) -> str:
            interval_values.extend([match.group(2), match.group(3)])
            return " "
        remainder = INTERVAL_RE.sub(remove_interval, text)
        return interval_values + NUMBER_RE.findall(remainder)

    target_numbers = {canonical_number(token) for token in numeric_tokens(target)}
    for token in numeric_tokens(source):
        canonical = canonical_number(token)
        if canonical is not None and canonical not in target_numbers:
            missing.append(token)
    return missing


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
        missing_tokens = missing_source_tokens(str(original.get("english_text") or ""), russian)
        if missing_tokens:
            errors.append(f"{block}: source tokens missing in Russian: {missing_tokens}")
        if original.get("asset_ids") and not target.get("source_html"):
            errors.append(f"{block}: raster formula/asset source_html missing")
        if target.get("translation_status") == "QA_PASS" and original.get("source_html") and not (target.get("target_html") or "").strip():
            errors.append(f"{block}: QA_PASS requires target_html")
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
