#!/usr/bin/env python3
"""Validate the autonomous translation queue and state without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BRANCH_RE = re.compile(r"^translation/(ch\\d{2})-b(\\d{4})-b(\\d{4})$")
VALID_MODES = {"pilot", "autonomous"}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    config = load_json(root / "automation" / "pipeline_config.json")
    state = load_json(root / "automation" / "state.json")
    expectations = load_json(root / "config" / "registry_expectations.json")

    config_mode = config.get("mode")
    state_mode = state.get("mode")
    if config_mode not in VALID_MODES or state_mode not in VALID_MODES:
        errors.append("mode must be pilot or autonomous")
    elif config_mode != state_mode:
        errors.append("config and state modes must match")

    if config.get("merge_policy") != "manual" or state.get("merge_policy") != "manual":
        errors.append("manual merge policy is required")

    config_auto_advance = config.get("auto_advance", False)
    state_auto_advance = state.get("auto_advance", False)
    if config_auto_advance != state_auto_advance:
        errors.append("config and state auto_advance values must match")
    if config_mode == "pilot" and config_auto_advance:
        errors.append("pilot mode cannot auto-advance")
    if config_mode == "autonomous" and not config_auto_advance:
        errors.append("autonomous mode requires auto_advance")

    allowed = set(config.get("allowed_states", []))
    queue = state.get("queue", [])
    if not queue:
        errors.append("queue is empty")

    seen: set[tuple[str, int]] = set()
    queue_keys: set[tuple[str, int, int, str]] = set()
    queue_status: dict[tuple[str, int, int, str], str] = {}
    expected_chapters = {
        item["chapter"]: item for item in expectations.get("chapters", [])
    }

    for index, item in enumerate(queue):
        label = f"queue[{index}]"
        chapter = item.get("chapter")
        start = item.get("start")
        end = item.get("end")
        branch = item.get("branch", "")
        status = item.get("status")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            errors.append(f"{label}: invalid range")
            continue
        if end - start + 1 > config.get("batch_size", 0):
            errors.append(f"{label}: range exceeds batch_size")
        if status not in allowed:
            errors.append(f"{label}: invalid status {status!r}")
        match = BRANCH_RE.fullmatch(branch)
        if not match or match.group(1).upper() != chapter or int(match.group(2)) != start or int(match.group(3)) != end:
            errors.append(f"{label}: branch does not encode chapter/range")
        total = expected_chapters.get(chapter, {}).get("expected_count")
        if not isinstance(total, int) or end > total:
            errors.append(f"{label}: range exceeds expected chapter total")
        for block in range(start, end + 1):
            key = (chapter, block)
            if key in seen:
                errors.append(f"{label}: overlaps {chapter}-B{block:04d}")
            seen.add(key)
        queue_key = (chapter, start, end, branch)
        queue_keys.add(queue_key)
        queue_status[queue_key] = status

    active = state.get("active")
    if active:
        active_key = (active.get("chapter"), active.get("start"), active.get("end"), active.get("branch"))
        if active_key not in queue_keys:
            errors.append("active range is not present in queue")
        elif queue_status[active_key] != active.get("status"):
            errors.append("active status does not match queue status")
        if active.get("status") not in allowed:
            errors.append("active status is invalid")
        attempt = active.get("attempt")
        if not isinstance(attempt, int) or attempt < 0 or attempt > config.get("max_fix_cycles", 0):
            errors.append("active attempt exceeds max_fix_cycles")

    if config.get("max_batches_per_run") != 1:
        errors.append("pipeline must process exactly one batch per run")
    if config.get("canonical_write_policy") != "integrator_only":
        errors.append("canonical registries must be integrator-only")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Autonomous pipeline state: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
