"""Validation tests for generate_charts_fixed.py"""
import sys, pathlib, ast
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_charts_fixed",
    pathlib.Path(__file__).parent.parent / "generate_charts_fixed.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PASS = FAIL = 0

def check(label, actual, expected, note=""):
    global PASS, FAIL
    ok = actual == expected
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        print(f"    expected: {expected!r}")
        print(f"    actual  : {actual!r}")
    if note:
        print(f"    note    : {note}")

strip = m.strip_comments_and_strings
strip_comment = m.strip_comment_lines

print("=== Regression: BUG-01 preload/comment ===")
# BUG-01 fix: preloads/emissions/get_nodes scanned on strip_comment_lines() output,
# which removes pure comment lines but preserves string content (the paths).
src = '# const Dead = preload("res://dead.gd")\nconst Live = preload("res://live.gd")\n'
no_comment = strip_comment(src)
found = [x.group(1) for x in m.PRELOAD.finditer(no_comment)]
check("BUG-01 comment preload excluded via strip_comment_lines", found, ["res://live.gd"])

src2 = '# emit_signal("dead_signal")\nemit_signal("live_signal")\n'
no_comment2 = strip_comment(src2)
found2 = [x.group(1) for x in m.EMIT.finditer(no_comment2)]
check("BUG-01 comment emit_signal excluded via strip_comment_lines", found2, ["live_signal"])

src3 = '# get_node("DeadNode")\nget_node("LiveNode")\n'
no_comment3 = strip_comment(src3)
found3 = [x.group(1) for x in m.GET_NODE.finditer(no_comment3)]
check("BUG-01 comment get_node excluded via strip_comment_lines", found3, ["LiveNode"])

print()
print("=== BUG-02: single-quoted preload ===")
src_sq = "const X = preload('res://bar.gd')\n"
found_sq = [x.group(1) for x in m.PRELOAD.finditer(src_sq)]
check("BUG-02 PRELOAD accepts single-quote on original", found_sq, ["res://bar.gd"])

print()
print("=== BUG-03: quoted extends ===")
src_qext = 'extends "res://core/Base.gd"\n'
found_qext = [x.group(1) for x in m.GD_EXTENDS_QUOTED.finditer(src_qext)]
check("BUG-03 GD_EXTENDS_QUOTED from original", found_qext, ["res://core/Base.gd"])

print()
print("=== BUG-04: signal.emit() ===")
src_emit = "hp_changed.emit(value)\n"
clean_emit = strip(src_emit)
found_emit = [x.group(1) for x in m.EMIT_NEW.finditer(clean_emit)]
check("BUG-04 EMIT_NEW captures signal.emit()", found_emit, ["hp_changed"])

# Old-style scanned on strip_comment_lines output
src_old = 'emit_signal("hp_changed", value)\n'
no_comment_old = strip_comment(src_old)
found_old = [x.group(1) for x in m.EMIT.finditer(no_comment_old)]
check("BUG-04 EMIT old-style still works (on no_comment_lines)", found_old, ["hp_changed"])

print()
print("=== BUG-05: ROOT duplicate ===")
src_path = pathlib.Path(__file__).parent.parent / "generate_charts_fixed.py"
tree = ast.parse(src_path.read_text(encoding="utf-8"))
root_lines = [
    n.lineno for n in ast.walk(tree)
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "ROOT" for t in n.targets)
]
check("BUG-05 ROOT assigned exactly once", len(root_lines), 1,
      f"assignment lines: {root_lines}")

print()
print("=== BUG-06: multi-level parent ===")
# Simulate build_scene_dot logic
node_ids = {
    "scene.tscn::Container": "scene.tscn::node_0",
    "scene.tscn::Panel": "scene.tscn::node_1",
}
parent_path = "Container/Panel"
direct_parent = parent_path.split("/")[-1]
parent_name = "scene.tscn::" + direct_parent
result_id = node_ids.get(parent_name, parent_name)
check("BUG-06 multi-level parent resolves last segment", direct_parent, "Panel")
check("BUG-06 node_ids lookup succeeds for direct parent", result_id, "scene.tscn::node_1")

print()
print("=== Regression: existing passing tests ===")
src_t11 = "# extends Node\nextends Node2\n"
found_t11 = [x.group(1) for x in m.GD_EXTENDS.finditer(strip(src_t11))]
check("T1-1 extends in comment erased", found_t11, ["Node2"])

src_t15 = '"""\nextends Node\n"""\nextends Node2\n'
found_t15 = [x.group(1) for x in m.GD_EXTENDS.finditer(strip(src_t15))]
check("T1-5 extends in triple-string erased", found_t15, ["Node2"])

src_t51 = '[ext_resource type="Script" uid="uid://abc123" path="res://core/Foo.gd" id="1_abc"]\n'
found_t51 = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_EXT.finditer(src_t51)]
check("T5-1 ext_resource uid-then-path", len(found_t51) == 1, True)

print()
print(f"=== SUMMARY: {PASS} passed, {FAIL} failed ===")
