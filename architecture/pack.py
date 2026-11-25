#!/usr/bin/env python3
"""pack.py -- クラウドAIに貼る1つのプロンプトを組み立てる（読み取り専用）。

使い方（プロジェクトのルートで）:
  python tools/architecture/pack.py --task "敵が死んだらXを追加" --target Enemy
  python tools/architecture/pack.py --task "..." --target Enemy --extra EnemyAI --max-chars 20000

前提: generate_charts_v2.py を先に実行して output/ を作っておく。
出力: output/pack_<クラス名>.md（そのままチャットに貼る）

含めるもの: 依頼 / 未解決([?]) / 依存関係(file:line) / ドメイン図 / 関連クラスのシグネチャ / 対象の本文 / 出力形式
サイズが上限を超えたら、関連クラスのシグネチャを関連の薄い順に省略し、
次にドメイン図、未解決の順に省く。省略したものは先頭に明記する。対象の本文は省かない。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

FUNC = re.compile(
    r"^[ \t]*(?:static[ \t]+)?func[ \t]+(\w+)[ \t]*\(([^)]*)\)([ \t]*->[ \t]*[\w.\[\]]+)?",
    re.M)
SIGNAL = re.compile(r"^[ \t]*signal[ \t]+[^\n]*", re.M)

OUTPUT_RULES = """## 出力形式（厳守）
変更は次の3種類のブロックだけで出す。説明文は書いてよいが、適用されるのはこのブロックだけ。
1. 関数の置換（1関数ごと。func 行から本文の最後まで丸ごと。インデントは元のまま）
=== REPLACE <path> :: <func名> ===
<新しい関数全体>
=== END ===
2. ファイルの新規作成・全置換（テストの追加など）
=== FILE <path> ===
<ファイル全体>
=== END ===
3. 上で書きにくい小さな変更は、```diff の unified diff（---/+++ 付き、a/ b/ 付き）
その他:
- テストは tests/ に追加する（既存の形式に合わせる）
- feature_tags.json の変更が要るなら、diff で出す
- 足りないファイルがあれば、推測で書かず、ファイル名だけ挙げる
"""


def load_json(out: Path, name: str, default):
    p = out / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def display(p: str, classes: dict) -> str:
    if p in classes:
        return classes[p]["class_name"] or Path(p).stem
    return p


def find_target(classes: dict, target: str):
    for p, v in classes.items():
        if p == target or v["class_name"] == target or Path(p).stem == target:
            return p
    return None


def edge_line(e: dict, classes: dict) -> str:
    where = e["target"] if e["kind"] == "signal" else e["source"]  # signal の line は受信側
    loc = f" @{where}:{e['line']}" if e.get("line") else ""
    det = f" ({e['detail']})" if e.get("detail") else ""
    return f"[{e['kind']}] {display(e['source'], classes)} -> {display(e['target'], classes)}{det}{loc}"


def signature_block(root: Path, rel: str, classes: dict, limit: int = 40) -> str:
    v = classes.get(rel, {})
    head = f"### {display(rel, classes)}  ({rel}, domain={v.get('domain', '?')})"
    p = root / rel
    if not p.exists():
        return head + "\n（ファイルが見つかりません）\n"
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = [head]
    if v.get("extends"):
        lines.append("extends " + ", ".join(v["extends"]))
    items = []
    for m in SIGNAL.finditer(text):
        items.append((text.count("\n", 0, m.start()) + 1, m.group(0).strip()))
    for m in FUNC.finditer(text):
        if m.group(1).startswith("_"):
            continue  # public のみ
        sig = f"func {m.group(1)}({' '.join(m.group(2).split())})"
        if m.group(3):
            sig += " " + m.group(3).strip()
        items.append((text.count("\n", 0, m.start()) + 1, sig))
    items.sort()
    for line, s in items[:limit]:
        lines.append(f"- L{line} {s}")
    if len(items) > limit:
        lines.append(f"- …他 {len(items) - limit} 件")
    return "\n".join(lines) + "\n"


def body_block(root: Path, rel: str, title: str) -> str:
    p = root / rel
    text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else "（ファイルが見つかりません）"
    return f"## {title}: {rel}\n```gdscript\n{text}\n```\n"


def build_pack(root: Path, out: Path, task: str, target: str, max_chars: int = 24000,
               max_neighbors: int = 12, brief_path: Path | None = None, extra=(),
               conventions_path: Path | None = None):
    classes = load_json(out, "classes.json", {})
    deps = load_json(out, "dependencies.json", [])
    unres = load_json(out, "unresolved.json", [])
    scenes = load_json(out, "scenes.json", {})
    tp = find_target(classes, target)
    if tp is None:
        raise SystemExit(f"[ERROR] target '{target}' が classes.json にありません")

    def to_script(p):
        if p in classes:
            return p
        return (scenes.get(p) or {}).get("root_script")

    uses = [e for e in deps if e["source"] == tp]
    used_by = [e for e in deps if e["target"] == tp]
    cnt: Counter = Counter()
    for e in uses:
        n = to_script(e["target"])
        if n and n != tp:
            cnt[n] += 1
    for e in used_by:
        n = to_script(e["source"])
        if n and n != tp:
            cnt[n] += 1

    def edge_block(title, es, cap=60):
        if not es:
            return ""
        es = sorted(es, key=lambda e: (e["kind"], e["source"], e["target"], e["detail"]))
        lines = [edge_line(e, classes) for e in es[:cap]]
        if len(es) > cap:
            lines.append(f"…他 {len(es) - cap} 件")
        return f"## {title}\n" + "\n".join(lines) + "\n"

    header = f"# 依頼\n目的: {task}\n対象: {display(tp, classes)} ({tp}, domain={classes[tp].get('domain', '?')})\n"
    if brief_path and brief_path.exists():
        header += "\n" + brief_path.read_text(encoding="utf-8", errors="replace")[:3000] + "\n"
    if conventions_path and conventions_path.exists():
        header += "\n## コーディング規約\n" + conventions_path.read_text(
            encoding="utf-8", errors="replace")[:2500] + "\n"
    mine = [u for u in unres if u["source"] == tp]
    unres_block = ""
    if mine:
        rows = [f"[?{u['kind']}] {u['source']}:{u['line']} {u['target']}" for u in mine[:20]]
        if len(mine) > 20:
            rows.append(f"…他 {len(mine) - 20} 件")
        unres_block = "## 未解決（解析で解決できなかった箇所）\n" + "\n".join(rows) + "\n"
    uses_block = edge_block("依存関係: 対象が使う/発行する", uses)
    used_block = edge_block("依存関係: 対象を使う/受信する", used_by)
    mmd = out / "domains.mmd"
    domains_block = ("## ドメイン図\n```mermaid\n" + mmd.read_text(encoding="utf-8") + "```\n") if mmd.exists() else ""
    neighbors = [(n, signature_block(root, n, classes)) for n, _ in cnt.most_common(max_neighbors)]
    body = body_block(root, tp, "対象の本文")
    extra_blocks = []
    for name in extra:
        ep = find_target(classes, name)
        if ep and ep != tp:
            extra_blocks.append(body_block(root, ep, "追加の本文"))
        elif not ep:
            print(f"[WARN] --extra '{name}' が見つかりません", file=sys.stderr)
    tail = f"## 最後に\n{task}\n"

    def build(nb, with_domains, with_unres, dropped):
        c = [header]
        if dropped:
            c.append("※ サイズ上限のため省略: " + ", ".join(dropped) + "\n")
        if with_unres and unres_block:
            c.append(unres_block)
        c += [uses_block, used_block]
        if with_domains and domains_block:
            c.append(domains_block)
        if nb:
            c.append("## 関連クラスのシグネチャ（public のみ）\n")
            c += [b for _, b in nb]
        c += [body] + extra_blocks + [OUTPUT_RULES, tail]
        return "\n".join(x for x in c if x)

    nb, with_domains, with_unres, dropped = list(neighbors), True, True, []
    text = build(nb, with_domains, with_unres, dropped)
    while len(text) > max_chars and nb:
        n, _ = nb.pop()
        dropped.append(display(n, classes))
        text = build(nb, with_domains, with_unres, dropped)
    if len(text) > max_chars and with_domains and domains_block:
        with_domains = False
        dropped.append("ドメイン図")
        text = build(nb, with_domains, with_unres, dropped)
    if len(text) > max_chars and with_unres and unres_block:
        with_unres = False
        dropped.append("未解決")
        text = build(nb, with_domains, with_unres, dropped)
    return text, dropped, tp, classes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--extra", nargs="*", default=[], help="本文も入れる追加クラス")
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", default="tools/architecture/output")
    ap.add_argument("--brief", default="tools/project_brief.md")
    ap.add_argument("--conventions", default="tools/conventions.md")
    ap.add_argument("--max-chars", type=int, default=24000)
    ap.add_argument("--max-neighbors", type=int, default=12)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.output)
    out = out if out.is_absolute() else root / out
    brief = Path(args.brief)
    brief = brief if brief.is_absolute() else root / brief
    conv = Path(args.conventions)
    conv = conv if conv.is_absolute() else root / conv
    text, dropped, tp, classes = build_pack(
        root, out, args.task, args.target, args.max_chars, args.max_neighbors, brief, args.extra, conv)
    dest = out / f"pack_{display(tp, classes)}.md"
    dest.write_text(text + "\n", encoding="utf-8")
    print(f"出力: {dest}  ({len(text)} 文字)")
    if dropped:
        print("省略: " + ", ".join(dropped))
    if len(text) > args.max_chars:
        print(f"[WARN] 上限 {args.max_chars} 文字を超えています。--extra を減らすか、対象を分けてください")


if __name__ == "__main__":
    main()