"""
Diagnostic tests for generate_charts.py code review.
Run: python tools/architecture/tests/test_review.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_charts",
    pathlib.Path(__file__).parent.parent / "generate_charts.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PASS = 0
FAIL = 0

def check(label, actual, expected, note=""):
    global PASS, FAIL
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    mark = "OK" if ok else "NG"
    print(f"  [{status}] {mark} {label}")
    if not ok:
        print(f"         expected : {expected!r}")
        print(f"         actual   : {actual!r}")
    if note:
        print(f"         note     : {note}")

strip = m.strip_comments_and_strings

print("=" * 60)
print("TEST GROUP 1: strip_comments_and_strings")
print("=" * 60)

# T1-1: extends in comment must be erased
src = "# extends Node\nextends Node2\n"
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T1-1 extends in comment is erased", found, ["Node2"])

# T1-2: extends in double-quoted string must be erased
src = 'var s = "extends Node"\nextends Node2\n'
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T1-2 extends in string is erased", found, ["Node2"])

# T1-3: preload in comment — scanned on original (BUG)
src = '# var x = preload("res://foo.gd")\nvar y = preload("res://bar.gd")\n'
found_orig = [x.group(1) for x in m.PRELOAD.finditer(src)]
check("T1-3 preload in comment on original (BUG: should be bar only)",
      found_orig, ["res://bar.gd"],
      "preloads are scanned on `original` not `clean` → comment preloads leak through")

# T1-4: preload in single-quoted string is erased in clean
src = "var x = preload('res://foo.gd')\nvar y = preload(\"res://bar.gd\")\n"
clean = strip(src)
found_clean = [x.group(1) for x in m.PRELOAD.finditer(clean)]
check("T1-4 preload in single-quoted string erased in clean",
      found_clean, ["res://bar.gd"])

# T1-5: triple-quoted string - newlines preserved
src = '"""\nextends Node\n"""\nextends Node2\n'
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T1-5 extends inside triple-quoted string erased", found, ["Node2"])

# T1-6: backslash escape in string
src = 'var x = "he said \\"hello\\""\nextends Node\n'
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T1-6 backslash escape in string handled", found, ["Node"])

# T1-7: single-quoted string
src = "var x = 'extends Node'\nextends Node2\n"
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T1-7 extends in single-quoted string erased", found, ["Node2"])

print()
print("=" * 60)
print("TEST GROUP 2: extends extraction")
print("=" * 60)

# T2-1: extends by class_name (built-in or user class)
src = "extends CharacterBody3D\n"
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T2-1 extends BuiltinType", found, ["CharacterBody3D"])

# T2-2: extends by res:// path (quoted) — STRIPPED by clean, so GD_EXTENDS finds nothing (BUG)
src = 'extends "res://core/Base.gd"\n'
clean = strip(src)
found_clean = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
found_orig  = [x.group(1) for x in m.GD_EXTENDS.finditer(src)]
check("T2-2a extends res:// path: extracted from clean (should be 0 due to stripping)",
      found_clean, [],
      "BUG: quoted extends stripped by clean → completely missed")
check("T2-2b extends res:// path on original (would find if scanned there)",
      found_orig, ['"res://core/Base.gd"'])

# T2-3: build_dependencies extends res:// check - the target begins with literal quote char
# The code checks: target.startswith('"res://')  — but after clean, nothing is extracted
# So that branch is unreachable for quoted extends.
check("T2-3 build_dependencies 'extends res://' branch: startswith check uses literal '\"'",
      '"res://x".startswith(\'"res://\')', "True",
      "The startswith check itself is correct IF the value contains the leading quote. "
      "But since clean strips strings, quoted extends are NEVER extracted → branch is dead code.")

# T2-4: multi-line extends (GDScript 4 does not allow, but check regex)
src = "extends \\\n  Node\n"  # Not valid GDScript, but robustness check
clean = strip(src)
found = [x.group(1) for x in m.GD_EXTENDS.finditer(clean)]
check("T2-4 multi-line extends (not valid GDScript)", found, [],
      "Not an actual GDScript feature; no special handling needed")

print()
print("=" * 60)
print("TEST GROUP 3: preload/load")
print("=" * 60)

# T3-1: preload .gd
src = 'const Foo = preload("res://core/Foo.gd")\n'
found = [x.group(1) for x in m.PRELOAD.finditer(src)]
check("T3-1 preload .gd", found, ["res://core/Foo.gd"])

# T3-2: load() with non-.gd path — collected but NOT added as edge (only .gd tracked)
src = 'var tex = load("res://assets/sprite.png")\n'
found = [x.group(1) for x in m.PRELOAD.finditer(src)]
check("T3-2 load non-.gd collected", found, ["res://assets/sprite.png"],
      "Collected but filtered in build_dependencies (only .gd → edge). OK by design.")

# T3-3: preload in comment on original (BUG confirmed)
src = '# const Dead = preload("res://dead.gd")\nconst Live = preload("res://live.gd")\n'
found = [x.group(1) for x in m.PRELOAD.finditer(src)]
check("T3-3 preload in comment leaked (BUG)",
      found, ["res://live.gd"],
      "BUG: preloads scanned on `original`. Comment preloads are included.")

# T3-4: emit_signal in comment leaked  
src = '# emit_signal("dead_signal")\nemit_signal("live_signal")\n'
found = [x.group(1) for x in m.EMIT.finditer(src)]
check("T3-4 emit_signal in comment leaked (BUG)",
      found, ["live_signal"],
      "BUG: emissions scanned on `original`. Comment emissions are included.")

# T3-5: get_node in comment leaked
src = '# get_node("DeadNode")\nget_node("LiveNode")\n'
found = [x.group(1) for x in m.GET_NODE.finditer(src)]
check("T3-5 get_node in comment leaked (BUG)",
      found, ["LiveNode"],
      "BUG: get_nodes scanned on `original`. Comment get_nodes are included.")

print()
print("=" * 60)
print("TEST GROUP 4: signal connect/emit")
print("=" * 60)

# T4-1: signal declaration
src = "signal hp_changed(new_hp: int)\n"
clean = strip(src)
found = [x.group(1) for x in m.SIGNAL.finditer(clean)]
check("T4-1 signal declaration", found, ["hp_changed"])

# T4-2: emit_signal old style
src = 'emit_signal("hp_changed", value)\n'
found = [x.group(1) for x in m.EMIT.finditer(src)]
check("T4-2 emit_signal old style", found, ["hp_changed"])

# T4-3: new-style signal.emit() — NOT captured (BUG for GDScript 4)
src = "hp_changed.emit(value)\n"
found = [x.group(1) for x in m.EMIT.finditer(src)]
check("T4-3 new-style signal.emit() (BUG: not captured)",
      found, [],
      "BUG: GDScript 4 prefers signal_name.emit() but only emit_signal() is extracted")

# T4-4: .connect() - CONNECT regex
src = "EventBus.player_died.connect(_on_player_died)\n"
clean = strip(src)
found = [(x.group(1), x.group(2)) for x in m.CONNECT.finditer(clean)]
check("T4-4 .connect() extracted", len(found) > 0, True,
      f"found: {found}")

# T4-5: new-style connect: signal_name.connect(callable)
src = "hp_changed.connect(_on_hp_changed)\n"
clean = strip(src)
found = [(x.group(1), x.group(2)) for x in m.CONNECT.finditer(clean)]
check("T4-5 signal.connect() captured", len(found) > 0, True,
      f"found: {found}")

print()
print("=" * 60)
print("TEST GROUP 5: .tscn parsing")
print("=" * 60)

# T5-1: ext_resource with uid before path
tscn = '[ext_resource type="Script" uid="uid://abc123" path="res://core/Foo.gd" id="1_abc"]\n'
found = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_EXT.finditer(tscn)]
check("T5-1 ext_resource uid-then-path", len(found) == 1, True, f"found: {found}")
if found:
    check("T5-1b path correct", found[0][1], "res://core/Foo.gd")
    check("T5-1c id correct", found[0][2], "1_abc")

# T5-2: ext_resource without uid (older format)
tscn2 = '[ext_resource type="Script" path="res://core/Foo.gd" id="1"]\n'
found2 = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_EXT.finditer(tscn2)]
check("T5-2 ext_resource without uid", len(found2) == 1, True, f"found: {found2}")

# T5-3: SCENE_NODE without parent (root node)
tscn3 = '[node name="Root" type="Node3D"]\n'
found3 = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_NODE.finditer(tscn3)]
check("T5-3 root node no parent", found3, [("Root", "Node3D", None)])

# T5-4: SCENE_NODE with parent
tscn4 = '[node name="Child" type="Node3D" parent="."]\n'
found4 = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_NODE.finditer(tscn4)]
check("T5-4 child node with parent='.'", found4, [("Child", "Node3D", ".")])

# T5-5: nested child (parent path)
tscn5 = '[node name="Leaf" type="Label" parent="Container/Panel"]\n'
found5 = [(x.group(1), x.group(2), x.group(3)) for x in m.SCENE_NODE.finditer(tscn5)]
check("T5-5 deeply nested node parent path", found5, [("Leaf", "Label", "Container/Panel")],
      "BUG: build_scene_dot resolves only single-level parents (scene_path + '::' + node['parent']); "
      "multi-level paths like 'Container/Panel' won't match any node_ids key → fallback to unresolved string in DOT")

# T5-6: script extraction from scene
tscn6 = 'script = ExtResource("1_abc")\n'
import re
m_script = re.search(r'script\s*=\s*ExtResource\("([^"]+)"\)', tscn6)
check("T5-6 script resource extraction", m_script.group(1) if m_script else None, "1_abc")

print()
print("=" * 60)
print("TEST GROUP 6: DOT output correctness")
print("=" * 60)

# T6-1: dot_escape
check("T6-1 dot_escape backslash", m.dot_escape("a\\b"), "a\\\\b")
check("T6-2 dot_escape quote",     m.dot_escape('a"b'), 'a\\"b')
check("T6-3 dot_escape newline",   m.dot_escape("a\nb"), "a\\nb")

# T6-4: graph_node_id passes dot_escape (path chars safe in DOT quotes)
nid = m.graph_node_id("core/Foo.gd")
check("T6-4 graph_node_id simple path", nid, "core/Foo.gd")

# T6-5: graph_header returns valid start
header = m.graph_header("Test")
check("T6-5 graph_header starts with digraph", header[0].startswith('digraph "'), True)
check("T6-6 graph_header last is not '}'", header[-1].startswith('  edge'), True)

# T6-7: node label format in build_scene_dot — dot_escape called on 'Name\nType'
# The label uses \\n (literal backslash-n) for DOT newline, but dot_escape converts \n → \\n
test_label = m.dot_escape("MyNode\\nNode3D")
check("T6-7 dot_escape on label with \\n", "\\n" in test_label, True)

print()
print("=" * 60)
print("TEST GROUP 7: build_indexes / path resolution")
print("=" * 60)

# T7-1: same stem name collision
scripts_data = {
    "core/Foo.gd": {"class_name": [], "source": "", "clean": "", "extends": [],
                     "signals": [], "functions": [], "preloads": [], "node_paths": [],
                     "get_nodes": [], "connections": [], "emissions": []},
    "scenes/Foo.gd": {"class_name": [], "source": "", "clean": "", "extends": [],
                       "signals": [], "functions": [], "preloads": [], "node_paths": [],
                       "get_nodes": [], "connections": [], "emissions": []},
}
ci, pi = m.build_indexes(scripts_data)
check("T7-1 stem collision: last-write wins (BUG)",
      ci.get("Foo") in ["core/Foo.gd", "scenes/Foo.gd"], True,
      "BUG: class_index.setdefault(stem, path) — setdefault keeps FIRST, but explicit class_name "
      "assignment uses direct assignment (overwrite). Stem-based lookup is non-deterministic for duplicates.")

# T7-2: explicit class_name overwrites stem
scripts_data2 = {
    "core/Bar.gd": {"class_name": [{"value": "BarClass", "line": 1}],
                    "source": "", "clean": "", "extends": [],
                    "signals": [], "functions": [], "preloads": [], "node_paths": [],
                    "get_nodes": [], "connections": [], "emissions": []},
}
ci2, pi2 = m.build_indexes(scripts_data2)
check("T7-2 explicit class_name indexed", ci2.get("BarClass"), "core/Bar.gd")
check("T7-2b stem also indexed", ci2.get("Bar"), "core/Bar.gd")

print()
print("=" * 60)
print("TEST GROUP 8: misc / ROOT duplicate")
print("=" * 60)

# T8-1: ROOT defined twice
import ast
src_path = pathlib.Path(__file__).parent.parent / "generate_charts.py"
tree = ast.parse(src_path.read_text(encoding="utf-8"))
root_assignments = [
    node.lineno for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "ROOT" for t in node.targets)
]
check("T8-1 ROOT assigned twice (lines 36,38)", root_assignments, [36, 38, 37],
      "BUG: ROOT = Path('.') appears on lines 36 AND 38. Line 38 is dead duplicate.")
# Adjust for 0-indexed or actual
if root_assignments != [36, 38]:
    print(f"         actual ROOT assignment lines: {root_assignments}")

# T8-2: signal_connection_candidate target is NOT a file path
# build_dependency_dot adds non-path targets as ellipse nodes — correct for signal connections
# But the target for connections is group(1) = "EventBus.player_died" style string, not a signal name
# CONNECT regex: group(1) = object, group(2) = signal_name  BUT find_matches returns group(1) only
import re
src_connect = "EventBus.player_died.connect(_on_player_died)\n"
clean_connect = strip(src_connect)
found_connect = [x.group(1) for x in m.CONNECT.finditer(clean_connect)]
check("T8-2 CONNECT find_matches uses group(1) = object side (not signal name)",
      found_connect, ["EventBus.player_died"],
      "find_matches always returns group(1). For CONNECT, group(1)=receiver, group(2)=signal. "
      "The edge target becomes the receiver object string, not the signal name. "
      "Misleading for 'signal_connection_candidate' kind.")

print()
print("=" * 60)
print(f"SUMMARY: {PASS} passed, {FAIL} failed")
print("=" * 60)
