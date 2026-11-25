# python -m pytest tools/architecture/tests -q
"""generate_charts_v2.py のフィクスチャテスト。
小さな仮プロジェクトを tmp_path に作り、抽出結果が期待どおりか確認する。"""
import importlib.util
from pathlib import Path

ARCH = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("gc2", ARCH / "generate_charts_v2.py")
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def analyze(root: Path, hubs=("EventBus",)):
    """main() の解析部分と同じ手順（main を変えたらここも合わせる）。"""
    gc.UID_MAP.clear()
    gc.UID_MAP.update(gc.build_uid_map(root))
    include = ("core", "data", "scenes")
    scripts, scenes = {}, {}
    for p in gc.iter_files(root, include, ".gd"):
        rec = gc.scan_script(p, root)
        scripts[rec["path"]] = rec
    for p in gc.iter_files(root, include, ".tscn"):
        rec = gc.scan_scene(p, root)
        scenes[rec["path"]] = rec
    autoloads = gc.parse_autoloads(root)
    path_index = {"res://" + p: p for p in scripts}
    name_to_path = {}
    for p, rec in scripts.items():
        if rec["class_name"]:
            name_to_path[rec["class_name"]] = p
    for n, p in autoloads.items():
        if p in scripts:
            name_to_path[n] = p
    edges, entries, unresolved = gc.build_edges(
        scripts, scenes, autoloads, name_to_path, path_index, set(hubs))
    return {"scripts": scripts, "scenes": scenes, "autoloads": autoloads,
            "edges": edges.list(), "entries": entries, "unresolved": unresolved}


def find(edges, source, target, kind, detail=None):
    return [e for e in edges if e["source"] == source and e["target"] == target
            and e["kind"] == kind and (detail is None or e["detail"] == detail)]


# ---------- mask ----------

def test_mask_keeps_length_and_lines():
    src = 'var a = "x # y"  # comment "q\nvar b = 1\n'
    out = gc.mask(src, False)
    assert len(out) == len(src)
    assert out.count("\n") == src.count("\n")
    assert "comment" not in out and "x # y" not in out
    keep = gc.mask(src, True)
    assert "x # y" in keep and "comment" not in keep


def test_mask_triple_quote_keeps_newlines():
    src = 'var s = """a\nb # c\n"""\nvar z = 1\n'
    out = gc.mask(src, False)
    assert out.count("\n") == src.count("\n")
    assert "var z = 1" in out


# ---------- class_use / extends ----------

def test_class_use_ignores_comment_and_string(tmp_path):
    write(tmp_path, "core/foo.gd", "class_name Foo\nextends Node\n")
    write(tmp_path, "core/bar.gd", 'extends Node\n# uses Foo\nvar s = "Foo"\n')
    r = analyze(tmp_path)
    assert not [e for e in r["edges"] if e["source"] == "core/bar.gd"]


def test_extends_is_not_class_use(tmp_path):
    write(tmp_path, "core/foo.gd", "class_name Foo\nextends Node\n")
    write(tmp_path, "core/baz.gd", "extends Foo\n")
    r = analyze(tmp_path)
    assert find(r["edges"], "core/baz.gd", "core/foo.gd", "extends")
    assert not find(r["edges"], "core/baz.gd", "core/foo.gd", "class_use")


# ---------- signals ----------

EVENTBUS = "extends Node\nsignal enemy_died(x)\n"
PROJECT = '[autoload]\n\nEventBus="*res://core/autoload/EventBus.gd"\n'


def test_eventbus_emit_connect_matched(tmp_path):
    write(tmp_path, "project.godot", PROJECT)
    write(tmp_path, "core/autoload/EventBus.gd", EVENTBUS)
    write(tmp_path, "core/spawner.gd",
          "extends Node\nfunc go():\n\tEventBus.enemy_died.emit(1)\n")
    write(tmp_path, "core/listener.gd",
          "extends Node\nfunc _ready():\n\tEventBus.enemy_died.connect(_on)\n")
    r = analyze(tmp_path)
    es = find(r["edges"], "core/spawner.gd", "core/listener.gd", "signal", "enemy_died")
    assert len(es) == 1 and es[0]["line"] == 3
    assert find(r["edges"], "core/listener.gd", "core/autoload/EventBus.gd",
                "signal_listen", "enemy_died")
    ent = r["entries"][("core/autoload/EventBus.gd", "enemy_died")]
    assert ent["emitters"] == {"core/spawner.gd"}
    assert set(ent["listeners"]) == {"core/listener.gd"}


def test_inherited_signal_resolves_to_declaring_class(tmp_path):
    write(tmp_path, "core/a.gd", "class_name Base\nextends Node\nsignal hit\n")
    write(tmp_path, "core/b.gd", "extends Base\nfunc f():\n\thit.emit()\n")
    write(tmp_path, "core/c.gd",
          "extends Node\nfunc _ready():\n\tvar b = null\n\tb.hit.connect(_x)\n")
    r = analyze(tmp_path)
    assert find(r["edges"], "core/b.gd", "core/c.gd", "signal", "hit")


def test_ambiguous_signal_goes_to_unresolved(tmp_path):
    write(tmp_path, "core/a.gd", "extends Node\nsignal died\n")
    write(tmp_path, "core/b.gd", "extends Node\nsignal died\n")
    write(tmp_path, "core/c.gd", "extends Node\nfunc f(x):\n\tx.died.emit()\n")
    r = analyze(tmp_path)
    assert any(u["kind"] == "ambiguous_signal_emit" and u["target"] == "died"
               for u in r["unresolved"])
    assert not [e for e in r["edges"] if e["kind"] == "signal"]


def test_builtin_signal_ignored(tmp_path):
    write(tmp_path, "core/a.gd",
          "extends Node\nfunc _ready():\n\t$Button.pressed.connect(_on)\n")
    r = analyze(tmp_path)
    assert not [e for e in r["edges"] if e["kind"].startswith("signal")]
    assert r["unresolved"] == []


# ---------- scenes ----------

def test_scene_root_script_ignores_sub_resource(tmp_path):
    write(tmp_path, "scenes/x.tscn",
          '[gd_scene load_steps=3 format=3]\n\n'
          '[ext_resource type="Script" path="res://scenes/root.gd" id="1_a"]\n'
          '[ext_resource type="Script" path="res://scenes/other.gd" id="2_b"]\n\n'
          '[sub_resource type="Resource" id="Resource_1"]\n'
          'script = ExtResource("2_b")\n\n'
          '[node name="Root" type="Node3D"]\n'
          'script = ExtResource("1_a")\n')
    write(tmp_path, "scenes/root.gd", "extends Node3D\n")
    write(tmp_path, "scenes/other.gd", "extends Resource\n")
    r = analyze(tmp_path)
    sc = r["scenes"]["scenes/x.tscn"]
    assert sc["root_script"] == "scenes/root.gd"
    assert sc["scripts"] == ["scenes/root.gd"]


def test_scene_ref_edge(tmp_path):
    write(tmp_path, "scenes/a.tscn",
          '[gd_scene load_steps=2 format=3]\n\n'
          '[ext_resource type="PackedScene" path="res://scenes/b.tscn" id="1_b"]\n\n'
          '[node name="A" type="Node"]\n')
    write(tmp_path, "scenes/b.tscn", '[gd_scene format=3]\n\n[node name="B" type="Node"]\n')
    r = analyze(tmp_path)
    assert find(r["edges"], "scenes/a.tscn", "scenes/b.tscn", "scene_ref")


def test_scene_connection_becomes_listener(tmp_path):
    write(tmp_path, "scenes/c.tscn",
          '[gd_scene load_steps=3 format=3]\n\n'
          '[ext_resource type="Script" path="res://scenes/panel.gd" id="1_p"]\n'
          '[ext_resource type="Script" path="res://scenes/button.gd" id="2_b"]\n\n'
          '[node name="Panel" type="Control"]\n'
          'script = ExtResource("1_p")\n\n'
          '[node name="Btn" type="Control" parent="."]\n'
          'script = ExtResource("2_b")\n\n'
          '[connection signal="clicked" from="Btn" to="." method="_on_clicked"]\n')
    write(tmp_path, "scenes/panel.gd", "extends Control\n")
    write(tmp_path, "scenes/button.gd", "extends Control\nsignal clicked\n")
    r = analyze(tmp_path)
    es = find(r["edges"], "scenes/panel.gd", "scenes/button.gd", "signal_listen", "clicked")
    assert len(es) == 1 and es[0]["line"] == 12


# ---------- uid ----------

def test_uid_autoload_and_preload(tmp_path):
    write(tmp_path, "project.godot",
          '[autoload]\n\nEventBus="*uid://eb123"\nGhost="*uid://nope"\n')
    write(tmp_path, "core/autoload/EventBus.gd", EVENTBUS)
    write(tmp_path, "core/autoload/EventBus.gd.uid", "uid://eb123\n")
    write(tmp_path, "scenes/b.tscn",
          '[gd_scene format=3 uid="uid://scn1"]\n\n[node name="B" type="Node"]\n')
    write(tmp_path, "core/a.gd", 'extends Node\nconst S = preload("uid://scn1")\n')
    r = analyze(tmp_path)
    assert r["autoloads"] == {"EventBus": "core/autoload/EventBus.gd"}
    assert find(r["edges"], "core/a.gd", "scenes/b.tscn", "preload_scene")

# ---------- C3 / C4 ----------

def test_group_edges_and_unresolved(tmp_path):
    write(tmp_path, "core/player.gd",
          'extends Node\nfunc _ready():\n\tadd_to_group("player")\n')
    write(tmp_path, "core/user.gd",
          'extends Node\nfunc f():\n\tvar p = get_tree().get_first_node_in_group("player")\n'
          '\tif p.is_in_group("player"):\n\t\tpass\n'
          '\tget_tree().call_group("Player", "x")\n')
    r = analyze(tmp_path)
    assert find(r["edges"], "core/user.gd", "core/player.gd", "group_call", "player")
    assert find(r["edges"], "core/user.gd", "core/player.gd", "group_check", "player")
    u = [x for x in r["unresolved"] if x["kind"] == "group_no_member"]
    assert len(u) == 1 and u[0]["target"] == "Player" and u[0]["similar"] == ["player"]


def test_scene_groups_become_members(tmp_path):
    write(tmp_path, "scenes/t.gd", "extends Node3D\n")
    write(tmp_path, "scenes/t.tscn",
          '[gd_scene load_steps=2 format=3]\n\n'
          '[ext_resource type="Script" path="res://scenes/t.gd" id="1_a"]\n\n'
          '[node name="T" type="Node3D" groups=["targetable"]]\n'
          'script = ExtResource("1_a")\n')
    write(tmp_path, "core/user.gd",
          'extends Node\nfunc f():\n\tget_tree().get_nodes_in_group("targetable")\n')
    r = analyze(tmp_path)
    assert find(r["edges"], "core/user.gd", "scenes/t.gd", "group_call", "targetable")


def test_dynamic_calls_go_to_unresolved(tmp_path):
    write(tmp_path, "core/a.gd",
          'extends Node\nfunc f(n):\n\tvar a = get_node(n)\n\tvar b = get_node("Lit")\n'
          '\tvar c = load(n)\n\tvar d = load("res://x.tres")\n')
    r = analyze(tmp_path)
    kinds = sorted(u["kind"] for u in r["unresolved"] if u["kind"].startswith("dynamic_"))
    assert kinds == ["dynamic_get_node", "dynamic_load"]


def test_export_scene_not_in_tscn(tmp_path):
    write(tmp_path, "scenes/sp.gd",
          "extends Node\n@export var used_scene: PackedScene\n"
          "@export var lost_scene: PackedScene\n")
    write(tmp_path, "scenes/b.tscn", '[gd_scene format=3]\n\n[node name="B" type="Node"]\n')
    write(tmp_path, "scenes/w.tscn",
          '[gd_scene load_steps=3 format=3]\n\n'
          '[ext_resource type="Script" path="res://scenes/sp.gd" id="1_s"]\n'
          '[ext_resource type="PackedScene" path="res://scenes/b.tscn" id="2_b"]\n\n'
          '[node name="W" type="Node"]\nscript = ExtResource("1_s")\n'
          'used_scene = ExtResource("2_b")\n')
    r = analyze(tmp_path)
    miss = [u["target"] for u in r["unresolved"] if u["kind"] == "export_scene_not_in_tscn"]
    assert miss == ["lost_scene"]


def test_old_style_connect_not_misread(tmp_path):
    write(tmp_path, "core/a.gd", "extends Node\nsignal timer\n")
    write(tmp_path, "core/b.gd",
          'extends Node\nfunc f(timer):\n\ttimer.connect("timeout", _x)\n')
    r = analyze(tmp_path)
    assert not [e for e in r["edges"] if e["kind"] == "signal_listen"]


def test_focus_does_not_expand_through_hub(tmp_path):
    write(tmp_path, "project.godot", PROJECT)
    write(tmp_path, "core/autoload/EventBus.gd", EVENTBUS)
    write(tmp_path, "core/a.gd",
          "class_name A\nextends Node\nfunc f():\n\tEventBus.enemy_died.emit(1)\n")
    write(tmp_path, "core/b.gd",
          "class_name B\nextends Node\nfunc f():\n\tEventBus.enemy_died.emit(2)\n")
    r = analyze(tmp_path)
    n2p = {rec["class_name"]: p for p, rec in r["scripts"].items() if rec["class_name"]}
    n2p["EventBus"] = "core/autoload/EventBus.gd"
    name = gc.write_focus(r["edges"], r["scripts"], r["scenes"], n2p, {}, "A", 2,
                          tmp_path, {"core/autoload/EventBus.gd"})
    dot = (tmp_path / f"{name}.dot").read_text(encoding="utf-8")
    assert '"core/autoload/EventBus.gd"' in dot
    assert '"core/b.gd"' not in dot

def test_bare_emit_of_foreign_signal_is_unresolved(tmp_path):
    write(tmp_path, "core/a.gd", "extends Node\nsignal spell_discovered\n")
    write(tmp_path, "core/b.gd",
          'extends Node\nfunc f():\n\temit_signal("spell_discovered")\n')
    r = analyze(tmp_path)
    assert any(u["kind"] == "foreign_bare_signal_emit" and u["source"] == "core/b.gd"
               for u in r["unresolved"])
    assert not [e for e in r["edges"] if e["kind"] == "signal"]


def test_subresource_packedscene_counts_as_assigned(tmp_path):
    write(tmp_path, "scenes/sp.gd", "extends Node\n@export var card_scene: PackedScene\n")
    write(tmp_path, "scenes/w.tscn",
          '[gd_scene load_steps=3 format=3]\n\n'
          '[ext_resource type="Script" path="res://scenes/sp.gd" id="1_s"]\n\n'
          '[sub_resource type="PackedScene" id="PackedScene_1"]\n\n'
          '[node name="W" type="Node"]\nscript = ExtResource("1_s")\n'
          'card_scene = SubResource("PackedScene_1")\n')
    r = analyze(tmp_path)
    assert not [u for u in r["unresolved"] if u["kind"].startswith("export_scene")]

def test_edges_txt_has_file_line(tmp_path):
    write(tmp_path, "project.godot", PROJECT)
    write(tmp_path, "core/autoload/EventBus.gd", EVENTBUS)
    write(tmp_path, "core/spawner.gd",
          "extends Node\nfunc go():\n\tEventBus.enemy_died.emit(1)\n")
    write(tmp_path, "core/listener.gd",
          "extends Node\nfunc _ready():\n\tEventBus.enemy_died.connect(_on)\n")
    r = analyze(tmp_path)
    gc.write_edges_txt(r["edges"], r["unresolved"], tmp_path / "e.txt")
    txt = (tmp_path / "e.txt").read_text(encoding="utf-8")
    assert "[signal] core/spawner.gd -> core/listener.gd (enemy_died) @core/listener.gd:3" in txt

def test_pack_contains_signatures_edges_and_body(tmp_path):
    import json
    pk_spec = importlib.util.spec_from_file_location("pk", ARCH / "pack.py")
    pk = importlib.util.module_from_spec(pk_spec)
    pk_spec.loader.exec_module(pk)
    write(tmp_path, "core/a.gd",
          "class_name A\nextends Node\nsignal done\nfunc pub(x) -> int:\n\treturn 1\nfunc _priv():\n\tpass\n")
    write(tmp_path, "core/b.gd", "class_name B\nextends Node\nfunc f():\n\tA.new()\n")
    out = tmp_path / "out"
    out.mkdir()
    cls = {"core/a.gd": {"class_name": "A", "domain": "core", "extends": ["Node"]},
           "core/b.gd": {"class_name": "B", "domain": "core", "extends": ["Node"]}}
    deps = [{"source": "core/b.gd", "target": "core/a.gd", "kind": "class_use",
             "line": 4, "detail": "", "count": 1}]
    (out / "classes.json").write_text(json.dumps(cls), encoding="utf-8")
    (out / "dependencies.json").write_text(json.dumps(deps), encoding="utf-8")
    text, dropped, tp, _ = pk.build_pack(tmp_path, out, "テスト", "A", 24000, 12, None, ())
    assert tp == "core/a.gd" and dropped == []
    assert "[class_use] B -> A @core/b.gd:4" in text
    assert "func pub(x) -> int" in text and "_priv" not in text.split("## 対象の本文")[0]
    assert "func _priv():" in text  # 対象の本文には全文が入る
    small, dropped2, _, _ = pk.build_pack(tmp_path, out, "テスト", "A", 300, 12, None, ())
    assert dropped2 == ["B"] and "サイズ上限のため省略: B" in small

def _load_ac():
    spec = importlib.util.spec_from_file_location("ac", ARCH / "apply_change.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


GD_SAMPLE = ("extends Node\n\nfunc a():\n\tpass\n\nfunc target(x):\n\tvar y = x\n"
             "\tif y:\n\t\tprint(y)\n\nfunc c():\n\tpass\n")


def test_replace_function_only_target():
    ac = _load_ac()
    out = ac.replace_function(GD_SAMPLE, "target", "func target(x):\n\treturn x * 2")
    assert "return x * 2" in out and "print(y)" not in out
    assert "func a():\n\tpass\n\nfunc target" in out
    assert "return x * 2\n\nfunc c():" in out


def test_replace_function_not_found_or_ambiguous():
    import pytest
    ac = _load_ac()
    with pytest.raises(ValueError):
        ac.replace_function(GD_SAMPLE, "nope", "func nope():\n\tpass")
    with pytest.raises(ValueError):
        ac.replace_function(GD_SAMPLE + "\nfunc c():\n\tpass\n", "c", "func c():\n\tpass")


def test_parse_blocks_and_fences():
    ac = _load_ac()
    text = ("説明\n=== REPLACE core/a.gd :: f ===\n```gdscript\nfunc f():\n\tpass\n```\n=== END ===\n"
            "=== FILE tests/t.gd ===\nextends Node\n=== END ===\n"
            "```diff\n--- a/x.gd\n+++ b/x.gd\n@@ -1 +1 @@\n-a\n+b\n```\n")
    p = ac.parse(text)
    assert p["replaces"] == [("core/a.gd", "f", "func f():\n\tpass")]
    assert p["files"] == [("tests/t.gd", "extends Node")]
    assert len(p["diffs"]) == 1 and p["diffs"][0].startswith("--- a/x.gd")


def test_apply_replace_and_file_without_git(tmp_path):
    ac = _load_ac()
    write(tmp_path, "core/a.gd", GD_SAMPLE)
    text = ("=== REPLACE core/a.gd :: target ===\nfunc target(x):\n\treturn 1\n=== END ===\n"
            "=== FILE tests/test_a.gd ===\nextends Node\n=== END ===\n")
    ac.run(tmp_path, text, dry_run=True)
    assert "return 1" not in (tmp_path / "core/a.gd").read_text(encoding="utf-8")
    ac.run(tmp_path, text)
    assert "return 1" in (tmp_path / "core/a.gd").read_text(encoding="utf-8")
    assert (tmp_path / "tests/test_a.gd").exists()
    assert list((tmp_path / "tools/architecture/backup").glob("*/core/a.gd"))

def test_check_flow_verifies_against_facts():
    spec = importlib.util.spec_from_file_location("cf", ARCH / "check_flow.py")
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
    classes = {"a.gd": {"class_name": "A"}, "b.gd": {"class_name": "B"}}
    signals = [{"signal": "died"}]
    deps = [{"source": "a.gd", "target": "b.gd", "kind": "signal", "detail": "died", "line": 1}]
    data = {"nodes": [{"id": "n1", "label": "x", "evidence": ["A", "died"]},
                      {"id": "n2", "label": "y", "evidence": ["B"]},
                      {"id": "n3", "label": "z", "evidence": ["Ghost"]}],
            "edges": [{"from": "n1", "to": "n2", "kind": "signal", "evidence": "died"},
                      {"from": "n2", "to": "n3", "kind": "direct", "evidence": ""},
                      {"from": "n1", "to": "n3", "kind": "guess", "evidence": ""}]}
    mmd, rep = cf.check_flow(data, classes, signals, deps)
    assert rep["edges_verified"] == 1 and rep["edges_guess"] == 1
    assert len(rep["edges_unverified"]) == 1
    assert rep["nodes_unverified"] == ["n3"] and rep["bad_evidence"] == {"n3": ["Ghost"]}
    assert ":::unverified" in mmd

def test_flow_trace_signal_chain(tmp_path):
    spec = importlib.util.spec_from_file_location("ft", ARCH / "flow_trace.py")
    ft = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ft)
    write(tmp_path, "core/a.gd",
          "class_name A\nextends Node\nsignal done\nfunc run():\n\t_step()\n\tdone.emit()\n"
          "func _step():\n\tB.work()\n")
    write(tmp_path, "core/b.gd", "class_name B\nextends Node\nstatic func work():\n\tpass\n")
    write(tmp_path, "core/c.gd",
          "class_name C\nextends Node\nfunc _ready():\n\tvar a = null\n\ta.done.connect(_on_done)\n"
          "func _on_done():\n\tB.work()\n")
    g = ft.build(tmp_path, tmp_path / "out")
    kinds = {(s, d, k) for s, d, k, _, _ in g["edges"]}
    assert ("A.run", "A._step", "call") in kinds
    assert ("A._step", "B.work", "call") in kinds
    assert ("A.run", "sig:A.done", "emit") in kinds
    assert ("sig:A.done", "C._on_done", "handle") in kinds
    assert ("C._on_done", "B.work", "call") in kinds
    dist, trunc = ft.bfs(ft.adjacency(g["edges"]), ["A.run"], 6, 100)
    assert "C._on_done" in dist and not trunc