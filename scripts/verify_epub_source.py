#!/usr/bin/env python3
"""Verify batch source_html fragments against canonical EPUB XPath nodes."""
from __future__ import annotations
import argparse,csv,zipfile
from pathlib import Path
from lxml import etree
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("epub",type=Path); ap.add_argument("batch",type=Path); ap.add_argument("--chapter",type=int,required=True); ns=ap.parse_args()
    with zipfile.ZipFile(ns.epub) as z: doc=etree.fromstring(z.read(f"OEBPS/Text/Chapter_{ns.chapter}.xhtml"))
    with ns.batch.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    errors=[]
    for r in rows:
        try:
            frag=etree.fromstring(r["source_html"].encode())
            nodes=doc.xpath(r["xhtml_path"])
            if len(nodes)!=1: errors.append(f'{r["block_id"]}: XPath matched {len(nodes)} nodes')
            elif etree.tostring(nodes[0],method="c14n")!=etree.tostring(frag,method="c14n"): errors.append(f'{r["block_id"]}: source_html mismatch')
        except Exception as exc: errors.append(f'{r.get("block_id","?")}: {exc}')
    for e in errors: print("ERROR:",e)
    if errors:return 1
    print(f"EPUB source verification: PASS ({len(rows)} blocks)"); return 0
if __name__=="__main__": raise SystemExit(main())
