#!/usr/bin/env python3
"""check_flow.py -- ローカルLLMが出した「ゲームプレイのフロー」JSONを、事実(output/*.json)で検証してMermaidにする。

使い方（プロジェクトのルートで）:
  python tools/architecture/check_flow.py tools/architecture/output/flow.json

入力 flow.json（LLMの出力。前後に説明文や <think> があっても、最初の { から最後の } を読む）:
  {"nodes":[{"id":"n1","label":"敵が死ぬ","evidence":["Enemy","enemy_died"]}],
   "edges":[{"from":"n1","to":"n2","kind":"signal|direct|guess","evidence":"enemy_died"}],
   "unknown":["資料から読み取れなかった点"]}

検証ルール（LLMの主張は、スクリプトの事実と照合する）:
  - node.evidence は classes.json のクラス名 / signals.json のシグナル名にあるものだけ有効。
    有効なものが1つもないノードは「未検証」（黄色の点線）。
  - edge kind=signal : そのシグナルの 発行->受信 の辺が dependencies.json にあり、
                       始点クラスか終点クラスがノードの根拠に含まれること。
  - edge kind=direct : 根拠クラス間に直接参照（class_use / autoload_use / preload / group_call など）があること。
  - edge kind=guess  : 常に「推測」（点線）。
出力: output/flow_checked.mmd と output/flow_report.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DIRECT_KINDS = {"class_use", "autoload_use", "preload", "preload_scene", "scene_ref",
                "group_call", "extends"}


def extract_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < i:
        raise SystemExit("[ERROR] JSON が見つかりません")
    try:
        return json.loads(text[i:j + 1])
    except json.JSONDecodeError as e:
        raise SystemExit(f"[ERROR] JSON が壊れています: {e}")


def safe(s: str) -> str:
    return re.sub(r"\W", "_", str(s)) or "x"


def check_flow(data: dict, classes: dict, signals: list, deps: list):
    name_of = {p: (v.get("class_name") or Path(p).stem) for p, v in classes.items()}

    def nm(p):
        return name_of.get(p, Path(p).stem)

    known_classes = set(name_of.values())
    known_signals = {s["signal"] for s in signals}
    sig_edges = [(nm(e["source"]), nm(e["target"]), e.get("detail", ""))
                 for e in deps if e["kind"] == "signal"]
    direct_pairs = set()
    for e in deps:
        if e["kind"] in DIRECT_KINDS:
            a, b = nm(e["source"]), nm(e["target"])
            direct_pairs.add((a, b))
            direct_pairs.add((b, a))  # 流れの向きと依存の向きは逆になりうる

    nodes: dict[str, dict] = {}
    report = {"nodes_total": 0, "nodes_unverified": [], "bad_evidence": {},
              "edges_total": 0, "edges_verified": 0, "edges_guess": 0,
              "edges_unverified": [], "edges_invalid": [], "unknown": list(data.get("unknown", []))}
    for n in data.get("nodes", []):
        nid = str(n.get("id", "")).strip()
        if not nid:
            continue
        ev = [str(x).strip() for x in n.get("evidence", [])]
        cls = [x for x in ev if x in known_classes]
        sig = [x for x in ev if x in known_signals]
        bad = [x for x in ev if x not in known_classes and x not in known_signals]
        nodes[nid] = {"label": str(n.get("label", "")), "classes": cls, "signals": sig,
                      "ok": bool(cls or sig)}
        if bad:
            report["bad_evidence"][nid] = bad
        if not nodes[nid]["ok"]:
            report["nodes_unverified"].append(nid)
    report["nodes_total"] = len(nodes)

    lines = ["flowchart LR"]
    for nid, n in nodes.items():
        label = n["label"].replace('"', "'")
        ev = ", ".join(n["classes"] + n["signals"])
        if ev:
            label += f"<br/>({ev})"
        lines.append(f'  {safe(nid)}["{label}"]' + ("" if n["ok"] else ":::unverified"))

    for e in data.get("edges", []):
        a, b = str(e.get("from", "")), str(e.get("to", ""))
        kind = str(e.get("kind", "guess")).strip()
        ev = str(e.get("evidence", "")).strip()
        report["edges_total"] += 1
        if a not in nodes or b not in nodes:
            report["edges_invalid"].append(f"{a} -> {b}（存在しないノード）")
            continue
        sa, sb = safe(a), safe(b)
        if kind not in ("signal", "direct"):
            report["edges_guess"] += 1
            lines.append(f'  {sa} -.->|"推測"| {sb}')
            continue
        ca, cb = set(nodes[a]["classes"]), set(nodes[b]["classes"])
        why = ""
        if kind == "signal":
            if ev not in known_signals:
                why = f"シグナル '{ev}' が存在しない"
            else:
                cand = [(s, t) for s, t, d in sig_edges if d == ev]
                if not cand:
                    why = f"'{ev}' の発行→受信の辺が検出されていない"
                elif (not ca and not cb) or any(s in ca or t in cb for s, t in cand):
                    why = ""
                else:
                    why = "ノードの根拠クラスと、そのシグナルの発行側/受信側が合わない"
        else:
            if not any((x, y) in direct_pairs for x in ca for y in cb):
                why = "根拠クラス間の直接参照が検出されていない"
        if why:
            report["edges_unverified"].append(f"{a} -> {b} [{kind} {ev}]: {why}")
            lines.append(f'  {sa} -.->|"未検証:{kind}"| {sb}')
        else:
            report["edges_verified"] += 1
            label = f'|"{ev}"|' if kind == "signal" else ""
            lines.append(f"  {sa} -->{label} {sb}")
    lines.append("  classDef unverified stroke-dasharray: 4 3,fill:#fff4c2")
    return "\n".join(lines) + "\n", report


def render_report(r: dict) -> str:
    claimed = r["edges_total"] - r["edges_guess"] - len(r["edges_invalid"])
    out = ["# フロー図の検証結果", "",
           f"- ノード {r['nodes_total']} 個（根拠なし {len(r['nodes_unverified'])}）",
           f"- 辺 {r['edges_total']} 本: 検証済み {r['edges_verified']} / 推測 {r['edges_guess']}"
           f" / 未検証 {len(r['edges_unverified'])} / 不正 {len(r['edges_invalid'])}",
           f"- LLMが根拠ありと主張した辺のうち検証できた割合: "
           f"{r['edges_verified']}/{claimed}" if claimed else "- 根拠ありと主張した辺: 0"]
    if r["nodes_total"] > 15:
        out.append("- [注意] ノードが15個を超えています。粒度が細かすぎます")
    if r["nodes_unverified"]:
        out += ["", "## 根拠なしのノード", *[f"- {x}" for x in r["nodes_unverified"]]]
    if r["bad_evidence"]:
        out += ["", "## 実在しない名前（LLMが作ったもの）",
                *[f"- {k}: {', '.join(v)}" for k, v in r["bad_evidence"].items()]]
    if r["edges_unverified"]:
        out += ["", "## 未検証の辺", *[f"- {x}" for x in r["edges_unverified"]]]
    if r["edges_invalid"]:
        out += ["", "## 不正な辺", *[f"- {x}" for x in r["edges_invalid"]]]
    if r["unknown"]:
        out += ["", "## LLMが読み取れなかったと述べた点", *[f"- {x}" for x in r["unknown"]]]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("flow", help="LLMの出力（JSON）")
    ap.add_argument("--output", default="tools/architecture/output")
    args = ap.parse_args()
    out = Path(args.output)

    def load(name, default):
        p = out / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    classes, signals, deps = load("classes.json", {}), load("signals.json", []), load("dependencies.json", [])
    if not classes:
        raise SystemExit(f"[ERROR] {out}/classes.json がありません。先に generate_charts_v2.py を実行してください")
    data = extract_json(Path(args.flow).read_text(encoding="utf-8", errors="replace"))
    mmd, rep = check_flow(data, classes, signals, deps)
    (out / "flow_checked.mmd").write_text(mmd, encoding="utf-8")
    text = render_report(rep)
    (out / "flow_report.md").write_text(text, encoding="utf-8")
    print(text)
    print(f"出力: {out / 'flow_checked.mmd'}")


if __name__ == "__main__":
    main()