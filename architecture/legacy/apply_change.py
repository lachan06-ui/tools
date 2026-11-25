#!/usr/bin/env python3
"""apply_change.py -- クラウドAIの出力を適用し、テストとチャート再生成まで1コマンドで行う。

使い方（プロジェクトのルート = gitのトップで）:
  python tools/architecture/apply_change.py change.txt            # 適用
  python tools/architecture/apply_change.py change.txt --dry-run  # 何も書かずに検証だけ
  python tools/architecture/apply_change.py change.txt --test-cmd "..." --charts-cmd "..."

change.txt = クラウドAIの返答をそのまま保存したもの（説明文が混ざっていてよい）。適用するのは次の3種類:
  1) === REPLACE path :: func名 ===  ...新しい関数全体...  === END ===
  2) === FILE path ===  ...ファイル全体...  === END ===
  3) ```diff ... ```（unified diff。git apply で適用）

設定: tools/architecture/apply_config.json に {"test_cmd": "...", "charts_cmd": "..."} を置くと毎回指定しなくてよい。
安全策: 検証が全部通るまで何も書かない / 適用前に tools/architecture/backup/<日時>/ へ退避 /
        .git .godot addons とルート外への書き込みは拒否。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BLOCK = re.compile(r"^=== (REPLACE|FILE) (.+?) ===[ \t]*\n(.*?)^=== END ===[ \t]*$", re.M | re.S)
DIFF = re.compile(r"```(?:diff|patch)[^\n]*\n(.*?)\n```", re.S)
PLUS = re.compile(r"^\+\+\+ (?:b/)?([^\t\n]+)", re.M)
FAIL_RE = re.compile(r"(?i)(fail|error|assert)")
FORBIDDEN_TOP = {".git", ".godot", "addons"}


# ---------- 解析 ----------

def strip_fence(body: str) -> str:
    lines = body.strip("\n").split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
    return "\n".join(lines)


def parse(text: str) -> dict:
    text = text.replace("\r\n", "\n")
    res = {"diffs": [], "replaces": [], "files": []}
    for m in BLOCK.finditer(text):
        kind, head, body = m.group(1), m.group(2).strip(), strip_fence(m.group(3))
        if kind == "REPLACE":
            if " :: " not in head:
                raise ValueError(f"REPLACE の見出しは 'path :: func名' の形: {head}")
            path, name = [s.strip() for s in head.split(" :: ", 1)]
            res["replaces"].append((path, name, body))
        else:
            res["files"].append((head, body))
    rest = BLOCK.sub("", text)
    for m in DIFF.finditer(rest):
        res["diffs"].append(m.group(1).rstrip("\n") + "\n")
    return res


def safe_path(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if root not in p.parents:
        raise ValueError(f"ルートの外は書き込めません: {rel}")
    if p.relative_to(root).parts[0] in FORBIDDEN_TOP:
        raise ValueError(f"対象外のフォルダです: {rel}")
    return p


# ---------- 関数の置換 ----------

def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def replace_function(src: str, name: str, new: str) -> str:
    eol = "\r\n" if "\r\n" in src else "\n"
    lines = src.replace("\r\n", "\n").split("\n")
    head = rf"^[ \t]*(?:static[ \t]+)?func[ \t]+{re.escape(name)}[ \t]*\("
    hits = [i for i, l in enumerate(lines) if re.match(head, l)]
    if not hits:
        raise ValueError(f"func {name} が見つかりません")
    if len(hits) > 1:
        raise ValueError(f"func {name} が {len(hits)} か所あり曖昧です（適用しません）")
    start = hits[0]
    base = indent_of(lines[start])
    end = start
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "":
            continue
        if indent_of(lines[i]) <= base:
            break
        end = i
    new_lines = new.strip("\n").split("\n")
    first = next((l for l in new_lines if l.strip()), "")
    if not re.match(head, first):
        raise ValueError(f"新しい本文の先頭が 'func {name}(' ではありません: {first[:60]}")
    if indent_of(first) < base:
        prefix = lines[start][:base]
        new_lines = [prefix + l if l.strip() else l for l in new_lines]
    return eol.join(lines[:start] + new_lines + lines[end + 1:])


# ---------- git apply ----------

def in_git(root: Path) -> bool:
    if not shutil.which("git"):
        return False
    r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True)
    return r.returncode == 0


def git_apply(root: Path, diff: str, check: bool):
    last = ""
    for level in (1, 0):
        cmd = ["git", "apply", f"-p{level}", "--recount", "--ignore-whitespace", "--whitespace=nowarn"]
        if check:
            cmd.append("--check")
        r = subprocess.run(cmd, cwd=root, input=diff, text=True, encoding="utf-8", capture_output=True)
        if r.returncode == 0:
            return level, ""
        last = r.stderr.strip()
    return None, last


# ---------- 実行補助 ----------

def run_cmd(cmd: str, root: Path, timeout: int):
    try:
        r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"タイムアウト（{timeout}秒）"


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def diff_dict(a: dict, b: dict) -> dict:
    return {k: (a.get(k, 0), b.get(k, 0)) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0)}


def summarize(log: str, cap: int = 40):
    lines = [l.rstrip() for l in log.splitlines()]
    return [l for l in lines if FAIL_RE.search(l)][:cap], lines[-10:]


# ---------- 本体 ----------

def run(root: Path, text: str, test_cmd=None, charts_cmd=None, dry_run=False, timeout=900) -> str:
    root = root.resolve()
    plan = parse(text)
    if not (plan["diffs"] or plan["replaces"] or plan["files"]):
        raise SystemExit("[ERROR] 適用できるブロックがありません（=== REPLACE / === FILE / ```diff が見つからない）")

    # 1) 検証（ここまでは何も書かない）
    new_contents: dict[Path, str] = {}
    for rel, name, body in plan["replaces"]:
        p = safe_path(root, rel)
        cur = new_contents.get(p)
        if cur is None:
            if not p.exists():
                raise SystemExit(f"[ERROR] {rel} がありません")
            cur = p.read_bytes().decode("utf-8")
        try:
            new_contents[p] = replace_function(cur, name, body)
        except ValueError as e:
            raise SystemExit(f"[ERROR] {rel}: {e}")
    replaced = set(new_contents)
    for rel, body in plan["files"]:
        p = safe_path(root, rel)
        if p in replaced:
            raise SystemExit(f"[ERROR] {rel} は REPLACE と FILE の両方に指定されています")
        new_contents[p] = body + "\n"

    diff_files: set[str] = set()
    for i, d in enumerate(plan["diffs"], 1):
        if not in_git(root):
            raise SystemExit("[ERROR] diff の適用には git が必要です（gitリポジトリのトップで実行）")
        level, err = git_apply(root, d, check=True)
        if level is None:
            raise SystemExit(f"[ERROR] diff {i} が当たりません:\n" + "\n".join(err.splitlines()[:15]))
        diff_files.update(f for f in PLUS.findall(d) if f.strip() != "/dev/null")
    clash = [f for f in diff_files if (root / f).resolve() in new_contents]
    if clash:
        raise SystemExit(f"[ERROR] diff と REPLACE/FILE が同じファイルを触っています: {clash}")

    lines = ["## 適用結果",
             f"- REPLACE {len(plan['replaces'])}件 / FILE {len(plan['files'])}件 / diff {len(plan['diffs'])}件",
             "- 対象: " + ", ".join(sorted(p.relative_to(root).as_posix() for p in new_contents)
                                   + sorted(diff_files))]
    if dry_run:
        lines.append("- dry-run: 検証は通りました。何も書き込んでいません")
        return "\n".join(lines)

    # 2) 退避して適用
    bdir = root / "tools" / "architecture" / "backup" / time.strftime("%Y%m%d_%H%M%S")
    for p in list(new_contents) + [(root / f).resolve() for f in diff_files]:
        if p.exists():
            try:
                dst = bdir / p.relative_to(root)
            except ValueError:
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
    lines.append(f"- バックアップ: {bdir.relative_to(root).as_posix()}")
    for i, d in enumerate(plan["diffs"], 1):
        level, err = git_apply(root, d, check=False)
        if level is None:
            raise SystemExit(f"[ERROR] diff {i} の適用に失敗（バックアップから戻してください）:\n{err}")
    for p, content in new_contents.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content.encode("utf-8"))

    # 3) テスト
    vdir = root / "tools" / "architecture" / "verify"
    vdir.mkdir(parents=True, exist_ok=True)
    if test_cmd:
        code, log = run_cmd(test_cmd, root, timeout)
        (vdir / "last_test.log").write_text(log, encoding="utf-8")
        lines.append(f"- テスト: 終了コード {code}（全文: tools/architecture/verify/last_test.log）")
        if code != 0:
            hits, tail = summarize(log)
            lines += ["  失敗らしき行:"] + [f"    {h[:200]}" for h in hits] + ["  末尾:"] + [f"    {t[:200]}" for t in tail]
    else:
        lines.append("- テスト: 未設定（--test-cmd または apply_config.json）")

    # 4) チャート再生成と差分
    out = root / "tools" / "architecture" / "output"
    if charts_cmd:
        before_rep = load_json(out / "report.json", {})
        before_un = {(u["kind"], u["source"], str(u["target"])) for u in load_json(out / "unresolved.json", [])}
        code, log = run_cmd(charts_cmd, root, timeout)
        (vdir / "last_charts.log").write_text(log, encoding="utf-8")
        if code != 0:
            lines.append("- チャート再生成: 失敗")
            lines += [f"    {t[:200]}" for t in log.splitlines()[-10:]]
        else:
            after_rep = load_json(out / "report.json", {})
            lines.append("- チャート差分:")
            for k in ("script_count", "scene_count", "unresolved_count",
                      "signals_never_emitted", "signals_never_listened"):
                if before_rep.get(k) != after_rep.get(k):
                    lines.append(f"    {k}: {before_rep.get(k)} -> {after_rep.get(k)}")
            for k in ("edge_kinds", "unresolved_kinds"):
                for sub, (a, b) in diff_dict(before_rep.get(k, {}), after_rep.get(k, {})).items():
                    lines.append(f"    {k}.{sub}: {a} -> {b}")
            new_un = [u for u in load_json(out / "unresolved.json", [])
                      if (u["kind"], u["source"], str(u["target"])) not in before_un]
            lines.append(f"    新しい未解決: {len(new_un)}件")
            lines += [f"      [?{u['kind']}] {u['source']}:{u['line']} {u['target']}" for u in new_un[:15]]
    else:
        lines.append("- チャート再生成: 未設定（--charts-cmd または apply_config.json）")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("change", help="クラウドAIの返答を保存したテキスト（'-' で標準入力）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--test-cmd")
    ap.add_argument("--charts-cmd")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    cfg = load_json(Path(__file__).with_name("apply_config.json"), {})
    text = sys.stdin.read() if args.change == "-" else Path(args.change).read_text(
        encoding="utf-8", errors="replace")
    print(run(Path(args.root), text, args.test_cmd or cfg.get("test_cmd"),
              args.charts_cmd or cfg.get("charts_cmd"), args.dry_run, args.timeout))


if __name__ == "__main__":
    main()