#!/usr/bin/env python3
"""Apply an audited JSON patch to mutable fields in one batch CSV."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
MUTABLE={"russian_text","target_html","translation_status","qa_semantic","qa_terminology","qa_numbers_code_links","qa_structure_formatting","qa_status","notes","version"}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("batch",type=Path); ap.add_argument("patch",type=Path); ap.add_argument("output",type=Path); ns=ap.parse_args()
    with ns.batch.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); header=reader.fieldnames or []; rows=list(reader)
    patches=json.loads(ns.patch.read_text(encoding="utf-8")); by_id={r["block_id"]:r for r in rows}
    for block_id,changes in patches.items():
        if block_id not in by_id: raise ValueError(f"unknown block_id: {block_id}")
        forbidden=set(changes)-MUTABLE
        if forbidden: raise ValueError(f"{block_id}: immutable or unknown fields: {sorted(forbidden)}")
        by_id[block_id].update({k:str(v) for k,v in changes.items()})
    ns.output.parent.mkdir(parents=True,exist_ok=True)
    with ns.output.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=header); w.writeheader(); w.writerows(rows)
    print(f"Applied {len(patches)} audited block patches"); return 0
if __name__=="__main__": raise SystemExit(main())
