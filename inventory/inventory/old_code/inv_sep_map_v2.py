from pathlib import Path
import re
import json


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("../tr_1_inventory.md")
OUTPUT_DIRECTORY = Path(".")
MAP_FILE_NAME = "inventory_map.json"


# ============================================================
# Patterns
# ============================================================

LAYER_PATTERN = re.compile(
    r"^# Layer (\d+):\s*(.+?)\s*$"
)

SYSTEM_PATTERN = re.compile(
    r"^##\s+(.+?)\s*$"
)

FIELD_PATTERN = re.compile(
    r"^###\s+(.+?)\s*:?\s*$"
)


# ============================================================
# Field Mapping
# ============================================================

# 元の長いフィールド名 → AI向け短縮名
FIELD_MAP = {
    "Purpose": "p",
    "Related Files": "f",
    "Responsibilities": "r",
    "Public API Methods": "api",
    "Public API Methods:": "api",
    "Signals": "sig",
    "Properties": "prop",
    "Owned Data": "data",
    "Depends On": "dep",
    "Used By": "use",
    "Save Data": "save",
    "Notes": "note",
}


# AIに不要な定型値
EMPTY_VALUES = {
    "",
    "none",
    "not found",
    "n/a",
    "na",
    "null",
}


# ============================================================
# Filename
# ============================================================

def sanitize_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip()
    return name or "Unnamed"


def make_layer_folder_name(
    layer_number: int,
    layer_title: str
) -> str:

    layer_title = re.sub(
        r"\s*\(.*?\)\s*$",
        "",
        layer_title
    )

    layer_title = layer_title.replace("&", "_")
    layer_title = re.sub(r"\s+", "", layer_title)
    layer_title = re.sub(
        r"[^a-zA-Z0-9_\-]",
        "",
        layer_title
    )
    layer_title = re.sub(
        r"_+",
        "_",
        layer_title
    )

    return (
        f"{layer_number}_"
        f"{layer_title.strip('_')}"
    )


# ============================================================
# Value Cleaning
# ============================================================

def clean_value(value: str) -> str:
    """
    AI向けに値を最小化する。
    """

    value = value.strip()

    # Markdown記号を除去
    if value.startswith("- "):
        value = value[2:].strip()

    # 不要なMarkdown
    value = value.replace("**", "")
    value = value.replace("__", "")

    return value.strip()


def is_empty(value: str) -> bool:
    return value.strip().lower() in EMPTY_VALUES


def compact_values(values):
    """
    値を正規化し、空値・重複を除去。
    """

    result = []
    seen = set()

    for value in values:

        value = clean_value(value)

        if is_empty(value):
            continue

        if value not in seen:
            result.append(value)
            seen.add(value)

    return result


# ============================================================
# Parser
# ============================================================

def parse_markdown(lines):
    """
    Inventoryを1回だけ走査し、
    Layer / System / Fieldを抽出する。
    """

    layers = []

    current_layer = None
    current_system = None
    current_field = None

    for line in lines:

        # ----------------------------------------------------
        # Layer
        # ----------------------------------------------------

        match = LAYER_PATTERN.match(line)

        if match:

            current_layer = {
                "id": int(match.group(1)),
                "title": match.group(2).strip(),
                "systems": []
            }

            layers.append(current_layer)

            current_system = None
            current_field = None

            continue

        # ----------------------------------------------------
        # System
        # ----------------------------------------------------

        match = SYSTEM_PATTERN.match(line)

        if match:

            if current_layer is None:
                continue

            current_system = {
                "name": match.group(1).strip(),
                "fields": {}
            }

            current_layer["systems"].append(
                current_system
            )

            current_field = None

            continue

        # ----------------------------------------------------
        # Field
        # ----------------------------------------------------

        match = FIELD_PATTERN.match(line)

        if match:

            if current_system is None:
                continue

            original_name = match.group(1).strip()

            field_name = FIELD_MAP.get(
                original_name
            )

            current_field = field_name

            if field_name:
                current_system["fields"][
                    field_name
                ] = []

            continue

        # ----------------------------------------------------
        # Value
        # ----------------------------------------------------

        if (
            current_system is not None
            and current_field is not None
        ):

            value = clean_value(line)

            if not is_empty(value):
                current_system["fields"][
                    current_field
                ].append(value)

    return layers


# ============================================================
# Compact System
# ============================================================

def compact_system(system):
    """
    System情報をAI向けのkey=value形式へ変換。
    """

    fields = system["fields"]

    output = [
        system["name"]
    ]

    # 順序を固定
    field_order = [
        "f",
        "p",
        "r",
        "api",
        "sig",
        "prop",
        "data",
        "dep",
        "use",
        "save",
        "note",
    ]

    for key in field_order:

        values = fields.get(key)

        if not values:
            continue

        values = compact_values(values)

        if not values:
            continue

        # 単一値
        if len(values) == 1:
            output.append(
                f"{key}={values[0]}"
            )

        # 複数値
        else:
            output.append(
                f"{key}=" + ",".join(values)
            )

    return "\n".join(output)


# ============================================================
# Dependency
# ============================================================

def get_dependencies(system):
    values = system["fields"].get("dep", [])
    return compact_values(values)


# ============================================================
# Output
# ============================================================

def write_files(
    layers,
    output_directory
):

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # Compact AI Map
    # ========================================================

    map_data = {
        "src": INPUT_FILE.name,
        "layers": [],
        "deps": {}
    }

    # --------------------------------------------------------
    # Layers
    # --------------------------------------------------------

    for layer in layers:

        folder_name = make_layer_folder_name(
            layer["id"],
            layer["title"]
        )

        layer_directory = (
            output_directory / folder_name
        )

        layer_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        layer_map = [
            layer["id"],
            re.sub(
                r"\s*\(.*?\)\s*$",
                "",
                layer["title"]
            ).strip(),
            folder_name,
            []
        ]

        # ----------------------------------------------------
        # Systems
        # ----------------------------------------------------

        for system in layer["systems"]:

            system_name = system["name"]

            file_name = (
                f"{sanitize_name(system_name)}.txt"
            )

            file_path = (
                layer_directory / file_name
            )

            # ------------------------------------------------
            # Write compact system
            # ------------------------------------------------

            text = compact_system(system)

            file_path.write_text(
                text + "\n",
                encoding="utf-8"
            )

            relative_path = (
                file_path
                .relative_to(output_directory)
                .as_posix()
            )

            # [name, file]
            layer_map[3].append([
                system_name,
                relative_path
            ])

            # ------------------------------------------------
            # Dependency graph
            # ------------------------------------------------

            dependencies = get_dependencies(
                system
            )

            if dependencies:
                map_data["deps"][
                    system_name
                ] = dependencies

        map_data["layers"].append(
            layer_map
        )

    # ========================================================
    # Write Map
    # ========================================================

    map_path = (
        output_directory / MAP_FILE_NAME
    )

    map_path.write_text(
        json.dumps(
            map_data,
            ensure_ascii=False,
            separators=(",", ":")
        ),
        encoding="utf-8"
    )

    return map_path


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("AI-Optimized Inventory Generator")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"入力ファイルが存在しません: {INPUT_FILE}"
        )

    text = INPUT_FILE.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    print(f"Lines  : {len(lines)}")

    # --------------------------------------------------------
    # Parse once
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

    system_count = sum(
        len(layer["systems"])
        for layer in layers
    )

    print()
    print("=" * 60)
    print("Completed")
    print("=" * 60)

    print(f"Layers  : {len(layers)}")
    print(f"Systems : {system_count}")
    print(f"Map     : {map_path}")


if __name__ == "__main__":
    main()
