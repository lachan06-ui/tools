#!/usr/bin/env python3
"""
feature_pack.py
機能タグから「送るべきクラス」を選び、タスク用コンテキストパックを出力する。

タグの正本は同じフォルダの feature_tags.json（inv_sep_map_v4.py が維持する）。

Usage:
  python3 feature_pack.py --list
  python3 feature_pack.py enemy
  python3 feature_pack.py enemy --class EnemyAI -o pack.txt
  python3 feature_pack.py enemy --inventory path/to/tr_1_inventory.md
"""
import argparse
import json
import re
from pathlib import Path

FEATURE_TAGS_FILE = Path(__file__).with_name("feature_tags.json")

SECTION_RE = re.compile(r"^## (.+?)\s*$")
FIELD_RE = re.compile(r"^### (.+?)\s*$")
LAYER_RE = re.compile(r"^# Layer")
EMPTY = {"", "none", "not found", "placeholder"}


def load_feature_tags():
    if not FEATURE_TAGS_FILE.exists():
        raise SystemExit(f"feature_tags.json が見つからない: {FEATURE_TAGS_FILE}")
    data = json.loads(FEATURE_TAGS_FILE.read_text(encoding="utf-8"))
    return data.get("classes", {}), data.get("tag_descriptions", {})


def parse_inventory(text):
    systems, cur, field = {}, None, None
    for raw in text.splitlines():
        line = raw.replace("\r", "").strip()
        if LAYER_RE.match(line):
            cur, field = None, None
            continue
        m = SECTION_RE.match(line)
        if m:
            cur, field = m.group(1), None
            systems[cur] = {}
            continue
        m = FIELD_RE.match(line)
        if m and cur:
            field = m.group(1)
            systems[cur][field] = []
            continue
        if cur and field and line.startswith("- "):
            value = line[2:].strip().replace("**", "")
            if value.lower() not in EMPTY:
                systems[cur][field].append(value)
    return systems


def tags_of(name, classes):
    entry = classes.get(name)
    return set(entry["tags"]) if entry else set()


def first(info, field):
    vals = info.get(field, [])
    return vals[0] if vals else ""


def file_of(info):
    return first(info, "Related Files")


def print_list(systems, classes, descriptions):
    buckets = {}
    for name in systems:
        for t in tags_of(name, classes):
            buckets.setdefault(t, []).append(name)

    print("== タグ一覧 ==")
    for t in sorted(buckets):
        names = sorted(buckets[t])
        print(f"{t} ({len(names)}) {descriptions.get(t, '')}")
        print(f"    {', '.join(names)}")

    untagged = [n for n in systems if not tags_of(n, classes)]
    auto = [n for n, e in classes.items() if e.get("source") == "auto"]
    print()
    print(f"登録: {len(classes)}  インベントリ内: {len(systems)}")
    if auto:
        print(f"自動追加（要確認）: {len(auto)} → {', '.join(sorted(auto))}")
    if untagged:
        print(f"タグなし: {', '.join(sorted(untagged))}")


def build_pack(systems, classes, tags, extra_classes):
    targets = set(extra_classes)
    for name in systems:
        if tags_of(name, classes) & set(tags):
            targets.add(name)

    lines = [f"=== FEATURE PACK: {', '.join(tags) or '-'} ===",
             f"Target classes: {len(targets)}", ""]

    lines.append("## 対象クラス（全フィールド）")
    for name in sorted(targets):
        info = systems.get(name)
        if info is None:
            lines.append(f"### {name}  [NOT IN INVENTORY]")
            continue
        lines.append(f"### {name}  ({file_of(info)})")
        lines.append(f"Purpose: {first(info, 'Purpose')}")
        for field in ["Public API Methods", "Signals", "Properties",
                      "Owned Data", "Depends On", "Used By", "Notes"]:
            vals = info.get(field, [])
            if vals:
                lines.append(f"{field}:")
                lines.extend(f"  - {v}" for v in vals)
        lines.append("")

    outside = set()
    for name in targets:
        for dep in systems.get(name, {}).get("Depends On", []):
            if dep not in targets:
                outside.add(dep)

    lines.append("## 外部依存（用途のみ）")
    for dep in sorted(outside):
        info = systems.get(dep)
        if info is None:
            lines.append(f"- {dep}")
        else:
            lines.append(f"- {dep} ({file_of(info)}): {first(info, 'Purpose')}")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--class", dest="classes", action="append", default=[])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--inventory", default=".doc/0_truth/tr_1_inventory.md")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    classes, descriptions = load_feature_tags()
    systems = parse_inventory(Path(args.inventory).read_text(encoding="utf-8"))

    if args.list:
        print_list(systems, classes, descriptions)
        return

    if not args.tags and not args.classes:
        ap.error("タグかクラス名を指定してください（--list で一覧）")

    pack = build_pack(systems, classes, args.tags, args.classes)
    if args.out:
        Path(args.out).write_text(pack, encoding="utf-8")
        print(f"written: {args.out}  ({len(pack)} chars)")
    else:
        print(pack)


if __name__ == "__main__":
    main()
