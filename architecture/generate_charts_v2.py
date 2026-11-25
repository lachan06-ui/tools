#!/usr/bin/env python3
# python -m pytest tools/architecture/tests -q
# python tools/architecture/generate_charts_v2.py --inventory tools\inventory\tr_1_inventory.md --tags tools\feature_tags.json --brief tools/project_brief.md
# (Get-Content tools/architecture/output/llm_flow_input.md -Raw).Length
"""
generate_charts_v2.py  --  Godot プロジェクトの「事実抽出」と「ドメイン単位の粗いフロー図」

generate_charts_fixed.py の置き換え。変更点:
  - tests/ addons/ を既定で除外（--with-tests で含める）
  - project.godot の [autoload] を読み、autoload 参照を本物の依存として解決
  - シグナルの「発行側 -> 受信側」を突き合わせ（EventBus 経由も追える）
  - 組み込みシグナル(pressed, timeout など)と $Node 参照のノイズを除去
  - .tscn は「ルートノードのスクリプト」を正しく取得（sub_resource の script を拾わない）
  - 出力 JSON から全文(source/clean)を除去
  - feature_tags.json があれば、ドメイン(タグ)単位に集約した粗い図を出力
      domains.mmd / domains.dot / domains.svg / domains.json
  - llm_flow_input.md : ローカルLLMにゲームプレイのフロー図を書かせるための事実資料
  - --focus クラス名 : そのクラスの周辺だけの図

Usage (プロジェクトのルートで):
  python tools/architecture/generate_charts_v2.py
  python tools/architecture/generate_charts_v2.py --inventory tr_1_inventory.md --brief tools/project_brief.md
  python tools/architecture/generate_charts_v2.py --focus EcologyManager --depth 1
  python tools/architecture/generate_charts_v2.py --hide debug core --min-direct 3
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import os
import shutil
import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path

DEFAULT_INCLUDE = ("core", "data", "scenes")
EXCLUDE_PARTS = {"addons", ".godot"}

# feature_tags.json に載っていないクラスのためのパス規則（先に書いたものが優先）
TAG_PATH_RULES = [
    ("ecology", "core/systems/ecology/"),
    ("enemy", "scenes/Characters/Enemies/"),
    ("npc", "scenes/Characters/NPC/"),
    ("spell", "scenes/Characters/Player/Spell/"),
    ("player", "scenes/Characters/Player/"),
    ("combat", "scenes/Systems/Combat/"),
    ("combat", "scenes/Systems/Targeting/"),
    ("feedback", "scenes/Systems/Indicator/"),
    ("status", "core/components/"),
    ("debug", "scenes/World/Debug/"),
    ("ui", "scenes/UI/"),
    ("map", "scenes/Map/"),
    ("map", "scenes/World/"),
    ("quest", "scenes/Quest/"),
    ("save", "scenes/Systems/SaveSystem"),
    ("item", "core/databases/"),
    ("core", "core/autoload/"),
]

DIRECT_KINDS = {"autoload_use", "class_use", "preload", "preload_scene", "scene_ref",
                "group_call"}

GRAPH_FONT = "Noto Sans CJK JP"
PALETTE = ["#DCEBFA", "#E3F4DC", "#FCE8D5", "#F2DDF3", "#FFF4C2", "#D8F0EE",
           "#F8D9D9", "#E6E6F5", "#EAEAEA", "#DDEBD0", "#F5E1C8", "#D5E3F0"]


# ============================================================
# 1. テキスト処理
# ============================================================

def mask(source: str, keep_strings: bool) -> str:
    """コメントを空白化。keep_strings=False なら文字列の中身も空白化。
    長さと改行位置は保つので、行番号は元ファイルと一致する。"""
    out: list[str] = []
    i, n = 0, len(source)
    in_str = False
    quote = ""
    triple = False
    while i < n:
        ch = source[i]
        if not in_str:
            if ch == "#":
                while i < n and source[i] != "\n":
                    out.append(" ")
                    i += 1
                continue
            if ch in "\"'":
                quote = ch
                triple = source.startswith(ch * 3, i)
                width = 3 if triple else 1
                in_str = True
                out.append(source[i:i + width] if keep_strings else " " * width)
                i += width
                continue
            out.append(ch)
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            seg = source[i:i + 2]
            if keep_strings:
                out.append(seg)
            else:
                out.append(" \n" if seg[1] == "\n" else "  ")
            i += 2
            continue
        if triple:
            if source.startswith(quote * 3, i):
                out.append(quote * 3 if keep_strings else "   ")
                i += 3
                in_str = False
                continue
        else:
            if ch == quote:
                out.append(ch if keep_strings else " ")
                i += 1
                in_str = False
                continue
            if ch == "\n":
                out.append("\n")
                i += 1
                in_str = False
                continue
        out.append(ch if (keep_strings or ch == "\n") else " ")
        i += 1
    return "".join(out)


class LineIndex:
    def __init__(self, text: str):
        self.starts = [0] + [m.end() for m in re.finditer("\n", text)]

    def line(self, pos: int) -> int:
        return bisect.bisect_right(self.starts, pos)


CLASS_NAME = re.compile(r"^[ \t]*class_name[ \t]+(\w+)", re.M)
EXTENDS_NAME = re.compile(
    r"^[ \t]*(?:class_name[ \t]+\w+[ \t]+)?extends[ \t]+([A-Za-z_]\w*)", re.M)
EXTENDS_PATH = re.compile(
    r"^[ \t]*(?:class_name[ \t]+\w+[ \t]+)?extends[ \t]+[\"'](res://[^\"']+)[\"']", re.M)
SIGNAL_DECL = re.compile(r"^[ \t]*signal[ \t]+(\w+)", re.M)
FUNC_DECL = re.compile(r"^[ \t]*(?:static[ \t]+)?func[ \t]+\w+", re.M)
PRELOAD = re.compile(
    r"\b(?:preload|load)\s*\(\s*[\"']((?:res|uid)://[^\"']+)[\"']\s*\)")
GET_NODE = re.compile(r"\bget_node(?:_or_null)?\s*\(\s*[\"']([^\"']+)[\"']")
EMIT_NEW = re.compile(r"(?<![\w.])([A-Za-z_][\w.]*)\.emit\s*\(")
EMIT_OLD = re.compile(
    r"(?<![\w.])(?:([A-Za-z_][\w.]*)\.)?emit_signal\s*\(\s*[\"'](\w+)[\"']")
CONNECT_NEW = re.compile(r"(?<![\w.])([A-Za-z_][\w.]*)\.connect\s*\(\s*(?=[^\s\"'])")
CONNECT_OLD = re.compile(
    r"(?<![\w.])(?:([A-Za-z_][\w.]*)\.)?connect\s*\(\s*[\"'](\w+)[\"']")
HEADER_LINE = re.compile(r"^[ \t]*(?:extends|class_name)\b[^\n]*", re.M)
ADD_GROUP = re.compile(r"(?<!\w)add_to_group\s*\(\s*([^,)\n]+)")
GROUP_USE = re.compile(
    r"\b(get_nodes_in_group|get_first_node_in_group|call_group|notify_group|is_in_group)"
    r"\s*\(\s*([^,)\n]+)")
GROUP_LIT = re.compile(r"^&?[\"']([^\"']+)[\"']$")
DYN_GET_NODE = re.compile(r"\b(get_node_or_null|get_node)\s*\(\s*([^\"'\s)^][^,)\n]*)")
DYN_LOAD = re.compile(r"(?<!func )(?<![\w.])(load)\s*\(\s*([^\"'\s)^][^,)\n]*)")
DYN_EMIT = re.compile(r"(?<!\w)(emit_signal)\s*\(\s*([^\"'\s)^][^,)\n]*)")
EXPORT_SCENE = re.compile(
    r"^[ \t]*@export(?:_\w+)?(?:\([^)]*\))?[ \t]+var[ \t]+(\w+)[ \t]*:[ \t]*PackedScene",
    re.M)


def split_expr(expr: str) -> tuple[str, str]:
    parts = expr.split(".")
    sig = parts[-1]
    prefix = ".".join(parts[:-1])
    if prefix == "self":
        prefix = ""
    elif prefix.startswith("self."):
        prefix = prefix[5:]
    return prefix, sig


# ============================================================
# 2. スキャン
# ============================================================

def iter_files(root: Path, include: tuple[str, ...], suffix: str):
    for name in include:
        base = root / name
        if not base.is_dir():
            continue
        for p in sorted(base.rglob(f"*{suffix}")):
            if EXCLUDE_PARTS & set(p.relative_to(root).parts):
                continue
            yield p


def scan_script(path: Path, root: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    clean = mask(text, False)
    keep = mask(text, True)
    li = LineIndex(text)
    rel = path.relative_to(root).as_posix()

    class_names = [m.group(1) for m in CLASS_NAME.finditer(clean)]
    extends = [{"value": m.group(1), "line": li.line(m.start())}
               for m in EXTENDS_PATH.finditer(keep)]
    extends += [{"value": m.group(1), "line": li.line(m.start())}
                for m in EXTENDS_NAME.finditer(clean)]

    emits = []
    for m in EMIT_NEW.finditer(clean):
        prefix, sig = split_expr(m.group(1))
        emits.append((prefix, sig, li.line(m.start())))
    for m in EMIT_OLD.finditer(keep):
        prefix, _ = split_expr((m.group(1) or "") + ".x")
        emits.append((prefix, m.group(2), li.line(m.start())))

    connects = []
    for m in CONNECT_NEW.finditer(clean):
        prefix, sig = split_expr(m.group(1))
        connects.append((prefix, sig, li.line(m.start())))
    for m in CONNECT_OLD.finditer(keep):
        prefix, _ = split_expr((m.group(1) or "") + ".x")
        connects.append((prefix, m.group(2), li.line(m.start())))

    group_adds, group_uses, dynamic = [], [], []
    for m in ADD_GROUP.finditer(keep):
        arg = m.group(1).strip()
        lit = GROUP_LIT.match(arg)
        if lit:
            group_adds.append((lit.group(1), li.line(m.start())))
        else:
            dynamic.append(("add_to_group", arg[:60], li.line(m.start())))
    for m in GROUP_USE.finditer(keep):
        arg = m.group(2).strip()
        lit = GROUP_LIT.match(arg)
        if lit:
            group_uses.append((m.group(1), lit.group(1), li.line(m.start())))
        else:
            dynamic.append((m.group(1), arg[:60], li.line(m.start())))
    for rx in (DYN_GET_NODE, DYN_LOAD, DYN_EMIT):
        for m in rx.finditer(keep):
            dynamic.append((m.group(1), m.group(2).strip()[:60], li.line(m.start())))

    return {
        "path": rel,
        "class_name": class_names[0] if class_names else "",
        "extends": extends,
        "signals": {m.group(1): li.line(m.start()) for m in SIGNAL_DECL.finditer(clean)},
        "func_count": len(FUNC_DECL.findall(clean)),
        "line_count": text.count("\n") + 1,
        "preloads": [(m.group(1), li.line(m.start())) for m in PRELOAD.finditer(keep)],
        "get_nodes": [(m.group(1), li.line(m.start())) for m in GET_NODE.finditer(keep)],
        "emits": emits,
        "connects": connects,
        "_clean": clean,
        "group_adds": group_adds, "group_uses": group_uses, "dynamic": dynamic,
        "export_scenes": [(m.group(1), li.line(m.start()))
                          for m in EXPORT_SCENE.finditer(clean)],
    }


ATTR = re.compile(r'(\w+)="([^"]*)"')
INSTANCE = re.compile(r'instance=ExtResource\("([^"]+)"\)')
SCRIPT_LINE = re.compile(r'^script\s*=\s*ExtResource\("([^"]+)"\)')


UID_MAP: dict[str, str] = {}
UID_HEADER = re.compile(r'uid="(uid://[^"]+)"')


def res_to_rel(p: str) -> str:
    if p.startswith("uid://"):
        return UID_MAP.get(p, p)
    return p[len("res://"):] if p.startswith("res://") else p


def build_uid_map(root: Path) -> dict[str, str]:
    """uid:// -> プロジェクト相対パス。*.gd.uid と、.tscn/.tres の1行目から作る。"""
    found: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_PARTS]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            if fn.endswith(".uid"):
                uid = p.read_text(encoding="utf-8", errors="replace").strip()
                if uid.startswith("uid://"):
                    found[uid] = rel[:-4]
            elif fn.endswith((".tscn", ".tres")):
                with p.open(encoding="utf-8", errors="replace") as f:
                    m = UID_HEADER.search(f.readline())
                if m:
                    found[m.group(1)] = rel
    return found


GROUPS_ATTR = re.compile(r'groups=\[([^\]]*)\]')
PROP_EXT = re.compile(r'^(\w+)\s*=\s*(ExtResource|SubResource)\("([^"]+)"\)')


def scan_scene(path: Path, root: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    ext: dict[str, dict] = {}
    nodes: list[dict] = []
    connections: list[dict] = []
    assigned: set[str] = set()
    subs: dict[str, str] = {}
    cur = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("[ext_resource"):
            a = dict(ATTR.findall(line))
            ext[a.get("id", "")] = {"type": a.get("type", ""), "path": a.get("path", "")}
            cur = None
        elif line.startswith("[node"):
            a = dict(ATTR.findall(line))
            inst = INSTANCE.search(line)
            gm = GROUPS_ATTR.search(line)
            cur = {"name": a.get("name", ""), "type": a.get("type", ""),
                   "parent": a.get("parent"),
                   "instance": inst.group(1) if inst else None, "script": None,
                   "groups": re.findall(r'"([^"]+)"', gm.group(1)) if gm else []}
            nodes.append(cur)
        elif line.startswith("[connection"):
            a = dict(ATTR.findall(line))
            connections.append({"signal": a.get("signal", ""), "from": a.get("from", ""),
                                "to": a.get("to", ""), "method": a.get("method", ""),
                                "line": lineno})
            cur = None
        elif line.startswith("["):
            if line.startswith("[sub_resource"):
                a = dict(ATTR.findall(line))
                subs[a.get("id", "")] = a.get("type", "")
            cur = None  # sub_resource など。ここの script= はノードのものではない
        elif cur is not None:
            m = SCRIPT_LINE.match(line)
            if m:
                cur["script"] = m.group(1)
            else:
                m = PROP_EXT.match(line)
                if m:
                    kind, rid = m.group(2), m.group(3)
                    if (kind == "ExtResource" and ext.get(rid, {}).get("type") == "PackedScene") \
                            or (kind == "SubResource" and subs.get(rid) == "PackedScene"):
                        assigned.add(m.group(1))

    def script_path(res_id):
        e = ext.get(res_id or "")
        if not e or not e["path"].endswith(".gd"):
            return None
        rel = res_to_rel(e["path"])
        return None if EXCLUDE_PARTS & set(Path(rel).parts) else rel

    def scene_rel(res_id):
        e = ext.get(res_id or "")
        if not e or not e["path"].endswith(".tscn"):
            return None
        rel = res_to_rel(e["path"])
        return None if EXCLUDE_PARTS & set(Path(rel).parts) else rel

    def npath(n):
        if n["parent"] is None:
            return "."
        return n["name"] if n["parent"] == "." else f'{n["parent"]}/{n["name"]}'

    root_node = next((n for n in nodes if n["parent"] is None), None)
    attached = []
    for n in nodes:
        sp = script_path(n["script"])
        if sp and sp not in attached:
            attached.append(sp)
    refs = []
    for e in ext.values():
        if e["type"] == "PackedScene" and e["path"].endswith(".tscn"):
            rel = res_to_rel(e["path"])
            if not (EXCLUDE_PARTS & set(Path(rel).parts)) and rel not in refs:
                refs.append(rel)
    return {
        "path": path.relative_to(root).as_posix(),
        "root_type": root_node["type"] if root_node else "",
        "root_script": script_path(root_node["script"]) if root_node else None,
        "root_instance": scene_rel(root_node["instance"]) if root_node else None,
        "scripts": attached,
        "scene_refs": refs,
        "node_count": len(nodes),
        "nodes": {npath(n): {"script": script_path(n["script"]),
                             "instance": scene_rel(n["instance"]),
                             "groups": n["groups"]} for n in nodes},
        "connections": connections,
        "assigned_scene_props": sorted(assigned),
    }


def scene_node_script(sc: dict, node_path: str, scenes: dict):
    """シーン内のノードに対応するスクリプト。インスタンスならその子シーンのルートスクリプト。"""
    n = sc["nodes"].get(node_path)
    if not n:
        return None
    if n["script"]:
        return n["script"]
    if n["instance"] and n["instance"] in scenes:
        return scenes[n["instance"]]["root_script"]
    return None

AUTOLOAD_LINE = re.compile(r'(\w+)\s*=\s*"\*?((?:res|uid)://[^"]+)"')


def parse_autoloads(root: Path) -> dict[str, str]:
    p = root / "project.godot"
    result: dict[str, str] = {}
    if not p.exists():
        return result
    section = None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            continue
        if section == "autoload":
            m = AUTOLOAD_LINE.match(s)
            if m:
                rel = res_to_rel(m.group(2))
                if rel.startswith("uid://"):
                    print(f"[WARN] autoload {m.group(1)}: {rel} をパスに解決できません")
                    continue
                result[m.group(1)] = rel
    return result

# ============================================================
# 3. 依存関係
# ============================================================

class EdgeSet:
    def __init__(self):
        self.items: dict[tuple, dict] = {}

    def add(self, source, target, kind, line=0, detail="", **extra):
        if source == target:
            return
        key = (source, target, kind, detail)
        if key in self.items:
            self.items[key]["count"] += 1
            return
        edge = {"source": source, "target": target, "kind": kind,
                "line": line, "detail": detail, "count": 1}
        edge.update(extra)
        self.items[key] = edge

    def list(self):
        return sorted(self.items.values(),
                      key=lambda e: (e["source"], e["target"], e["kind"], e["detail"]))


def display_name(path: str, scripts: dict) -> str:
    if path in scripts and scripts[path]["class_name"]:
        return scripts[path]["class_name"]
    return Path(path).stem


def ancestors(path, scripts, name_to_path, path_index):
    chain, seen, cur = [path], {path}, path
    while True:
        nxt = None
        for e in scripts[cur]["extends"]:
            t = e["value"]
            cand = path_index.get(t) if t.startswith("res://") else name_to_path.get(t)
            if cand and cand in scripts:
                nxt = cand
                break
        if not nxt or nxt in seen:
            break
        chain.append(nxt)
        seen.add(nxt)
        cur = nxt
    return chain


def build_edges(scripts, scenes, autoloads, name_to_path, path_index, hubs):
    edges = EdgeSet()
    unresolved: list[dict] = []
    autoload_names = set(autoloads)

    # --- extends / preload / get_node ---
    for path, rec in scripts.items():
        for e in rec["extends"]:
            t = e["value"]
            target = path_index.get(t) if t.startswith("res://") else name_to_path.get(t)
            if target in scripts:
                edges.add(path, target, "extends", e["line"])
            elif t.startswith("res://"):
                unresolved.append({"source": path, "target": t, "kind": "extends", "line": e["line"]})
        for res, line in rec["preloads"]:
            rel = res_to_rel(res)
            if rel.endswith(".gd"):
                if rel in scripts:
                    edges.add(path, rel, "preload", line)
                elif not (EXCLUDE_PARTS & set(Path(rel).parts)):
                    unresolved.append({"source": path, "target": res, "kind": "preload_missing", "line": line})
            elif rel.endswith(".tscn"):
                if rel in scenes:
                    edges.add(path, rel, "preload_scene", line)
                elif not (EXCLUDE_PARTS & set(Path(rel).parts)):
                    unresolved.append({"source": path, "target": res, "kind": "preload_missing", "line": line})
        for s, line in rec["get_nodes"]:
            name = s.rstrip("/").split("/")[-1]
            if name in autoload_names and name_to_path.get(name) in scripts:
                edges.add(path, name_to_path[name], "autoload_use", line, detail="get_node")

    # --- 識別子による使用（class_name / autoload） ---
    names = sorted(name_to_path, key=len, reverse=True)
    if names:
        ident = re.compile(r"(?<![\w$%&^./])(" + "|".join(map(re.escape, names)) + r")\b")
        for path, rec in scripts.items():
            text = HEADER_LINE.sub(lambda m: " " * len(m.group(0)), rec["_clean"])
            li = LineIndex(text)
            for m in ident.finditer(text):
                name = m.group(1)
                target = name_to_path[name]
                if target == path or target not in scripts:
                    continue
                kind = "autoload_use" if name in autoload_names else "class_use"
                edges.add(path, target, kind, li.line(m.start()))

    # --- シーン ---
    for spath, sc in scenes.items():
        for sp in sc["scripts"]:
            if sp in scripts:
                edges.add(spath, sp, "scene_script")
        for ref in sc["scene_refs"]:
            if ref in scenes:
                edges.add(spath, ref, "scene_ref")

    # --- グループ / 動的呼び出し / @export PackedScene ---
    members: dict[str, set[str]] = defaultdict(set)
    for path, rec in scripts.items():
        for g, _ in rec["group_adds"]:
            members[g].add(path)
    for sc in scenes.values():
        for node in sc["nodes"].values():
            if not node["groups"]:
                continue
            tgt = node["script"] or (scenes[node["instance"]]["root_script"]
                                     if node["instance"] in scenes else None)
            if tgt in scripts:
                for g in node["groups"]:
                    members[g].add(tgt)
    assigned: set[str] = set()
    for sc in scenes.values():
        assigned.update(sc["assigned_scene_props"])
    for path, rec in scripts.items():
        for fn, g, line in rec["group_uses"]:
            if g.startswith("_"):
                continue
            ms = members.get(g)
            if not ms:
                near = sorted(k for k in members if k.lower() == g.lower())
                unresolved.append({"source": path, "target": g, "kind": "group_no_member",
                                   "line": line, "similar": near})
                continue
            kind = "group_check" if fn == "is_in_group" else "group_call"
            for m in sorted(ms):
                edges.add(path, m, kind, line, detail=g)
        for fn, arg, line in rec["dynamic"]:
            unresolved.append({"source": path, "target": arg,
                               "kind": f"dynamic_{fn}", "line": line})
        if rec["export_scenes"]:
            is_res = any(e["value"] == "Resource"
                         for a in ancestors(path, scripts, name_to_path, path_index)
                         for e in scripts[a]["extends"])
        for var, line in rec["export_scenes"]:
            if var not in assigned:
                kind = "export_scene_in_resource" if is_res else "export_scene_not_in_tscn"
                unresolved.append({"source": path, "target": var, "kind": kind, "line": line})

    # --- シグナル ---
    signal_entries, sig_unresolved = analyze_signals(
        scripts, autoloads, name_to_path, path_index, hubs, edges, scenes)
    unresolved += sig_unresolved
    return edges, signal_entries, unresolved


def analyze_signals(scripts, autoloads, name_to_path, path_index, hubs, edges, scenes):
    declared_in: dict[str, list[str]] = defaultdict(list)
    for p, rec in scripts.items():
        for s in rec["signals"]:
            declared_in[s].append(p)
    anc = {p: ancestors(p, scripts, name_to_path, path_index) for p in scripts}
    autoload_script = {n: name_to_path.get(n) for n in autoloads}
    hub_paths = {name_to_path.get(h) for h in hubs if name_to_path.get(h)}

    def resolve(src, prefix, sig):
        decl = declared_in.get(sig, [])
        if not decl:
            return None, "not_project_signal", []
        if prefix == "":
            for p in anc[src]:
                if p in decl:
                    return p, "own", []
            return None, "foreign_bare", decl  # 素の emit/connect は自分の継承チェーンのシグナルだけ
        if "." not in prefix and autoload_script.get(prefix) in scripts:
            for p in anc[autoload_script[prefix]]:
                if p in decl:
                    return p, "autoload", []
        if len(decl) == 1:
            return decl[0], "by_name", []
        return None, "ambiguous", decl

    entries: dict[tuple, dict] = {}

    def entry(owner, sig):
        key = (owner, sig)
        if key not in entries:
            entries[key] = {"owner": owner, "signal": sig,
                            "declared_line": scripts[owner]["signals"].get(sig, 0),
                            "emitters": set(), "listeners": {}, "by_name": 0}
        return entries[key]

    for p, rec in scripts.items():
        for s in rec["signals"]:
            entry(p, s)

    unresolved: list[dict] = []
    for src, rec in scripts.items():
        for prefix, sig, line in rec["emits"]:
            owner, how, cands = resolve(src, prefix, sig)
            if owner:
                e = entry(owner, sig)
                e["emitters"].add(src)
                e["by_name"] += how == "by_name"
            elif how in ("ambiguous", "foreign_bare"):
                unresolved.append({"source": src, "target": sig, "kind": f"{how}_signal_emit",
                                   "line": line, "candidates": cands})
        for prefix, sig, line in rec["connects"]:
            owner, how, cands = resolve(src, prefix, sig)
            if owner:
                e = entry(owner, sig)
                e["listeners"].setdefault(src, line)
                e["by_name"] += how == "by_name"
            elif how in ("ambiguous", "foreign_bare"):
                unresolved.append({"source": src, "target": sig, "kind": f"{how}_signal_connect",
                                   "line": line, "candidates": cands})

    # --- .tscn の [connection] ---
    for sc in scenes.values():
        for c in sc["connections"]:
            src = scene_node_script(sc, c["from"], scenes)
            dst = scene_node_script(sc, c["to"], scenes)
            if not src or not dst or src not in scripts or dst not in scripts:
                continue
            owner = next((p for p in anc[src] if c["signal"] in scripts[p]["signals"]), None)
            if owner is None:
                continue  # 組み込みシグナルは対象外
            entry(owner, c["signal"])["listeners"].setdefault(dst, c["line"])

    for (owner, sig), e in entries.items():
        for lis, line in e["listeners"].items():
            if lis != owner:
                edges.add(lis, owner, "signal_listen", line, detail=sig)
        if e["emitters"]:
            for em in e["emitters"]:
                for lis, line in e["listeners"].items():
                    if em != lis:
                        edges.add(em, lis, "signal", line, detail=sig)
        elif owner not in hub_paths:
            for lis, line in e["listeners"].items():
                if owner != lis:
                    edges.add(owner, lis, "signal", line, detail=sig, inferred_emitter=True)
    return entries, unresolved


# ============================================================
# 4. ドメイン集約
# ============================================================

def load_tags(path: Path | None) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("classes", {})
    return {}


def domain_of(path, scripts, tag_classes):
    name = display_name(path, scripts)
    entry = tag_classes.get(name)
    if entry and entry.get("tags"):
        return entry["tags"][0]  # 先頭タグを主ドメインとして扱う
    for tag, prefix in TAG_PATH_RULES:
        if prefix in path:
            return tag
    return "untagged"


def build_domain_graph(edges, scripts, scenes, tag_classes, hide, min_direct, hub_paths):
    def to_script(p):
        if p in scripts:
            return p
        if p in scenes:
            return scenes[p]["root_script"]
        return None

    dom = {p: domain_of(p, scripts, tag_classes) for p in scripts}
    groups: dict[tuple, dict] = {}
    for e in edges:
        if e["kind"] == "signal":
            group = "event"
        elif e["kind"] in DIRECT_KINDS:
            group = "direct"
        else:
            continue
        s, t = to_script(e["source"]), to_script(e["target"])
        if not s or not t:
            continue
        if group == "direct" and (s in hub_paths or t in hub_paths):
            continue
        sd, td = dom[s], dom[t]
        if sd == td or sd in hide or td in hide:
            continue
        g = groups.setdefault((sd, td, group), {"pairs": set(), "signals": Counter()})
        g["pairs"].add((s, t))
        if group == "event":
            g["signals"][e["detail"]] += 1

    out_edges = []
    for (sd, td, group), g in sorted(groups.items()):
        weight = len(g["pairs"])
        if group == "direct" and weight < min_direct:
            continue
        examples = [f"{display_name(a, scripts)}->{display_name(b, scripts)}"
                    for a, b in sorted(g["pairs"])[:4]]
        out_edges.append({
            "source": sd, "target": td, "group": group, "weight": weight,
            "signals": [n for n, _ in g["signals"].most_common()],
            "examples": examples,
        })

    members: dict[str, list[str]] = defaultdict(list)
    for p, d in dom.items():
        if d not in hide:
            members[d].append(display_name(p, scripts))
    nodes = {d: sorted(set(v)) for d, v in sorted(members.items())}
    return nodes, out_edges, dom


def safe_id(name: str) -> str:
    return re.sub(r"\W", "_", name)


def write_edges_txt(edge_list, unresolved, path: Path):
    out = []
    for e in sorted(edge_list, key=lambda e: (e["kind"], e["source"], e["target"], e["detail"])):
        where = e["target"] if e["kind"] == "signal" else e["source"]  # signal の line は受信側
        loc = f" @{where}:{e['line']}" if e["line"] else ""
        det = f" ({e['detail']})" if e["detail"] else ""
        out.append(f"[{e['kind']}] {e['source']} -> {e['target']}{det}{loc}")
    for u in sorted(unresolved, key=lambda u: (u["kind"], u["source"], u["line"])):
        out.append(f"[?{u['kind']}] {u['source']}:{u['line']} {u['target']}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_domain_mermaid(nodes, edges, path: Path):
    lines = ["flowchart LR"]
    for d, cls in nodes.items():
        lines.append(f'  {safe_id(d)}["{d} ({len(cls)})"]')
    for e in edges:
        s, t = safe_id(e["source"]), safe_id(e["target"])
        if e["group"] == "event":
            label = ", ".join(e["signals"][:3]) + (" …" if len(e["signals"]) > 3 else "")
            lines.append(f'  {s} -.->|"{label}"| {t}')
        else:
            lines.append(f'  {s} -->|"{e["weight"]}"| {t}')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dot_escape(v: str) -> str:
    return v.replace("\\", "\\\\").replace('"', '\\"')


def dot_header(title):
    return [f'digraph "{dot_escape(title)}" {{', '  rankdir="LR";', '  bgcolor="transparent";',
            f'  graph [fontname="{GRAPH_FONT}", pad="0.3"];',
            f'  node [shape=box, style="rounded,filled", fontname="{GRAPH_FONT}", fontsize=11];',
            f'  edge [fontname="{GRAPH_FONT}", fontsize=9];']


def write_domain_dot(nodes, edges, path: Path):
    color = {d: PALETTE[i % len(PALETTE)] for i, d in enumerate(nodes)}
    lines = dot_header("domains")
    for d, cls in nodes.items():
        lines.append(f'  "{safe_id(d)}" [label="{dot_escape(d)}\\n({len(cls)})", fillcolor="{color[d]}"];')
    for e in edges:
        s, t = safe_id(e["source"]), safe_id(e["target"])
        if e["group"] == "event":
            label = ", ".join(e["signals"][:3]) + (" …" if len(e["signals"]) > 3 else "")
            lines.append(f'  "{s}" -> "{t}" [style=dashed, color="#2563EB", fontcolor="#2563EB", label="{dot_escape(label)}"];')
        else:
            pw = min(1 + e["weight"] / 3, 5)
            lines.append(f'  "{s}" -> "{t}" [color="#64748B", penwidth={pw:.1f}, label="{e["weight"]}"];')
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_purposes(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    cur = field = None
    for raw in text.splitlines():
        line = raw.replace("\r", "").strip()
        if line.startswith("# Layer"):
            cur = field = None
        elif line.startswith("## "):
            cur, field = line[3:].strip(), None
        elif line.startswith("### ") and cur:
            field = line[4:].strip()
        elif cur and field == "Purpose" and line.startswith("- ") and cur not in result:
            v = line[2:].replace("**", "").strip()
            if v.lower() not in {"", "none", "not found", "placeholder"}:
                result[cur] = v
    return result


FLOW_PROMPT = """# 依頼
下の【事実資料】だけを根拠に、このゲームの「プレイヤー視点のゲームプレイフロー」を、次のJSONだけで出力してください。
説明文・Markdown・コードフェンスは書かないでください。出力は { で始まり } で終わります。

## 出力スキーマ
{"nodes":[{"id":"n1","label":"出来事を日本語で15字程度","evidence":["資料に出てくるクラス名またはシグナル名"]}],
 "edges":[{"from":"n1","to":"n2","kind":"signal または direct または guess","evidence":"シグナル名（kind が signal のときだけ）"}],
 "unknown":["資料から読み取れなかった点"]}

## ルール
- ノードは最大15個。クラス名ではなく「出来事」を書く（例：敵が死ぬ／死体が残る／栄養が土に戻る）。
- evidence は、資料にある名前をそのまま写す。資料にない名前を書かない。作らない。
- 辺の kind:
  - signal: 資料の「ドメイン間のイベント（シグナル）」にある関係。evidence にそのシグナル名
  - direct: 資料の「ドメイン間の直接呼び出し」にある関係
  - guess: 資料に根拠がないが、流れとして必要なもの
- 迷ったら guess にする。根拠を捏造しない。
- 資料から読み取れなかった点は unknown に書く。

"""


def write_llm_input(path, nodes, edges, scripts, dom, edge_list, purposes, brief_text):
    lines = [FLOW_PROMPT, "# 事実資料", ""]
    if brief_text:
        lines += ["## ゲーム概要", brief_text.strip(), ""]
    lines.append("## ドメインと所属クラス")
    for d, cls in nodes.items():
        lines.append(f"### {d}")
        for c in cls:
            p = purposes.get(c, "")
            lines.append(f"- {c}" + (f": {p[:90]}" if p else ""))
        lines.append("")

    lines.append("## ドメイン間のイベント（シグナル）")
    ev = [e for e in edge_list if e["kind"] == "signal"]
    seen = set()
    for e in ev:
        s = e["source"] if e["source"] in scripts else None
        t = e["target"] if e["target"] in scripts else None
        if not s or not t or dom[s] == dom[t] or dom[s] not in nodes or dom[t] not in nodes:
            continue
        key = (dom[s], dom[t], e["detail"])
        if len(seen) >= 80:
            break
        if key in seen:
            continue
        seen.add(key)
        mark = "（発行元は推定）" if e.get("inferred_emitter") else ""
        lines.append(f"- {dom[s]} → {dom[t]}: {e['detail']}  [{display_name(s, scripts)} → {display_name(t, scripts)}]{mark}")
    if not seen:
        lines.append("- （検出なし）")
    lines.append("")

    lines.append("## ドメイン間の直接呼び出し（クラス対の数が多い順）")
    for e in sorted([e for e in edges if e["group"] == "direct"], key=lambda x: -x["weight"])[:40]:
        lines.append(f"- {e['source']} → {e['target']} ({e['weight']}): {', '.join(e['examples'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ============================================================
# 5. focus 図
# ============================================================

def write_focus(edge_list, scripts, scenes, name_to_path, tag_classes, focus, depth, out: Path,
                hub_paths=frozenset()):
    center = name_to_path.get(focus)
    if center is None:
        for p in scripts:
            if Path(p).stem == focus or display_name(p, scripts) == focus:
                center = p
                break
    if center is None:
        print(f"[WARN] --focus: '{focus}' が見つかりません")
        return None

    def to_script(p):
        if p in scripts:
            return p
        return scenes[p]["root_script"] if p in scenes else None

    adj = defaultdict(set)
    shown = [e for e in edge_list
             if e["kind"] in DIRECT_KINDS | {"signal", "extends"}]
    for e in shown:
        s, t = to_script(e["source"]), to_script(e["target"])
        if s and t and s != t:
            adj[s].add(t)
            adj[t].add(s)
    dist = {center: 0}
    q = deque([center])
    while q:
        cur = q.popleft()
        if dist[cur] >= depth or (cur in hub_paths and cur != center):
            continue
        for n in adj[cur]:
            if n not in dist:
                dist[n] = dist[cur] + 1
                q.append(n)
    if len(dist) > 60:
        print(f"[WARN] --focus {focus}: {len(dist)} ノード。--depth を下げると読みやすくなります")

    domains = sorted({domain_of(p, scripts, tag_classes) for p in dist})
    color = {d: PALETTE[i % len(PALETTE)] for i, d in enumerate(domains)}
    lines = dot_header(f"focus {focus}")
    for p in dist:
        d = domain_of(p, scripts, tag_classes)
        pen = ', penwidth=3' if p == center else ''
        lines.append(f'  "{dot_escape(p)}" [label="{dot_escape(display_name(p, scripts))}\\n[{d}]", fillcolor="{color[d]}"{pen}];')
    done = set()
    for e in shown:
        s, t = to_script(e["source"]), to_script(e["target"])
        if s in dist and t in dist and s != t:
            key = (s, t, e["kind"], e["detail"])
            if key in done:
                continue
            done.add(key)
            if e["kind"] == "signal":
                lines.append(f'  "{dot_escape(s)}" -> "{dot_escape(t)}" [style=dashed, color="#2563EB", fontcolor="#2563EB", label="{dot_escape(e["detail"])}"];')
            elif e["kind"] == "extends":
                lines.append(f'  "{dot_escape(s)}" -> "{dot_escape(t)}" [arrowhead=empty, color="#94A3B8"];')
            else:
                lines.append(f'  "{dot_escape(s)}" -> "{dot_escape(t)}" [color="#64748B"];')
    lines.append("}")
    name = f"focus_{display_name(center, scripts)}"
    (out / f"{name}.dot").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def generate_svg(output: Path, names: list[str]) -> list[str]:
    exe = shutil.which("dot")
    if exe is None:
        print("[INFO] Graphviz 'dot' が無いので SVG は省略（.mmd は Mermaid で表示できます）")
        return []
    made = []
    for n in names:
        r = subprocess.run([exe, "-Tsvg", str(output / f"{n}.dot"), "-o", str(output / f"{n}.svg")],
                           capture_output=True, text=True, check=False)
        if r.returncode == 0:
            made.append(f"{n}.svg")
        else:
            print(f"[ERROR] {n}: {r.stderr.strip()}")
    return made


# ============================================================
# 6. main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", default="tools/architecture/output")
    ap.add_argument("--include", nargs="*", default=list(DEFAULT_INCLUDE))
    ap.add_argument("--with-tests", action="store_true")
    ap.add_argument("--tags", default=None, help="feature_tags.json（既定: このスクリプトと同じフォルダ、または tools/）")
    ap.add_argument("--inventory", default=None, help="tr_1_inventory.md（Purpose を資料に入れる）")
    ap.add_argument("--brief", default=None, help="project_brief.md（概要を資料に入れる）")
    ap.add_argument("--hide", nargs="*", default=["debug"], help="図から除くドメイン")
    ap.add_argument("--hub", nargs="*", default=["EventBus"], help="ハブ扱いのautoload")
    ap.add_argument("--min-direct", type=int, default=2, help="直接呼び出しの線を出す最小クラス対数")
    ap.add_argument("--focus", default=None)
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--no-svg", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.output)
    out = out if out.is_absolute() else root / out
    out.mkdir(parents=True, exist_ok=True)

    include = tuple(args.include) + (("tests",) if args.with_tests else ())
    scripts = {}
    for p in iter_files(root, include, ".gd"):
        rec = scan_script(p, root)
        scripts[rec["path"]] = rec
    scenes = {}
    for p in iter_files(root, include, ".tscn"):
        rec = scan_scene(p, root)
        scenes[rec["path"]] = rec

    UID_MAP.update(build_uid_map(root))

    for _ in range(5):
        for sc in scenes.values():
            if not sc["root_script"] and sc.get("root_instance") in scenes:
                sc["root_script"] = scenes[sc["root_instance"]]["root_script"]

    autoloads = parse_autoloads(root)
    if not autoloads:
        for p in scripts:
            if p.startswith("core/autoload/"):
                autoloads[Path(p).stem] = p
        if autoloads:
            print("[INFO] project.godot に [autoload] が無いので core/autoload/ から推定しました")
    for n, p in list(autoloads.items()):
        if p.endswith(".tscn"):
            rs = scenes.get(p, {}).get("root_script")
            if rs:
                autoloads[n] = rs
            else:
                del autoloads[n]

    path_index = {"res://" + p: p for p in scripts}
    name_to_path: dict[str, str] = {}
    for p, rec in scripts.items():
        if rec["class_name"]:
            name_to_path[rec["class_name"]] = p
    for n, p in autoloads.items():
        if p in scripts:
            name_to_path[n] = p

    missing = [n for n, p in autoloads.items() if p not in scripts]
    if missing:
        print("[WARN] autoload がスキャン対象外または見つからない:", ", ".join(missing))

    edges, signal_entries, unresolved = build_edges(
        scripts, scenes, autoloads, name_to_path, path_index, set(args.hub))
    edge_list = edges.list()
    for rec in scripts.values():
        rec.pop("_clean", None) if False else None  # _clean は後で消す

    # --- tags / domains ---
    tags_file = Path(args.tags) if args.tags else None
    if tags_file is not None and not tags_file.is_absolute():
        tags_file = root / tags_file
    if tags_file is None:
        for cand in (Path(__file__).with_name("feature_tags.json"),
                     root / "tools" / "feature_tags.json", root / "feature_tags.json"):
            if cand.exists():
                tags_file = cand
                break
    if tags_file is not None and not tags_file.exists():
        raise SystemExit(f"[ERROR] --tags {tags_file} が存在しません")
    tag_classes = load_tags(tags_file)
    if tags_file is None:
        print("[WARN] feature_tags.json が見つかりません。パス規則だけで分類します（--tags で指定）")
    else:
        print(f"[INFO] tags: {tags_file} ({len(tag_classes)} classes)")

    hub_paths = {name_to_path[h] for h in args.hub if h in name_to_path}
    nodes, domain_edges, dom = build_domain_graph(
        edge_list, scripts, scenes, tag_classes, set(args.hide), args.min_direct, hub_paths)
    
    existing = {display_name(p, scripts) for p in scripts}
    stale_tags = sorted(n for n in tag_classes if n not in existing)

    vocab = None
    if tags_file is not None:
        td = json.loads(tags_file.read_text(encoding="utf-8")).get("tag_descriptions", {})
        vocab = {k for k, v in td.items() if isinstance(v, str)}
    out_of_vocab = (sorted({d for d in dom.values() if d != "untagged" and d not in vocab})
                    if vocab is not None else "tag_descriptions なし")
    moved_tags = sorted(n for n, e in tag_classes.items()
                        if n in existing and e.get("file") and e["file"] not in scripts)
    untagged_classes = sorted(display_name(p, scripts) for p, d in dom.items() if d == "untagged")
    out_of_vocab = (sorted({d for d in dom.values() if d != "untagged" and d not in vocab}) if vocab is not None else "tag_descriptions なし")
    moved_tags = sorted(n for n, e in tag_classes.items() if n in existing and e.get("file") and e["file"] not in scripts)

    # --- 出力 ---
    def dump(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    classes_out = {}
    for p, rec in scripts.items():
        classes_out[p] = {
            "class_name": rec["class_name"], "domain": dom[p],
            "extends": [e["value"] for e in rec["extends"]],
            "signals": rec["signals"], "func_count": rec["func_count"], "line_count": rec["line_count"],
        }
    signals_out = []
    for (owner, sig), e in sorted(entries_items(signal_entries)):
        note = []
        if not e["emitters"]:
            note.append("発行元が検出されない")
        if not e["listeners"]:
            note.append("受信側が検出されない")
        signals_out.append({
            "owner": owner, "signal": sig, "declared_line": e["declared_line"],
            "emitters": sorted(e["emitters"]), "listeners": sorted(e["listeners"]),
            "resolved_by_name_only": e["by_name"], "note": note,
        })
    scenes_out = {p: {k: v for k, v in s.items() if k != "path"} for p, s in scenes.items()}

    dump("classes.json", classes_out)
    dump("dependencies.json", edge_list)
    dump("signals.json", signals_out)
    dump("scenes.json", scenes_out)
    dump("unresolved.json", unresolved)
    dump("domains.json", {"nodes": nodes, "edges": domain_edges})

    write_domain_mermaid(nodes, domain_edges, out / "domains.mmd")
    write_domain_dot(nodes, domain_edges, out / "domains.dot")
    write_edges_txt(edge_list, unresolved, out / "edges.txt")

    purposes = {}
    if args.inventory and Path(args.inventory).exists():
        purposes = parse_purposes(Path(args.inventory).read_text(encoding="utf-8", errors="replace"))
    brief = ""
    if args.brief and Path(args.brief).exists():
        brief = Path(args.brief).read_text(encoding="utf-8", errors="replace")
    write_llm_input(out / "llm_flow_input.md", nodes, domain_edges, scripts, dom, edge_list, purposes, brief)

    dot_names = ["domains"]
    if args.focus:
        name = write_focus(edge_list, scripts, scenes, name_to_path, tag_classes,
                           args.focus, args.depth, out, hub_paths)
        if name:
            dot_names.append(name)
    svgs = [] if args.no_svg else generate_svg(out, dot_names)

    kinds = Counter(e["kind"] for e in edge_list)
    report = {
        "script_count": len(scripts), "scene_count": len(scenes),
        "autoloads": sorted(autoloads), "edge_kinds": dict(kinds),
        "signals_declared": len(signals_out),
        "signals_never_emitted": sum("発行元が検出されない" in s["note"] for s in signals_out),
        "signals_never_listened": sum("受信側が検出されない" in s["note"] for s in signals_out),
        "unresolved_count": len(unresolved),
        "domains": {d: len(c) for d, c in nodes.items()},
        "domain_edges": len(domain_edges), "svg": svgs,
        "scene_connections": sum(len(s["connections"]) for s in scenes.values()),
        "unresolved_kinds": dict(Counter(u["kind"] for u in unresolved)),
        "untagged_classes": untagged_classes, "stale_tags": stale_tags,
        "out_of_vocab": out_of_vocab,
        "moved_tags": moved_tags,
    }
    dump("report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n出力先: {out}\n  まず見る: domains.mmd / domains.svg\n  LLMに渡す: llm_flow_input.md")


def entries_items(entries: dict):
    return entries.items()


if __name__ == "__main__":
    main()