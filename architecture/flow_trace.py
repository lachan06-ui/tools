#!/usr/bin/env python3
"""flow_trace.py -- 既存コードから「ここで何が起きるか」を、関数単位の因果チェーンとして取り出して図（SVG）にする。

骨格を人が書く必要はない。コードから次を機械で取り出す:
  call   : 関数 -> 関数   （autoload名.メソッド() / class_name.メソッド() / 同一クラス内の呼び出し）
  emit   : 関数 -> シグナル（signal.emit() / emit_signal("..")）
  handle : シグナル -> 関数（x.sig.connect(ハンドラ) の ハンドラ）
起点から辿ると「この処理が走ると、次に何が起きるか」のチェーンになる。
LLMは各関数に短い説明（ラベル）を付けるだけ。辺はLLMに作らせない。

使い方（プロジェクトのルートで。先に generate_charts_v2.py を実行して output/ を作っておくと色分けされる）:
  python tools/architecture/flow_trace.py entries                       # 起点の候補（到達できる関数が多い順）
  python tools/architecture/flow_trace.py trace --from EcologyManager.on_day_passed --depth 6
  python tools/architecture/flow_trace.py trace --from EcologyManager.on_day_passed --labels output/labels.json

trace の出力（output/）: trace_<起点>.svg / .dot / .txt（辺リスト file:line 付き）/ .json / _prompt.md（LLMにラベルを付けさせる依頼）

限界（クラス単位の静的解析）:
  - 変数に入ったインスタンスへの呼び出し（enemy.die() など）は、型が分からないので辿れない
  - ラムダのハンドラ、Callable(obj, "name") 形式、グループ呼び出しは辿らない
  - インナークラスの関数は対象外
  辿れていない可能性があるので、図は「少なくともこの経路はある」と読む。
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

FUNC_DEF = re.compile(r"^([ \t]*)(?:static[ \t]+)?func[ \t]+(\w+)[ \t]*\(")
CALL = re.compile(r"(?<![\w.$%&^])([A-Za-z_]\w*)\.(\w+)[ \t]*\(")
BARE = re.compile(r"(?<![\w.$%&^])(?:self\.)?([A-Za-z_]\w*)[ \t]*\(")
HANDLER_NEW = re.compile(r"\.connect\s*\(\s*(?:self\.)?([A-Za-z_]\w*)\s*[,)]")
HANDLER_OLD = re.compile(r"connect\s*\(\s*[\"']\w+[\"']\s*,\s*[\w.]+\s*,\s*[\"'](\w+)[\"']")
FONT = "Noto Sans CJK JP"
PALETTE = ["#DCEBFA", "#E3F4DC", "#FCE8D5", "#F2DDF3", "#FFF4C2", "#D8F0EE",
           "#F8D9D9", "#E6E6F5", "#EAEAEA", "#DDEBD0", "#F5E1C8", "#D5E3F0"]

LABEL_PROMPT = """# 依頼
次の関数それぞれが「何をするか」を、日本語20字以内で書いてください。
根拠は、関数名・シグネチャ・コメント・呼び先の名前だけです。コードの中身を想像で補わないでください。
読み取れない場合は「不明」と書いてください。

## 出力（JSONのみ。説明文・コードフェンスは書かない。出力は { で始まり } で終わる）
{"labels":{"Class.func":"20字以内の説明"}}

## ルール
- キーは、下の一覧にある関数ID（Class.func）をそのまま使う。一覧にないIDを書かない。
- 「〜する」の形で、動作を書く（例：種の個体数を日次で更新する）。

## 関数一覧
"""


def load_gc():
    spec = importlib.util.spec_from_file_location("gc2", Path(__file__).with_name("generate_charts_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def parse_funcs(clean: str):
    lines = clean.split("\n")
    funcs = []
    for i, l in enumerate(lines):
        m = FUNC_DEF.match(l)
        if not m or m.group(1) != "":  # トップレベルの関数だけ
            continue
        end = i
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == "":
                continue
            if len(lines[j]) - len(lines[j].lstrip(" \t")) == 0:
                break
            end = j
        funcs.append({"name": m.group(2), "start": i, "end": end})
    return lines, funcs


def doc_before(raw: list, idx: int) -> str:
    i, out = idx - 1, []
    while i >= 0 and raw[i].lstrip().startswith("@"):
        i -= 1
    while i >= 0 and raw[i].lstrip().startswith("#") and len(out) < 3:
        out.append(raw[i].strip().lstrip("#").strip())
        i -= 1
    return " / ".join(reversed(out))


def build(root: Path, out: Path) -> dict:
    gc = load_gc()
    gc.UID_MAP.clear()
    gc.UID_MAP.update(gc.build_uid_map(root))
    autoloads = gc.parse_autoloads(root)
    cj = out / "classes.json"
    domain_of_file = ({p: v.get("domain", "?") for p, v in json.loads(cj.read_text(encoding="utf-8")).items()}
                      if cj.exists() else {})

    files = {}
    for p in gc.iter_files(root, ("core", "data", "scenes"), ".gd"):
        text = p.read_text(encoding="utf-8", errors="replace")
        clean, keep = gc.mask(text, False), gc.mask(text, True)
        m = gc.CLASS_NAME.search(clean)
        lines, funcs = parse_funcs(clean)
        files[p.relative_to(root).as_posix()] = {
            "cls": m.group(1) if m else p.stem, "text": text, "clean": clean, "keep": keep,
            "lines": lines, "funcs": funcs, "raw": text.split("\n")}
    cls_file: dict[str, str] = {}
    for rel, f in files.items():
        cls_file.setdefault(f["cls"], rel)
    targets = {c: c for c in cls_file}
    for name, p in autoloads.items():
        if p in files:
            targets[name] = files[p]["cls"]
    func_ids = {f"{f['cls']}.{fn['name']}" for f in files.values() for fn in f["funcs"]}

    path_to_cls = {rel: f["cls"] for rel, f in files.items()}
    parent: dict[str, str | None] = {}
    for rel, f in files.items():
        mp, mn = gc.EXTENDS_PATH.search(f["keep"]), gc.EXTENDS_NAME.search(f["clean"])
        if mp:
            parent[f["cls"]] = path_to_cls.get(gc.res_to_rel(mp.group(1)))
        elif mn:
            parent[f["cls"]] = mn.group(1) if mn.group(1) in cls_file else None
    declared: dict[str, list] = defaultdict(list)
    for f in files.values():
        for m in gc.SIGNAL_DECL.finditer(f["clean"]):
            declared[m.group(1)].append(f["cls"])

    def ancestors(c):
        chain, seen = [], set()
        while c and c not in seen:
            chain.append(c)
            seen.add(c)
            c = parent.get(c)
        return chain

    def signal_owner(prefix, sig, cls):
        decl = declared.get(sig, [])
        if not decl:
            return None
        if prefix == "":
            return next((c for c in ancestors(cls) if c in decl), None)
        if "." not in prefix and prefix in targets:
            hit = next((c for c in ancestors(targets[prefix]) if c in decl), None)
            if hit:
                return hit
        return decl[0] if len(decl) == 1 else None

    nodes: dict[str, dict] = {}
    edges: set = set()

    def sig_node(owner, sig):
        sid = f"sig:{owner}.{sig}"
        if sid not in nodes:
            nodes[sid] = {"id": sid, "kind": "signal", "name": sig, "cls": owner,
                          "domain": domain_of_file.get(cls_file.get(owner, ""), "?")}
        return sid

    for rel, f in files.items():
        cls, lines = f["cls"], f["lines"]
        li = gc.LineIndex(f["text"])
        func_of_line: dict[int, str] = {}
        own = {fn["name"] for fn in f["funcs"]}
        for fn in f["funcs"]:
            fid = f"{cls}.{fn['name']}"
            nodes[fid] = {"id": fid, "kind": "func", "cls": cls, "file": rel, "line": fn["start"] + 1,
                          "sig": f["raw"][fn["start"]].strip()[:160],
                          "doc": doc_before(f["raw"], fn["start"]),
                          "domain": domain_of_file.get(rel, "?")}
            for i in range(fn["start"], fn["end"] + 1):
                func_of_line[i + 1] = fid
            for i in range(fn["start"] + 1, fn["end"] + 1):
                for m in CALL.finditer(lines[i]):
                    tgt = targets.get(m.group(1))
                    if tgt and tgt != cls and f"{tgt}.{m.group(2)}" in func_ids:
                        edges.add((fid, f"{tgt}.{m.group(2)}", "call", rel, i + 1))
                for m in BARE.finditer(lines[i]):
                    if m.group(1) in own and m.group(1) != fn["name"]:
                        edges.add((fid, f"{cls}.{m.group(1)}", "call", rel, i + 1))

        def emit(prefix, sig, pos):
            line = li.line(pos)
            owner, fid = signal_owner(prefix, sig, cls), func_of_line.get(line)
            if owner and fid:
                edges.add((fid, sig_node(owner, sig), "emit", rel, line))

        for m in gc.EMIT_NEW.finditer(f["clean"]):
            emit(gc.split_expr(m.group(1))[0], gc.split_expr(m.group(1))[1], m.start())
        for m in gc.EMIT_OLD.finditer(f["keep"]):
            emit(gc.split_expr((m.group(1) or "") + ".x")[0], m.group(2), m.start())

        def connect(prefix, sig, pos):
            owner = signal_owner(prefix, sig, cls)
            if not owner:
                return
            eol = f["keep"].find("\n", pos)
            seg = f["keep"][pos: eol if eol >= 0 else len(f["keep"])]
            h = HANDLER_NEW.search(seg) or HANDLER_OLD.search(seg)
            if h and h.group(1) in own:
                edges.add((sig_node(owner, sig), f"{cls}.{h.group(1)}", "handle", rel, li.line(pos)))

        for m in gc.CONNECT_NEW.finditer(f["clean"]):
            connect(gc.split_expr(m.group(1))[0], gc.split_expr(m.group(1))[1], m.start())
        for m in gc.CONNECT_OLD.finditer(f["keep"]):
            connect(gc.split_expr((m.group(1) or "") + ".x")[0], m.group(2), m.start())

    return {"nodes": nodes, "edges": sorted(edges)}


def adjacency(edges) -> dict:
    adj = defaultdict(list)
    for s, d, k, f, l in edges:
        adj[s].append((d, k, f, l))
    return adj


def bfs(adj: dict, seeds: list, depth: int, cap: int):
    dist = {s: 0 for s in seeds}
    q = deque(seeds)
    truncated = False
    while q:
        cur = q.popleft()
        if dist[cur] >= depth:
            continue
        for nxt, _, _, _ in adj.get(cur, ()):
            if nxt in dist:
                continue
            if len(dist) >= cap:
                truncated = True
                continue
            dist[nxt] = dist[cur] + 1
            q.append(nxt)
    return dist, truncated


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def to_dot(nodes, sel_edges, dist, seeds, labels):
    pal: dict[str, str] = {}
    lines = ['digraph "trace" {', '  rankdir="LR";', '  bgcolor="white";',
             f'  graph [fontname="{FONT}", pad="0.3"];',
             f'  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=11];',
             f'  edge [fontname="{FONT}", fontsize=9];']
    for nid in dist:
        n = nodes[nid]
        if n["kind"] == "signal":
            lines.append(f'  "{esc(nid)}" [label="{esc(n["name"])}", shape=ellipse, '
                         f'style="filled", fillcolor="#E0ECFF", fontsize=10];')
            continue
        fill = pal.setdefault(n["domain"], PALETTE[len(pal) % len(PALETTE)])
        text = esc(nid) + (r"\n" + esc(labels[nid]) if nid in labels else "")
        pen = ", penwidth=3" if nid in seeds else ""
        lines.append(f'  "{esc(nid)}" [label="{text}", fillcolor="{fill}"{pen}];')
    style = {"call": 'color="#64748B"', "emit": 'color="#2563EB", style=dashed',
             "handle": 'color="#2563EB"'}
    for s, d, k, _, _ in sel_edges:
        lines.append(f'  "{esc(s)}" -> "{esc(d)}" [{style[k]}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def resolve_seeds(names: list, nodes: dict, adj: dict) -> list:
    out = []
    for s in names:
        if s in nodes:
            out.append(s)
            continue
        cls = [n for n, v in nodes.items() if v["kind"] == "func" and v["cls"] == s and adj.get(n)]
        if cls:
            out += [n for n in cls if not nodes[n]["id"].split(".", 1)[1].startswith("_")] or cls
            continue
        near = [n for n in nodes if s.lower() in n.lower()][:10]
        raise SystemExit(f"[ERROR] 起点 '{s}' が見つかりません。近い候補: {near}")
    return out


def cmd_entries(args):
    root, out = Path(args.root).resolve(), Path(args.output)
    g = build(root, out)
    nodes, edges = g["nodes"], g["edges"]
    adj = adjacency(edges)
    has_in = {d for _, d, k, _, _ in edges if k in ("call", "handle")}
    rows = []
    for n, v in nodes.items():
        if v["kind"] == "func" and n not in has_in and adj.get(n):
            dist, _ = bfs(adj, [n], 6, 10 ** 6)
            rows.append((sum(1 for x in dist if nodes[x]["kind"] == "func"), n))
    rows.sort(key=lambda r: (-r[0], r[1]))
    print(f"関数 {sum(1 for v in nodes.values() if v['kind'] == 'func')} / シグナル "
          f"{sum(1 for v in nodes.values() if v['kind'] == 'signal')} / 辺 {len(edges)}")
    print("起点の候補（到達できる関数の数 / ID / 場所 / ドメイン）:")
    for reach, n in rows[: args.top]:
        v = nodes[n]
        print(f"  {reach:3d}  {n}  {v['file']}:{v['line']}  [{v['domain']}]")


def cmd_trace(args):
    root, out = Path(args.root).resolve(), Path(args.output)
    g = build(root, out)
    nodes, edges = g["nodes"], g["edges"]
    adj = adjacency(edges)
    seeds = resolve_seeds(args.seeds, nodes, adj)
    dist, truncated = bfs(adj, seeds, args.depth, args.cap)
    sel = [e for e in edges if e[0] in dist and e[1] in dist]
    labels: dict[str, str] = {}
    if args.labels:
        txt = re.sub(r"<think>.*?</think>", "", Path(args.labels).read_text(encoding="utf-8", errors="replace"), flags=re.S)
        i, j = txt.find("{"), txt.rfind("}")
        data = json.loads(txt[i:j + 1]) if i >= 0 else {}
        raw = data.get("labels", data)
        labels = {k: str(v)[:40] for k, v in raw.items() if k in dist and nodes.get(k, {}).get("kind") == "func"}
        ignored = [k for k in raw if k not in dist]
        if ignored:
            print(f"[WARN] ラベルのキーが図に存在しないので無視: {ignored[:10]}")
    base = re.sub(r"[^\w]+", "_", seeds[0] if len(seeds) == 1 else f"{args.seeds[0]}_etc").strip("_")
    dot = out / f"trace_{base}.dot"
    out.mkdir(parents=True, exist_ok=True)
    dot.write_text(to_dot(nodes, sel, dist, set(seeds), labels), encoding="utf-8")
    (out / f"trace_{base}.txt").write_text(
        "\n".join(f"{s} -{k}-> {d} @{f}:{l}" for s, d, k, f, l in sel) + "\n", encoding="utf-8")
    funcs = []
    for nid in dist:
        v = nodes[nid]
        if v["kind"] != "func":
            continue
        callees = sorted({d.replace("sig:", "シグナル ") for s, d, k, _, _ in sel if s == nid})
        funcs.append({"id": nid, "file": v["file"], "line": v["line"], "sig": v["sig"],
                      "doc": v["doc"], "callees": callees})
    (out / f"trace_{base}.json").write_text(json.dumps(funcs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prompt = [LABEL_PROMPT]
    for f in funcs:
        prompt.append(f"### {f['id']}  ({f['file']}:{f['line']})\nsig: {f['sig']}\n"
                      + (f"doc: {f['doc']}\n" if f["doc"] else "")
                      + (f"calls: {', '.join(f['callees'])}\n" if f["callees"] else ""))
    (out / f"trace_{base}_prompt.md").write_text("\n".join(prompt), encoding="utf-8")
    nf = sum(1 for n in dist if nodes[n]["kind"] == "func")
    print(f"起点 {seeds} / 深さ {args.depth}: 関数 {nf} / シグナル {len(dist) - nf} / 辺 {len(sel)}"
          + ("  [注意] 上限に達して打ち切り。--depth を下げるか --cap を上げてください" if truncated else ""))
    exe = shutil.which("dot")
    if exe and not args.no_svg:
        r = subprocess.run([exe, "-Tsvg", str(dot), "-o", str(out / f"trace_{base}.svg")],
                           capture_output=True, text=True, check=False)
        print("出力: " + (str(out / f"trace_{base}.svg") if r.returncode == 0 else f"SVG失敗 {r.stderr.strip()}"))
    else:
        print(f"出力: {dot}（SVGは Graphviz の dot が必要）")
    print(f"辺リスト: {out / f'trace_{base}.txt'} / ラベル依頼: {out / f'trace_{base}_prompt.md'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", default="tools/architecture/output")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("entries")
    p1.add_argument("--top", type=int, default=40)
    p1.set_defaults(fn=cmd_entries)
    p2 = sub.add_parser("trace")
    p2.add_argument("--from", dest="seeds", nargs="+", required=True, help="Class.func / Class")
    p2.add_argument("--depth", type=int, default=6)
    p2.add_argument("--cap", type=int, default=60)
    p2.add_argument("--labels", default=None)
    p2.add_argument("--no-svg", action="store_true")
    p2.set_defaults(fn=cmd_trace)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()