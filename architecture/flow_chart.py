#!/usr/bin/env python3
"""flow_chart.py -- 人が書いた「出来事の骨格」に、事実で根拠と接続を付けて、図（SVG）にする。

役割分担:
  人          : 出来事と、その順序（tools/flow_skeleton.txt）
  ローカルLLM : 各出来事に対応するクラス名・シグナル名を「候補」から選ぶだけ（evidence.json）
  スクリプト  : 名前の実在を検証し、出来事どうしが実際に接続しているかを依存関係から判定して描く

使い方（プロジェクトのルートで）:
  1) python tools/architecture/flow_chart.py prompt tools/flow_skeleton.txt --inventory tr_1_inventory.md
       -> output/evidence_prompt.md  （全文をローカルLLMに貼り、返答を output/evidence.json に保存）
  2) python tools/architecture/flow_chart.py check tools/flow_skeleton.txt tools/architecture/output/evidence.json
       -> output/flow_final.dot / flow_final.svg / flow_final_report.md

スケルトンの書式（# で始まる行はコメント）:
  id | 出来事 | 次のid（, 区切り。なければ空）
辺の判定（出来事Aの根拠クラス群 -> 出来事Bの根拠クラス群）:
  シグナル(青)   : そのクラス間（または根拠のシグナル）に 発行->受信 の辺がある
  直接(黒)       : クラス間に直接参照がある
  同一クラス(黒) : 両方に同じクラスが含まれる
  経由(橙の点線) : ハブ（EventBus 等）を除いて、3ホップ以内で依存がつながる
  未接続(赤の点線): つながりが検出されない（設計と実装のずれ、または根拠の選び間違い）
  根拠なし(灰の点線): どちらかの出来事に根拠名が無い
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
from collections import defaultdict, deque
from pathlib import Path

DIRECT_KINDS = {"class_use", "autoload_use", "preload", "preload_scene", "scene_ref",
                "group_call", "extends"}
FONT = "Noto Sans CJK JP"
PALETTE = ["#DCEBFA", "#E3F4DC", "#FCE8D5", "#F2DDF3", "#FFF4C2", "#D8F0EE",
           "#F8D9D9", "#E6E6F5", "#EAEAEA", "#DDEBD0", "#F5E1C8", "#D5E3F0"]
STYLE = {  # kind -> (color, style)
    "signal": ("#2563EB", "solid"), "direct": ("#334155", "solid"), "same": ("#334155", "solid"),
    "path": ("#D97706", "dashed"), "none": ("#DC2626", "dashed"), "noevidence": ("#94A3B8", "dotted"),
}
LABEL = {"same": "同一クラス", "none": "未接続", "noevidence": "根拠なし"}

PROMPT = """# 依頼
下の「出来事」それぞれについて、対応する実装上の名前を、「候補」の中から選んでください。
出来事どうしの関係（矢印）は考えなくてかまいません。人が決めています。

## 出力（JSONのみ。説明文・Markdown・コードフェンスは書かない。出力は { で始まり } で終わる）
{"nodes":[{"id":"n1","evidence":["候補にあるクラス名やシグナル名"]}],
 "unknown":["候補から選べなかった出来事の id と理由"]}

## ルール
- 1つの出来事につき1〜4個。その出来事を実際に担う中心のクラス（とシグナル）だけを選ぶ。
- 名前は候補の表記をそのまま写す。候補にない名前を書かない。作らない。
- 該当するものが候補に無ければ evidence は空配列にして、unknown に書く。
- 汎用の基盤クラス（GameState、EventBus など）は、その出来事の中心でない限り選ばない。

"""


def parse_skeleton(text: str):
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2 or not parts[0]:
            raise SystemExit(f"[ERROR] 'id | 出来事 | 次のid' の形式ではありません: {line}")
        nodes[parts[0]] = parts[1]
        if len(parts) > 2:
            edges += [(parts[0], n.strip()) for n in parts[2].split(",") if n.strip()]
    missing = sorted({b for _, b in edges if b not in nodes})
    if missing:
        raise SystemExit(f"[ERROR] 次のid が定義されていません: {missing}")
    return nodes, edges


def extract_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < i:
        raise SystemExit("[ERROR] JSON が見つかりません")
    try:
        return json.loads(text[i:j + 1])
    except json.JSONDecodeError as e:
        raise SystemExit(f"[ERROR] JSON が壊れています: {e}")


def shortest(src: set, dst: set, adj: dict, hubs: set, max_depth: int = 3):
    prev = {x: None for x in src}
    q = deque((x, 0) for x in sorted(src))
    while q:
        cur, d = q.popleft()
        if cur in dst:
            path, n = [], cur
            while n is not None:
                path.append(n)
                n = prev[n]
            return path[::-1]
        if d >= max_depth:
            continue
        for nb in sorted(adj.get(cur, ())):
            if nb in prev or (nb in hubs and nb not in dst):
                continue
            prev[nb] = cur
            q.append((nb, d + 1))
    return None


def classify(ca, cb, sa, sb, direct_pairs, sig_edges, adj, hubs):
    if not (ca or sa) or not (cb or sb):
        return "noevidence", ""
    both = ca | cb
    for s, t, d in sig_edges:
        strong = (s in ca and t in cb) or (s in cb and t in ca)
        weak = d in (sa | sb) and (not both or s in both or t in both)
        if strong or weak:
            return "signal", d
    if ca & cb:
        return "same", ""
    if any((x, y) in direct_pairs for x in ca for y in cb):
        return "direct", ""
    path = shortest(ca, cb, adj, hubs)
    if path:
        return "path", " → ".join(path)
    return "none", ""


def evaluate(nodes, edges, raw_evidence, classes, signals, deps, hubs=()):
    name_of = {p: (v.get("class_name") or Path(p).stem) for p, v in classes.items()}

    def nm(p):
        return name_of.get(p, Path(p).stem)

    known_classes = set(name_of.values())
    known_signals = {s["signal"] for s in signals}
    adj: dict[str, set] = defaultdict(set)
    direct_pairs: set = set()
    sig_edges = []
    for e in deps:
        a, b = nm(e["source"]), nm(e["target"])
        if a == b:
            continue
        if e["kind"] == "signal":
            sig_edges.append((a, b, e.get("detail", "")))
        elif e["kind"] in DIRECT_KINDS:
            direct_pairs.add((a, b))
            direct_pairs.add((b, a))
        else:
            continue
        adj[a].add(b)
        adj[b].add(a)
    ev, bad = {}, {}
    for nid in nodes:
        raw = [str(x).strip() for x in raw_evidence.get(nid, [])]
        cls = [x for x in raw if x in known_classes]
        sig = [x for x in raw if x in known_signals and x not in known_classes]
        wrong = [x for x in raw if x not in known_classes and x not in known_signals]
        ev[nid] = {"classes": cls, "signals": sig}
        if wrong:
            bad[nid] = wrong
    rows = []
    for a, b in edges:
        kind, label = classify(set(ev[a]["classes"]), set(ev[b]["classes"]),
                               set(ev[a]["signals"]), set(ev[b]["signals"]),
                               direct_pairs, sig_edges, adj, set(hubs))
        rows.append((a, b, kind, label))
    return ev, rows, bad


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def to_dot(nodes, ev, rows, classes):
    domain_of = {(v.get("class_name") or Path(p).stem): v.get("domain", "?")
                 for p, v in classes.items()}
    palette: dict[str, str] = {}
    lines = ['digraph "flow" {', '  rankdir="LR";', '  bgcolor="white";',
             f'  graph [fontname="{FONT}", pad="0.3"];',
             f'  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=11];',
             f'  edge [fontname="{FONT}", fontsize=9];']
    for nid, label in nodes.items():
        names = ev[nid]["classes"] + ev[nid]["signals"]
        text = esc(f"{nid} {label}")
        if names:
            text += r"\n" + esc("(" + ", ".join(names[:4]) + ")")
            dom = domain_of.get(ev[nid]["classes"][0], "?") if ev[nid]["classes"] else "?"
            fill = palette.setdefault(dom, PALETTE[len(palette) % len(PALETTE)])
            lines.append(f'  "{esc(nid)}" [label="{text}", fillcolor="{fill}"];')
        else:
            lines.append(f'  "{esc(nid)}" [label="{text}", fillcolor="#FFF4C2", '
                         f'style="rounded,filled,dashed"];')
    for a, b, kind, label in rows:
        color, style = STYLE[kind]
        elabel = label if kind in ("signal", "path") else LABEL.get(kind, "")
        lines.append(f'  "{esc(a)}" -> "{esc(b)}" [color="{color}", fontcolor="{color}", '
                     f'style={style}, label="{esc(elabel)}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_report(nodes, ev, rows, bad, unknown) -> str:
    cnt: dict[str, int] = defaultdict(int)
    for _, _, k, _ in rows:
        cnt[k] += 1
    names = {"signal": "シグナル", "direct": "直接", "same": "同一クラス", "path": "経由",
             "none": "未接続", "noevidence": "根拠なし"}
    out = ["# フロー図（人の骨格 + 事実）の検証結果", "",
           f"- 出来事 {len(nodes)} 個、辺 {len(rows)} 本",
           "- 辺の内訳: " + " / ".join(f"{names[k]} {cnt.get(k, 0)}" for k in names)]
    noev = [n for n in nodes if not (ev[n]["classes"] or ev[n]["signals"])]
    if noev:
        out += ["", "## 根拠名のない出来事（実装が無い、または候補から選べなかった）",
                *[f"- {n} {nodes[n]}" for n in noev]]
    if bad:
        out += ["", "## 実在しない名前（LLMが作ったもの。除外済み）",
                *[f"- {k}: {', '.join(v)}" for k, v in bad.items()]]
    for kind, title in (("none", "未接続の辺（設計と実装のずれか、根拠の選び間違い。上から確認）"),
                        ("path", "経由でつながる辺（間に入るクラス）")):
        hit = [(a, b, l) for a, b, k, l in rows if k == kind]
        if hit:
            out += ["", f"## {title}"]
            for a, b, l in hit:
                out.append(f"- {a} {nodes[a]} -> {b} {nodes[b]}" + (f"  [{l}]" if l else ""))
    if unknown:
        out += ["", "## LLMが選べなかったと述べた点", *[f"- {x}" for x in unknown]]
    return "\n".join(out) + "\n"


def load(out: Path, name: str, default):
    p = out / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def cmd_prompt(args):
    out = Path(args.output)
    nodes, _ = parse_skeleton(Path(args.skeleton).read_text(encoding="utf-8"))
    classes, signals = load(out, "classes.json", {}), load(out, "signals.json", [])
    if not classes:
        raise SystemExit(f"[ERROR] {out}/classes.json がありません。先に generate_charts_v2.py を実行してください")
    purposes: dict[str, str] = {}
    if args.inventory and Path(args.inventory).exists():
        spec = importlib.util.spec_from_file_location("gc2", Path(__file__).with_name("generate_charts_v2.py"))
        gc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gc)
        purposes = gc.parse_purposes(Path(args.inventory).read_text(encoding="utf-8", errors="replace"))
    name_of = {p: (v.get("class_name") or Path(p).stem) for p, v in classes.items()}
    by_domain: dict[str, set] = defaultdict(set)
    for p, v in classes.items():
        if v.get("domain") != "debug":
            by_domain[v.get("domain", "?")].add(name_of[p])
    lines = [PROMPT, "## 出来事（これに対応する名前を選ぶ）"]
    lines += [f"- {nid}: {label}" for nid, label in nodes.items()]
    lines += ["", "## 候補1: クラス（ドメイン別。: の後ろは役割）"]
    for d in sorted(by_domain):
        lines.append(f"### {d}")
        for n in sorted(by_domain[d]):
            lines.append(f"- {n}" + (f": {purposes[n][:50]}" if n in purposes else ""))
    lines += ["", "## 候補2: シグナル（発行元 → 受信側）"]
    for s in signals[:100]:
        em = ", ".join(sorted(name_of.get(p, p) for p in s["emitters"])) or "?"
        li = ", ".join(sorted(name_of.get(p, p) for p in s["listeners"])) or "?"
        lines.append(f"- {s['signal']}: {em} → {li}")
    dest = out / "evidence_prompt.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"出力: {dest}  ({len(dest.read_text(encoding='utf-8'))} 文字、役割つきクラス {sum(1 for n in name_of.values() if n in purposes)} 個)")


def cmd_check(args):
    out = Path(args.output)
    nodes, edges = parse_skeleton(Path(args.skeleton).read_text(encoding="utf-8"))
    data = extract_json(Path(args.evidence).read_text(encoding="utf-8", errors="replace"))
    src = data.get("nodes", data)
    raw: dict[str, list] = {}
    if isinstance(src, list):
        for n in src:
            if isinstance(n, dict) and n.get("id"):
                raw[str(n["id"])] = n.get("evidence", [])
    elif isinstance(src, dict):
        raw = {str(k): v for k, v in src.items() if isinstance(v, list)}
    classes, signals, deps = load(out, "classes.json", {}), load(out, "signals.json", []), load(out, "dependencies.json", [])
    ev, rows, bad = evaluate(nodes, edges, raw, classes, signals, deps, set(args.hubs))
    dot = out / "flow_final.dot"
    dot.write_text(to_dot(nodes, ev, rows, classes), encoding="utf-8")
    report = render_report(nodes, ev, rows, bad, data.get("unknown", []) if isinstance(data, dict) else [])
    (out / "flow_final_report.md").write_text(report, encoding="utf-8")
    print(report)
    exe = shutil.which("dot")
    if exe and not args.no_svg:
        r = subprocess.run([exe, "-Tsvg", str(dot), "-o", str(out / "flow_final.svg")],
                           capture_output=True, text=True, check=False)
        print("出力: " + (str(out / "flow_final.svg") if r.returncode == 0 else f"SVG失敗 {r.stderr.strip()}"))
    else:
        print(f"出力: {dot}（SVGは Graphviz の dot が必要）")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("prompt")
    p1.add_argument("skeleton")
    p1.add_argument("--inventory", default=None)
    p1.add_argument("--output", default="tools/architecture/output")
    p1.set_defaults(fn=cmd_prompt)
    p2 = sub.add_parser("check")
    p2.add_argument("skeleton")
    p2.add_argument("evidence")
    p2.add_argument("--output", default="tools/architecture/output")
    p2.add_argument("--hubs", nargs="*", default=["EventBus", "GameState"], help="経由の探索で素通りしないクラス")
    p2.add_argument("--no-svg", action="store_true")
    p2.set_defaults(fn=cmd_check)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()