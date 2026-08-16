#!/usr/bin/env python3
"""Verify batch source_html fragments against canonical EPUB XPath nodes."""
from __future__ import annotations

import argparse
import csv
import zipfile
from pathlib import Path

from lxml import etree


def canonicalize(element: etree._Element) -> bytes:
    """Serialize a fragment without inherited namespace context or tail text."""
    return etree.tostring(element, method="c14n", exclusive=True, with_comments=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", type=Path)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    with zipfile.ZipFile(args.epub) as archive:
        document = etree.fromstring(archive.read(f"OEBPS/Text/Chapter_{args.chapter}.xhtml"))
    with args.batch.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    errors = []
    for row in rows:
        try:
            fragment = etree.fromstring(row["source_html"].encode())
            nodes = document.xpath(row["xhtml_path"])
            if len(nodes) != 1:
                errors.append(f'{row["block_id"]}: XPath matched {len(nodes)} nodes')
            elif canonicalize(nodes[0]) != canonicalize(fragment):
                errors.append(f'{row["block_id"]}: source_html mismatch')
        except Exception as exc:
            errors.append(f'{row.get("block_id", "?")}: {exc}')
    for error in errors:
        print("ERROR:", error)
    if errors:
        return 1
    print(f"EPUB source verification: PASS ({len(rows)} blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
