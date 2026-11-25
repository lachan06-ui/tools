# python tools/architecture/generate_charts.py --root . --output tools/architecture/output
#!/usr/bin/env python3
"""
Godot 4.7 Architecture Chart Generator

Outputs:
  classes.json
  dependencies.json
  unresolved.json
  inheritance.dot
  dependencies.dot
  scenes.dot
  report.json

Dependency sources:
  - GDScript extends
  - class_name
  - preload/load paths
  - signal declarations and connections
  - direct function calls (conservative extraction)
  - scene ext_resource references
  - scene node hierarchy
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
OUTPUT = Path("tools/architecture/output")
ROOT = Path(".")

INCLUDE: tuple[str, ...] = ("core", "data", "scenes", "tests")

GRAPH_FONT = "Noto Sans CJK JP"
GRAPH_RANKDIR = "TB"
GRAPH_NODE_SEP = "0.35"
GRAPH_RANK_SEP = "0.65"
GRAPH_DPI = "120"

GD_EXTENDS = re.compile(r'^\s*extends\s+([^\s#]+)', re.M)
CLASS_NAME = re.compile(r'^\s*class_name\s+(\w+)', re.M)
SIGNAL = re.compile(r'^\s*signal\s+(\w+)', re.M)
FUNC = re.compile(r'^\s*(?:static\s+)?func\s+(\w+)\s*\(', re.M)

PRELOAD = re.compile(
    r'(?:preload|load)\s*\(\s*"([^"]+)"\s*\)'
)

NODE_PATH = re.compile(r'\$([A-Za-z0-9_./]+)')
GET_NODE = re.compile(
    r'get_node(?:_or_null)?\s*\(\s*"([^"]+)"\s*\)'
)

CONNECT = re.compile(
    r'([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)'
    r'\.connect\s*\(\s*'
    r'([A-Za-z_]\w*)'
)

EMIT = re.compile(
    r'emit_signal\s*\(\s*"([^"]+)"'
)

SCENE_EXT = re.compile(
    r'\[ext_resource\s+type="([^"]+)"'
    r'[^]]*path="([^"]+)"'
    r'[^]]*id="([^"]+)"'
)

SCENE_NODE = re.compile(
    r'\[node\s+name="([^"]+)"'
    r'\s+type="([^"]+)"'
    r'(?:\s+parent="([^"]+)")?'
)

SCENE_SCRIPT = re.compile(
    r'script\s*=\s*ExtResource\("([^"]+)"\)'
)

CALL = re.compile(
    r'\b([A-Za-z_]\w*)\s*\('
)

BUILTINS = {
    "if", "for", "while", "match", "return",
    "preload", "load", "print", "push_warning",
    "push_error", "assert", "super", "await",
    "range", "min", "max", "clamp", "str",
    "int", "float", "bool", "len", "typeof",
    "is_instance_valid", "is_same", "get_node",
    "get_node_or_null", "has_node", "has_method",
    "emit_signal", "connect", "disconnect",
}


def strip_comments_and_strings(source: str) -> str:
    """Remove comments and strings while preserving newlines."""
    result = []
    i = 0
    in_string = False
    quote = ""
    triple = False

    while i < len(source):
        ch = source[i]

        if not in_string and ch == "#":
            while i < len(source) and source[i] != "\n":
                result.append(" ")
                i += 1
            continue

        if not in_string and ch in ('"', "'"):
            quote = ch
            triple = source[i:i + 3] == ch * 3
            in_string = True
            count = 3 if triple else 1
            result.extend(" " * count)
            i += count
            continue

        if in_string:
            if ch == "\\":
                result.append(" ")
                if i + 1 < len(source):
                    result.append(" ")
                    i += 2
                    continue

            if triple and source[i:i + 3] == quote * 3:
                result.extend("   ")
                i += 3
                in_string = False
                continue

            if not triple and ch == quote:
                result.append(" ")
                in_string = False
                i += 1
                continue

            result.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def line_of(source: str, position: int) -> int:
    return source.count("\n", 0, position) + 1


def get_included_roots(root: Path) -> list[Path]:
    """Return existing analysis directories specified by INCLUDE."""
    return [
        root / name
        for name in INCLUDE
        if (root / name).is_dir()
    ]


def graph_node_name(path: str) -> str:
    """Return a compact repository-relative graph label."""
    parts: tuple[str, ...] = Path(path).parts
    if len(parts) <= 1:
        return path
    return "/".join(parts[-2:])


def dot_escape(value: str) -> str:
    """Escape strings for Graphviz DOT."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def graph_node_id(path: str) -> str:
    """Return a stable DOT node identifier."""
    return dot_escape(path)


def graph_node_label(path: str) -> str:
    """Return a readable graph label."""
    return dot_escape(graph_node_name(path))


def graph_header(title: str) -> list[str]:
    """Create common Graphviz layout settings."""
    return [
        f'digraph "{dot_escape(title)}" {{',
        f'  rankdir="{GRAPH_RANKDIR}";',
        f'  ranksep="{GRAPH_RANK_SEP}";',
        f'  nodesep="{GRAPH_NODE_SEP}";',
        '  splines=true;',
        '  overlap=false;',
        '  concentrate=true;',
        '  bgcolor="transparent";',
        f'  graph [fontname="{GRAPH_FONT}", dpi={GRAPH_DPI}, pad="0.3"];',
        f'  node [shape=box, style="rounded,filled", fillcolor="#EAF1F8", color="#64748B", fontname="{GRAPH_FONT}", fontsize=10, margin="0.14,0.09"];',
        f'  edge [color="#64748B", fontname="{GRAPH_FONT}", fontsize=8, arrowsize=0.7];'
    ]

def find_matches(pattern, source):
    return [
        {
            "value": match.group(1),
            "line": line_of(source, match.start())
        }
        for match in pattern.finditer(source)
    ]



def collect_scripts(root: Path) -> dict:
    scripts: dict = {}

    for included_root in get_included_roots(root):
        for path in sorted(included_root.rglob("*.gd")):
            if ".godot" in path.parts:
                continue

            original: str = path.read_text(encoding="utf-8")
            clean: str = strip_comments_and_strings(original)

            rel: str = path.relative_to(root).as_posix()

            scripts[rel] = {
                "source": original,
                "clean": clean,
                "extends": find_matches(GD_EXTENDS, clean),
                "class_name": find_matches(CLASS_NAME, clean),
                "signals": find_matches(SIGNAL, clean),
                "functions": find_matches(FUNC, clean),
                "preloads": find_matches(PRELOAD, original),
                "node_paths": find_matches(NODE_PATH, clean),
                "get_nodes": find_matches(GET_NODE, original),
                "connections": find_matches(CONNECT, clean),
                "emissions": find_matches(EMIT, original),
            }

    return scripts


def collect_scenes(root: Path) -> dict:
    scenes: dict = {}

    for included_root in get_included_roots(root):
        for path in sorted(included_root.rglob("*.tscn")):
            if ".godot" in path.parts:
                continue

            source: str = path.read_text(encoding="utf-8")

            resources: list[dict] = []
            for match in SCENE_EXT.finditer(source):
                resources.append({
                    "type": match.group(1),
                    "path": match.group(2),
                    "id": match.group(3),
                    "line": line_of(source, match.start())
                })

            nodes: list[dict] = []
            for match in SCENE_NODE.finditer(source):
                nodes.append({
                    "name": match.group(1),
                    "type": match.group(2),
                    "parent": match.group(3) or ".",
                    "line": line_of(source, match.start())
                })

            script_match = re.search(
                r'script\s*=\s*ExtResource\("([^"]+)"\)',
                source
            )

            rel: str = path.relative_to(root).as_posix()

            scenes[rel] = {
                "resources": resources,
                "nodes": nodes,
                "script_resource_id": (
                    script_match.group(1) if script_match else None
                )
            }

    return scenes


def build_indexes(scripts):
    class_index = {}
    path_index = {}

    for path, data in scripts.items():
        path_index["res://" + path] = path

        for item in data["class_name"]:
            class_index[item["value"]] = path

        class_index.setdefault(Path(path).stem, path)

    return class_index, path_index


def build_dependencies(scripts, class_index, path_index):
    edges = []
    unresolved = []

    def add_edge(source, target, kind, line):
        edges.append({
            "source": source,
            "target": target,
            "kind": kind,
            "line": line
        })

    for path, data in scripts.items():

        for item in data["extends"]:
            target = item["value"]

            if target in class_index:
                add_edge(path, class_index[target], "extends", item["line"])
            elif target.startswith('"res://'):
                unresolved.append({
                    "source": path,
                    "target": target,
                    "kind": "extends",
                    "line": item["line"]
                })

        for item in data["preloads"]:
            target = item["value"]

            if target.startswith("res://") and target.endswith(".gd"):
                if target in path_index:
                    add_edge(
                        path, path_index[target],
                        "preload", item["line"]
                    )
                else:
                    unresolved.append({
                        "source": path,
                        "target": target,
                        "kind": "preload",
                        "line": item["line"]
                    })

        for item in data["get_nodes"]:
            unresolved.append({
                "source": path,
                "target": item["value"],
                "kind": "dynamic_node_reference",
                "line": item["line"]
            })

        for item in data["node_paths"]:
            unresolved.append({
                "source": path,
                "target": item["value"],
                "kind": "scene_node_reference",
                "line": item["line"]
            })

        for item in data["connections"]:
            add_edge(
                path,
                item["value"],
                "signal_connection_candidate",
                item["line"]
            )

    return edges, unresolved


def build_inheritance_dot(scripts: dict, class_index: dict) -> str:
    lines = graph_header("Inheritance")

    for path in scripts:
        node_id = graph_node_id(path)
        label = graph_node_label(path)
        lines.append(f'  "{node_id}" [label="{label}"];')

    for path, data in scripts.items():
        for item in data["extends"]:
            target = item["value"]
            if target in class_index:
                target_path = class_index[target]
                lines.append(
                    f'  "{graph_node_id(target_path)}" -> '
                    f'"{graph_node_id(path)}" '
                    f'[label="extends:{item["line"]}"];'
                )

    lines.append("}")
    return "\n".join(lines)


def build_dependency_dot(edges: list[dict]) -> str:
    lines = graph_header("Dependencies")
    nodes: set[str] = set()

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        if target in BUILTINS:
            continue

        nodes.add(source)
        if target.endswith(".gd") or target.endswith(".tscn"):
            nodes.add(target)

    for node in sorted(nodes):
        lines.append(
            f'  "{graph_node_id(node)}" '
            f'[label="{graph_node_label(node)}"];'
        )

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        if target in BUILTINS:
            continue

        target_is_path = target.endswith((".gd", ".tscn"))
        target_id = graph_node_id(target) if target_is_path else graph_node_id(target)

        if not target_is_path:
            lines.append(
                f'  "{target_id}" '
                f'[label="{dot_escape(target)}", shape=ellipse, fillcolor="#FFF4D6"];'
            )

        lines.append(
            f'  "{graph_node_id(source)}" -> "{target_id}" '
            f'[label="{dot_escape(edge["kind"])}:{edge["line"]}"];'
        )

    lines.append("}")
    return "\n".join(lines)


def build_scene_dot(scenes: dict) -> str:
    lines = graph_header("Scenes")

    for scene_path, data in scenes.items():
        scene_id = graph_node_id(scene_path)
        scene_label = graph_node_label(scene_path)

        lines.append(
            f'  "{scene_id}" '
            f'[label="{scene_label}", fillcolor="#DCEFE2"];'
        )

        node_ids: dict[str, str] = {}

        for index, node in enumerate(data["nodes"]):
            full_name = scene_path + "::" + node["name"]
            node_ids[full_name] = f"{scene_path}::node_{index}"

            node_id = graph_node_id(node_ids[full_name])
            label = dot_escape(
                f'{node["name"]}\\n{node["type"]}'
            )

            lines.append(
                f'  "{node_id}" [label="{label}", fillcolor="#EAF1F8"];'
            )

        for index, node in enumerate(data["nodes"]):
            full_name = scene_path + "::" + node["name"]
            child_id = graph_node_id(node_ids[full_name])

            if node["parent"] == ".":
                parent_id = scene_id
            else:
                parent_name = scene_path + "::" + node["parent"]
                parent_id = graph_node_id(
                    node_ids.get(parent_name, parent_name)
                )

            lines.append(
                f'  "{parent_id}" -> "{child_id}";'
            )

    lines.append("}")
    return "\n".join(lines)

def generate_svg(output: Path, graph_names: list[str]) -> list[str]:
    """Generate SVG files from DOT files using Graphviz."""
    generated: list[str] = []

    dot_executable = shutil.which("dot")
    if dot_executable is None:
        print("[WARNING] Graphviz 'dot' not found. SVG generation skipped.")
        return generated

    for name in graph_names:
        dot_path = output / f"{name}.dot"
        svg_path = output / f"{name}.svg"

        result = subprocess.run(
            [dot_executable, "-Tsvg", str(dot_path), "-o", str(svg_path)],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print(f"[ERROR] SVG generation failed: {name}")
            print(result.stderr)
            continue

        generated.append(svg_path.name)
        print(f"[OK] Generated {svg_path.name}")

    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    included_roots: list[Path] = get_included_roots(root)
    print("[INFO] Included directories:")
    for included_root in included_roots:
        print(f"  - {included_root.relative_to(root)}")

    scripts = collect_scripts(root)
    scenes = collect_scenes(root)

    class_index, path_index = build_indexes(scripts)

    edges, unresolved = build_dependencies(
        scripts, class_index, path_index
    )

    def write_json(name, value):
        (output / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    write_json("classes.json", scripts)
    write_json("scenes.json", scenes)
    write_json("dependencies.json", edges)
    write_json("unresolved.json", unresolved)

    (output / "inheritance.dot").write_text(
        build_inheritance_dot(scripts, class_index),
        encoding="utf-8"
    )

    (output / "dependencies.dot").write_text(
        build_dependency_dot(edges),
        encoding="utf-8"
    )

    (output / "scenes.dot").write_text(
        build_scene_dot(scenes),
        encoding="utf-8"
    )

    svg_files = generate_svg(
        output,
        ["inheritance", "dependencies", "scenes"]
    )
    
    report = {
        "script_count": len(scripts),
        "scene_count": len(scenes),
        "dependency_count": len(edges),
        "unresolved_count": len(unresolved),
        "generated_files": [
            "classes.json",
            "scenes.json",
            "dependencies.json",
            "unresolved.json",
            "inheritance.dot",
            "dependencies.dot",
            "scenes.dot",
            *svg_files
        ]
    }

    write_json("report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
