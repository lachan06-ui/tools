from pathlib import Path
import re
import json


# ============================================================
# Configuration
# ============================================================

# 元となる巨大Markdown
INPUT_FILE = Path("../tr_1_inventory.md")

# 分割先
OUTPUT_DIRECTORY = Path(".")

# マップファイル名
MAP_FILE_NAME = "inventory_map.json"


# ============================================================
# Patterns
# ============================================================

LAYER_PATTERN = re.compile(
    r"^# Layer (\d+): (.+?)\s*$"
)

SYSTEM_PATTERN = re.compile(
    r"^## (.+?)\s*$"
)


# ============================================================
# Filename
# ============================================================

def sanitize_name(name: str) -> str:
    """
    ファイル名・フォルダ名として安全な文字列に変換する。
    """

    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip()

    if not name:
        return "Unnamed"

    return name


def make_layer_folder_name(
    layer_number: int,
    layer_title: str
) -> str:
    """
    Layer 0: Primitives & Data Atoms (...)
    ↓
    0_Primitives_DataAtoms
    """

    # 括弧以降の説明を除去
    layer_title = re.sub(
        r"\s*\(.*?\)\s*$",
        "",
        layer_title
    )

    # & を除去
    layer_title = layer_title.replace("&", "_")

    # 空白 → _
    layer_title = re.sub(
        r"\s+",
        "",
        layer_title
    )

    # 英数字 / _ / - 以外を削除
    layer_title = re.sub(
        r"[^a-zA-Z0-9_\-]",
        "",
        layer_title
    )

    # __ → _
    layer_title = re.sub(
        r"_+",
        "_",
        layer_title
    )

    layer_title = layer_title.strip("_")

    return f"{layer_number}_{layer_title}"


# ============================================================
# Parser
# ============================================================

def parse_markdown(lines):
    """
    元Markdownを解析する。

    行番号も保持する。
    """

    layers = []

    current_layer = None
    current_system = None

    for index, line in enumerate(lines):

        # Markdown上の行番号
        # 人間向けなので1始まり
        line_number = index + 1

        # ----------------------------------------------------
        # Layer
        # ----------------------------------------------------

        layer_match = LAYER_PATTERN.match(line)

        if layer_match:

            layer_number = int(
                layer_match.group(1)
            )

            layer_title = (
                layer_match.group(2).strip()
            )

            current_layer = {
                "number": layer_number,
                "title": layer_title,
                "start_line": line_number,
                "end_line": None,
                "systems": []
            }

            layers.append(current_layer)

            current_system = None

            continue

        # ----------------------------------------------------
        # System
        # ----------------------------------------------------

        system_match = SYSTEM_PATTERN.match(line)

        if system_match:

            if current_layer is None:
                print(
                    f"Warning: Layerより前にSystemがあります "
                    f"(line {line_number})"
                )

                continue

            # 前のSystemを終了
            if current_system is not None:
                current_system["end_line"] = (
                    line_number - 1
                )

            system_name = (
                system_match.group(1).strip()
            )

            current_system = {
                "name": system_name,
                "start_line": line_number,
                "end_line": None,
                "content": []
            }

            current_layer["systems"].append(
                current_system
            )

            continue

        # ----------------------------------------------------
        # System content
        # ----------------------------------------------------

        if current_system is not None:
            current_system["content"].append(line)

    # --------------------------------------------------------
    # 最後のSystem / Layerを閉じる
    # --------------------------------------------------------

    total_lines = len(lines)

    if current_system is not None:
        current_system["end_line"] = total_lines

    if current_layer is not None:
        current_layer["end_line"] = total_lines

    # Layer同士の境界を正確にする
    for i in range(len(layers) - 1):

        current = layers[i]
        next_layer = layers[i + 1]

        current["end_line"] = (
            next_layer["start_line"] - 1
        )

    return layers


# ============================================================
# Content
# ============================================================

def clean_content(lines):
    """
    System本文を整理する。
    """

    result = []

    for line in lines:

        # Markdown上の区切り
        if line.strip() == "---":
            continue

        result.append(line)

    # 前後の空行を削除

    while result and not result[0].strip():
        result.pop(0)

    while result and not result[-1].strip():
        result.pop()

    return result


# ============================================================
# Output
# ============================================================

def write_files(
    layers,
    output_directory
):
    """
    Layer / Systemをファイルへ出力しながら
    マップ情報も生成する。
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    map_data = {
        "source_file": str(INPUT_FILE),
        "layers": [],
        "files": {}
    }

    for layer in layers:

        # ----------------------------------------------------
        # Layer folder
        # ----------------------------------------------------

        folder_name = make_layer_folder_name(
            layer["number"],
            layer["title"]
        )

        layer_directory = (
            output_directory / folder_name
        )

        layer_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        layer_map = {
            "number": layer["number"],
            "title": layer["title"],
            "folder": folder_name,
            "source_start_line": layer["start_line"],
            "source_end_line": layer["end_line"],
            "systems": []
        }

        # ----------------------------------------------------
        # Systems
        # ----------------------------------------------------

        for system in layer["systems"]:

            system_name = sanitize_name(
                system["name"]
            )

            file_name = (
                f"{system_name}.md"
            )

            file_path = (
                layer_directory / file_name
            )

            content = clean_content(
                system["content"]
            )

            text = "\n".join(content)

            if text:
                text += "\n"

            file_path.write_text(
                text,
                encoding="utf-8"
            )

            # 相対パス
            relative_path = (
                file_path
                .relative_to(output_directory)
                .as_posix()
            )

            # ------------------------------------------------
            # System map
            # ------------------------------------------------

            system_map = {
                "name": system["name"],
                "file": relative_path,
                "source_start_line": system["start_line"],
                "source_end_line": system["end_line"]
            }

            layer_map["systems"].append(
                system_map
            )

            # ファイルをキーにした逆引き
            map_data["files"][relative_path] = {
                "layer": layer["number"],
                "layer_title": layer["title"],
                "system": system["name"],
                "source_file": str(INPUT_FILE),
                "source_start_line": system["start_line"],
                "source_end_line": system["end_line"]
            }

        map_data["layers"].append(
            layer_map
        )

    # --------------------------------------------------------
    # Map JSON
    # --------------------------------------------------------

    map_path = (
        output_directory / MAP_FILE_NAME
    )

    map_path.write_text(
        json.dumps(
            map_data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return map_path


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("Markdown Layer Splitter")
    print("=" * 60)

    print(f"Source : {INPUT_FILE}")
    print(f"Output : {OUTPUT_DIRECTORY}")

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"入力ファイルが存在しません: {INPUT_FILE}"
        )

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    text = INPUT_FILE.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    print(
        f"Lines  : {len(lines)}"
    )

    # --------------------------------------------------------
    # Parse
    # --------------------------------------------------------

    layers = parse_markdown(lines)

    if not layers:

        raise ValueError(
            "Layerが見つかりませんでした。"
        )

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    map_path = write_files(
        layers,
        OUTPUT_DIRECTORY
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    system_count = sum(
        len(layer["systems"])
        for layer in layers
    )

    print()
    print("=" * 60)
    print("Completed")
    print("=" * 60)

    print(
        f"Layers  : {len(layers)}"
    )

    print(
        f"Systems : {system_count}"
    )

    print(
        f"Map     : {map_path}"
    )


if __name__ == "__main__":
    main()