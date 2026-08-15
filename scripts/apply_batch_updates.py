#!/usr/bin/env python3
"""Apply block-keyed translation updates to an extracted CSV with a strict allowlist."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ALLOWED_FIELDS = {"russian_text", "target_html", "translation_status", "batch_id", "notes", "version"}


def apply_updates(batch: Path, updates_path: Path, output: Path) -> int:
    with batch.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        rows = list(reader)
    updates = json.loads(updates_path.read_text(encoding="utf-8"))
    by_id = {row["block_id"]: row for row in rows}
    unknown = set(updates) - set(by_id)
    if unknown:
        raise ValueError(f"updates outside batch: {sorted(unknown)}")
    for block_id, patch in updates.items():
        forbidden = set(patch) - ALLOWED_FIELDS
        if forbidden:
            raise ValueError(f"{block_id}: forbidden fields {sorted(forbidden)}")
        for field, value in patch.items():
            if field not in header:
                raise ValueError(f"{block_id}: missing output column {field}")
            by_id[block_id][field] = value
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return len(updates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    parser.add_argument("updates", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count = apply_updates(args.batch, args.updates, args.output)
    print(f"Applied updates to {count} blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

