from pathlib import Path
import re
import json


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path("./../../..")

INPUT_FILE = Path("../tr_1_inventory.md")

OUTPUT_DIRECTORY = Path(".")
MAP_FILE_NAME = "inventory_map.json"

GD_ROOTS = [
    Path(f"{PROJECT_ROOT}/core"),
    Path(f"{PROJECT_ROOT}/scenes"),
]

CLASSIFICATION_PENDING_TITLE = "Classification Pending"


# ============================================================
# Inventory Field Order
# ============================================================

FIELD_ORDER = [
    "Purpose",
    "Related Files",
    "Responsibilities",
    "Public API Methods",
    "Signals",
    "Properties",
    "Owned Data",
    "Depends On",
    "Used By",
    "Save Data",
    "Notes",
]


# ============================================================
# Field Ownership
# ============================================================

MANUAL_FIELDS = {
    "Purpose",
    "Responsibilities",
    "Notes",
}


# ============================================================
# Markdown Patterns
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
# GDScript Patterns
# ============================================================

CLASS_PATTERN = re.compile(
    r"^\s*class_name\s+(\w+)"
)

ROLE_PATTERN = re.compile(
    r"^\s*#\s*ROLE:\s*(.+)"
)

SYS_PATTERN = re.compile(
    r"^\s*#\s*SYS:\s*(.+)"
)

DESCRIPTION_PATTERN = re.compile(
    r"^\s*#\s*(?!ROLE:|SYS:)(.+)"
)

# Top-level const
CONST_PATTERN = re.compile(
    r"^const\s+(\w+)"
    r"(?:\s*:\s*([^=\n]+))?"
)

# Top-level var
VAR_PATTERN = re.compile(
    r"^var\s+(\w+)"
    r"(?:\s*:\s*([^=\n]+))?"
)

FUNC_PATTERN = re.compile(
    r"^\s*(?:static\s+)?func\s+(\w+)\s*"
    r"\((.*?)\)"
    r"(?:\s*->\s*([^\s:]+))?"
)

SIGNAL_PATTERN = re.compile(
    r"^\s*signal\s+(\w+)\s*(?:\((.*?)\))?"
)

PRELOAD_PATTERN = re.compile(
    r'preload\(["\']res://([^"\']+)["\']\)'
)

LOAD_PATTERN = re.compile(
    r'load\(["\']res://([^"\']+)["\']\)'
)

# Generic identifier usage.
# Depends On補助解析用。
IDENTIFIER_PATTERN = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\b"
)


# ============================================================
# Save-related Patterns
# ============================================================

SAVE_METHOD_NAMES = {
    "get_save_data",
    "load_save_data",
    "serialize",
    "deserialize",
    "save",
    "load",
    "save_data",
    "load_data",
}

SERIALIZER_NAME_PATTERN = re.compile(
    r"\b([A-Z]\w*Serializer)\b"
)

# ============================================================
# Type Formatting
# ============================================================

UNMARKED_TYPE = "unmarked"


def format_typed_name(
    name,
    type_name=None,
):
    type_name = (
        type_name.strip()
        if type_name
        else UNMARKED_TYPE
    )

    return f"{name}: {type_name}"

# ============================================================
# AI Field Map
# ============================================================

FIELD_MAP = {
    "Purpose": "p",
    "Related Files": "f",
    "Responsibilities": "r",
    "Public API Methods": "api",
    "Signals": "sig",
    "Properties": "prop",
    "Owned Data": "data",
    "Depends On": "dep",
    "Used By": "use",
    "Save Data": "save",
    "Notes": "note",
}


EMPTY_VALUES = {
    "",
    "none",
    "not found",
    "n/a",
    "na",
    "null",
}


# ============================================================
# Godot / Generic Types
# ============================================================

BUILTIN_TYPES = {
    "bool",
    "int",
    "float",
    "String",
    "StringName",
    "Array",
    "Dictionary",
    "Object",
    "Node",
    "Node2D",
    "Node3D",
    "Control",
    "CanvasItem",
    "Resource",
    "RefCounted",
    "PackedScene",
    "PackedStringArray",
    "PackedVector2Array",
    "PackedVector3Array",
    "Vector2",
    "Vector2i",
    "Vector3",
    "Vector3i",
    "Vector4",
    "Vector4i",
    "Color",
    "Transform2D",
    "Transform3D",
    "Basis",
    "Quaternion",
    "Rect2",
    "Rect2i",
    "AABB",
    "Plane",
    "RID",
    "Callable",
    "Signal",
    "Variant",
    "Nil",
}


# ============================================================
# Utilities
# ============================================================

def unique(values):
    result = []
    seen = set()

    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)

    return result


def clean_value(value):
    if value is None:
        return ""

    value = value.strip()

    if value.startswith("- "):
        value = value[2:].strip()

    value = value.replace("**", "")
    value = value.replace("__", "")

    return value.strip()


def is_empty(value):
    return clean_value(value).lower() in EMPTY_VALUES


def compact_values(values):
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


def sanitize_name(name):
    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name,
    )

    name = name.strip()

    return name or "Unnamed"


def clean_layer_title(title):
    return re.sub(
        r"\s*\(.*?\)\s*$",
        "",
        title,
    ).strip()


def make_layer_folder_name(
    layer_number,
    layer_title,
):
    title = clean_layer_title(layer_title)

    title = title.replace("&", "_")
    title = re.sub(r"\s+", "", title)
    title = re.sub(
        r"[^a-zA-Z0-9_\-]",
        "",
        title,
    )
    title = re.sub(r"_+", "_", title)

    return f"{layer_number}_{title.strip('_')}"


# ============================================================
# Inventory Parser
# ============================================================

def parse_existing_inventory(text):
    """
    既存Inventoryを解析する。

    Layer:
        維持

    Manual:
        Purpose
        Responsibilities
        Notes

    その他:
        後続処理でコード側から更新可能。
    """

    layers = []

    current_layer = None
    current_system = None
    current_field = None

    for line in text.splitlines():

        # ----------------------------------------------------
        # Layer
        # ----------------------------------------------------

        match = LAYER_PATTERN.match(line)

        if match:

            current_layer = {
                "id": int(match.group(1)),
                "title": match.group(2).strip(),
                "systems": [],
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
                "fields": {
                    field: []
                    for field in FIELD_ORDER
                },
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

            field_name = (
                match.group(1)
                .strip()
                .rstrip(":")
            )

            if field_name in FIELD_ORDER:
                current_field = field_name
            else:
                current_field = None

            continue

        # ----------------------------------------------------
        # Value
        # ----------------------------------------------------

        if (
            current_system is not None
            and current_field is not None
        ):

            value = clean_value(line)

            if value:
                current_system["fields"][
                    current_field
                ].append(value)

    return layers


# ============================================================
# Existing Inventory Index
# ============================================================

def index_existing_inventory(layers):

    result = {}

    for layer in layers:

        for system in layer["systems"]:

            result[system["name"]] = {
                "layer_id": layer["id"],
                "layer_title": layer["title"],
                "system": system,
            }

    return result


# ============================================================
# GDScript Scanner
# ============================================================

def scan_gd_file(path):

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    lines = text.splitlines()

    class_name = path.stem

    role = None
    system = None
    description = None

    properties = []
    owned_data = []
    methods = []
    signals = []
    dependencies = []
    used_identifiers = []

    save_methods = []
    serializers = []

    for line in lines:

        # ----------------------------------------------------
        # class_name
        # ----------------------------------------------------

        match = CLASS_PATTERN.match(line)

        if match:
            class_name = match.group(1)

        # ----------------------------------------------------
        # ROLE
        # ----------------------------------------------------

        match = ROLE_PATTERN.match(line)

        if match:
            role = match.group(1).strip()

        # ----------------------------------------------------
        # SYS
        # ----------------------------------------------------

        match = SYS_PATTERN.match(line)

        if match:
            system = match.group(1).strip()

        # ----------------------------------------------------
        # const
        # ----------------------------------------------------

        match = CONST_PATTERN.match(line)

        if match:

            name = match.group(1)
            type_name = match.group(2)

            owned_data.append(
                format_typed_name(
                    name,
                    type_name,
                )
            )

        # ----------------------------------------------------
        # Properties
        # ----------------------------------------------------

        property_match = re.match(
            r"^\s*@(?:export|onready)\s+var\s+"
            r"(\w+)"
            r"(?:\s*:\s*([^=\n]+))?",
            line,
        )

        if property_match:

            name = property_match.group(1)
            type_name = property_match.group(2)

            properties.append(
                format_typed_name(
                    name,
                    type_name,
                )
            )


        # ----------------------------------------------------
        # var
        # ----------------------------------------------------

        match = VAR_PATTERN.match(line)

        if match:

            name = match.group(1)
            type_name = match.group(2)

            owned_data.append(
                format_typed_name(
                    name,
                    type_name,
                )
            )

        # ----------------------------------------------------
        # func
        # ----------------------------------------------------

        match = FUNC_PATTERN.match(line)

        if match:

            name = match.group(1)

            if not name.startswith("_"):

                args = match.group(2).strip()
                return_type = match.group(3)

                signature = f"{name}({args})"

                if return_type:
                    signature += (
                        f" -> {return_type}"
                    )

                methods.append(signature)

            if name in SAVE_METHOD_NAMES:
                save_methods.append(name)

        # ----------------------------------------------------
        # signal
        # ----------------------------------------------------

        match = SIGNAL_PATTERN.match(line)

        if match:
            name = match.group(1)
            args = match.group(2)
            if args is None or not args.strip():
                signals.append(f"{name}()")
                continue
            formatted_args = []

            for arg in args.split(","):
                arg = arg.strip()
                if not arg:
                    continue
                if ":" in arg:
                    arg_name, arg_type = arg.split(":",1,)

                    formatted_args.append(
                        format_typed_name(arg_name.strip(), arg_type.strip(),)
                    )
                else:
                    formatted_args.append(
                        format_typed_name(arg, None,)
                    )

            signals.append(
                f"{name}("
                + ", ".join(formatted_args)
                + ")"
            )


        # ----------------------------------------------------
        # preload / load
        # ----------------------------------------------------

        for match in PRELOAD_PATTERN.finditer(line):
            dependencies.append(
                match.group(1)
            )

        for match in LOAD_PATTERN.finditer(line):
            dependencies.append(
                match.group(1)
            )

        # ----------------------------------------------------
        # Save serializer
        # ----------------------------------------------------

        for match in SERIALIZER_NAME_PATTERN.finditer(line):
            serializers.append(
                match.group(1)
            )

        # ----------------------------------------------------
        # Identifier usage
        # ----------------------------------------------------

        for match in IDENTIFIER_PATTERN.finditer(line):

            identifier = match.group(1)

            if identifier not in BUILTIN_TYPES:
                used_identifiers.append(
                    identifier
                )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    for line in lines:

        match = DESCRIPTION_PATTERN.match(line)

        if not match:
            continue

        value = match.group(1).strip()

        if value:
            description = value
            break

    return {
        "name": class_name,
        "file": path.relative_to(
            PROJECT_ROOT
        ).as_posix(),
        "path": path,
        "role": role,
        "system": system,
        "description": description,
        "properties": unique(properties),
        "owned_data": unique(owned_data),
        "methods": unique(methods),
        "signals": unique(signals),
        "dependencies": unique(dependencies),
        "used_identifiers": unique(
            used_identifiers
        ),
        "save_methods": unique(save_methods),
        "serializers": unique(serializers),
    }


# ============================================================
# Project Scanner
# ============================================================

def scan_project():

    files = []

    for root in GD_ROOTS:

        if not root.exists():
            continue

        for path in root.rglob("*.gd"):

            if ".godot" in path.parts:
                continue

            files.append(path)

    scanned = []

    for path in sorted(files):

        scanned.append(
            scan_gd_file(path)
        )

    return scanned


# ============================================================
# Project Class Index
# ============================================================

def build_class_index(scanned):

    result = {}

    for item in scanned:

        result[item["name"]] = item

    return result


# ============================================================
# Dependency Resolution
# ============================================================

def resolve_dependencies(
    item,
    class_index,
):
    """
    Depends Onを決定。

    1. preload/load
    2. プロジェクト内 class_name の使用
    """

    result = []

    # --------------------------------------------------------
    # preload/load
    # --------------------------------------------------------

    for dependency_path in item["dependencies"]:

        path = Path(dependency_path)

        class_name = path.stem

        if class_name in class_index:
            result.append(class_name)

    # --------------------------------------------------------
    # class_name identifiers
    # --------------------------------------------------------

    for identifier in item["used_identifiers"]:

        if identifier in class_index:
            result.append(identifier)

    # 自分自身は除外
    result = [
        x
        for x in result
        if x != item["name"]
    ]

    return unique(result)


# ============================================================
# Used By
# ============================================================

def build_used_by_map(
    scanned,
    class_index,
):
    """
    A depends on B
    ↓
    B used by A
    """

    used_by = {
        item["name"]: []
        for item in scanned
    }

    for item in scanned:

        dependencies = resolve_dependencies(
            item,
            class_index,
        )

        for dependency in dependencies:

            if dependency in used_by:

                used_by[dependency].append(
                    item["name"]
                )

    for name in used_by:

        used_by[name] = sorted(
            unique(
                used_by[name]
            )
        )

    return used_by


# ============================================================
# Save Data
# ============================================================

def resolve_save_data(item):

    methods = item["save_methods"]
    serializers = item["serializers"]

    # --------------------------------------------------------
    # Serializer
    # --------------------------------------------------------

    if serializers:

        return [
            f"Serialized via {x}"
            for x in serializers
        ]

    # --------------------------------------------------------
    # Explicit save API
    # --------------------------------------------------------

    if methods:

        return [
            f"Provides {x}"
            for x in methods
        ]

    return ["None"]

# ============================================================
# Build New System
# ============================================================

def build_new_system(item):

    fields = {
        field: []
        for field in FIELD_ORDER
    }

    fields["Purpose"] = [
        "PLACEHOLDER"
    ]

    fields["Related Files"] = [
        item["file"]
    ]

    fields["Responsibilities"] = [
        "PLACEHOLDER"
    ]

    fields["Public API Methods"] = (
        item["methods"]
        or ["Not Found"]
    )

    fields["Signals"] = (
        item["signals"]
        or ["Not Found"]
    )

    # Properties:
    # 意味的なPropertiesは既存Inventoryで管理。
    fields["Properties"] = [
        item["properties"]
        or "Not Found"
    ]

    # const / var
    fields["Owned Data"] = (
        item["owned_data"]
        or ["Not Found"]
    )

    fields["Depends On"] = [
        "Not Found"
    ]

    fields["Used By"] = [
        "Not Found"
    ]

    fields["Save Data"] = resolve_save_data(
        item
    )

    fields["Notes"] = [
        "None"
    ]

    return {
        "name": item["name"],
        "fields": fields,
    }


# ============================================================
# Merge Existing System
# ============================================================

def merge_existing_system(
    old_system,
    item,
    dependencies,
    used_by,
):
    """
    既存System。

    手動:
      Purpose
      Responsibilities
      Notes

    コード:
      Related Files
      Public API Methods
      Signals
      Owned Data
      Depends On
      Used By
      Save Data

    Properties:
      既存値を維持。
    """

    old_fields = old_system["fields"]

    fields = {
        field: list(
            old_fields.get(
                field,
                []
            )
        )
        for field in FIELD_ORDER
    }

    # --------------------------------------------------------
    # Code-generated fields
    # --------------------------------------------------------

    fields["Related Files"] = [
        item["file"]
    ]

    fields["Public API Methods"] = (
        item["methods"]
        or ["Not Found"]
    )

    fields["Signals"] = (
        item["signals"]
        or ["Not Found"]
    )

    fields["Properties"] = (
        item["properties"]
        or ["Not Found"]
    )

    fields["Owned Data"] = (
        item["owned_data"]
        or ["Not Found"]
    )

    fields["Depends On"] = (
        dependencies
        or ["Not Found"]
    )

    fields["Used By"] = (
        used_by
        or ["None"]
    )

    fields["Save Data"] = resolve_save_data(
        item
    )

    # --------------------------------------------------------
    # Manual fields are intentionally untouched:
    #
    # Purpose
    # Responsibilities
    # Notes
    #
    # Properties is also intentionally preserved.
    # --------------------------------------------------------

    return {
        "name": item["name"],
        "fields": fields,
    }


# ============================================================
# Classification Pending Layer
# ============================================================

def get_or_create_pending_layer(
    layers
):
    """
    新規System用Layer。

    既存Layerの最大番号 + 1。
    """

    existing_ids = [
        layer["id"]
        for layer in layers
    ]

    if existing_ids:
        pending_id = max(
            existing_ids
        ) + 1
    else:
        pending_id = 0

    for layer in layers:

        if (
            layer["title"]
            == CLASSIFICATION_PENDING_TITLE
        ):
            return layer

    layer = {
        "id": pending_id,
        "title": CLASSIFICATION_PENDING_TITLE,
        "systems": [],
    }

    layers.append(layer)

    return layer


# ============================================================
# Build Inventory
# ============================================================

def build_inventory(
    scanned,
    existing_layers,
):
    """
    Inventory統合。

    既存:
      Layer維持
      Manual維持
      Code更新

    新規:
      Classification Pending
      Manual = PLACEHOLDER
    """

    existing_index = index_existing_inventory(
        existing_layers
    )

    # --------------------------------------------------------
    # Copy existing layers
    # --------------------------------------------------------

    layers = []

    for layer in existing_layers:

        layers.append({
            "id": layer["id"],
            "title": layer["title"],
            "systems": [],
        })

    layer_index = {
        layer["id"]: layer
        for layer in layers
    }

    # --------------------------------------------------------
    # Ensure pending layer only when needed
    # --------------------------------------------------------

    pending_layer = None

    class_index = build_class_index(
        scanned
    )

    used_by_map = build_used_by_map(
        scanned,
        class_index,
    )

    # --------------------------------------------------------
    # Merge scanned systems
    # --------------------------------------------------------

    for item in scanned:

        name = item["name"]

        dependencies = resolve_dependencies(
            item,
            class_index,
        )

        used_by = used_by_map.get(
            name,
            [],
        )

        # ----------------------------------------------------
        # Existing
        # ----------------------------------------------------

        if name in existing_index:

            old = existing_index[name]

            layer_id = old["layer_id"]

            merged = merge_existing_system(
                old["system"],
                item,
                dependencies,
                used_by,
            )

            if layer_id not in layer_index:

                layer_index[layer_id] = {
                    "id": layer_id,
                    "title": old["layer_title"],
                    "systems": [],
                }

                layers.append(
                    layer_index[layer_id]
                )

            layer_index[layer_id][
                "systems"
            ].append(merged)

        # ----------------------------------------------------
        # New
        # ----------------------------------------------------

        else:

            if pending_layer is None:

                pending_layer = (
                    get_or_create_pending_layer(
                        layers
                    )
                )

                layer_index[
                    pending_layer["id"]
                ] = pending_layer

            new_system = build_new_system(
                item
            )

            # New system can still receive
            # automatically detected code data.
            new_system["fields"][
                "Depends On"
            ] = (
                dependencies
                or ["Not Found"]
            )

            new_system["fields"][
                "Used By"
            ] = (
                used_by
                or ["None"]
            )

            pending_layer["systems"].append(
                new_system
            )

    # --------------------------------------------------------
    # Sort layers
    # --------------------------------------------------------

    layers.sort(
        key=lambda layer: layer["id"]
    )

    return layers


# ============================================================
# Markdown Generator
# ============================================================

def markdown_values(values):

    if not values:
        return "- Not Found"

    return "\n".join(
        f"- {value}"
        for value in values
    )


def generate_inventory_markdown(
    layers
):

    output = []

    for layer in layers:

        output.append(
            f"# Layer {layer['id']}: "
            f"{layer['title']}"
        )

        output.append("")

        # System order:
        # scanned order / existing order
        for system in layer["systems"]:

            output.append(
                f"## {system['name']}"
            )

            for field in FIELD_ORDER:

                output.append(
                    f"### {field}"
                )

                values = system[
                    "fields"
                ].get(
                    field,
                    []
                )

                output.append(
                    markdown_values(values)
                )

            output.append("")

    return "\n".join(output)


# ============================================================
# AI Parser
# ============================================================

def parse_markdown_for_ai(text):

    layers = []

    current_layer = None
    current_system = None
    current_field = None

    for line in text.splitlines():

        # ----------------------------------------------------
        # Layer
        # ----------------------------------------------------

        match = LAYER_PATTERN.match(line)

        if match:

            current_layer = {
                "id": int(match.group(1)),
                "title": match.group(2).strip(),
                "systems": [],
            }

            layers.append(
                current_layer
            )

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
                "fields": {},
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

            original_name = (
                match.group(1)
                .strip()
                .rstrip(":")
            )

            current_field = FIELD_MAP.get(
                original_name
            )

            if current_field:

                current_system["fields"][
                    current_field
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
# Compact AI System
# ============================================================

def compact_system(system):

    fields = system["fields"]

    output = [
        system["name"]
    ]

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

        if len(values) == 1:

            output.append(
                f"{key}={values[0]}"
            )

        else:

            output.append(
                f"{key}="
                + ",".join(values)
            )

    return "\n".join(output)


# ============================================================
# AI Dependency
# ============================================================

def get_dependencies(system):

    values = system["fields"].get(
        "dep",
        []
    )

    return compact_values(values)


# ============================================================
# AI Output
# ============================================================

def write_ai_outputs(
    layers,
    output_directory,
):

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    map_data = {
        "src": INPUT_FILE.name,
        "layers": [],
        "deps": {},
    }

    for layer in layers:

        folder_name = make_layer_folder_name(
            layer["id"],
            layer["title"],
        )

        layer_directory = (
            output_directory
            / folder_name
        )

        layer_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        layer_map = [
            layer["id"],
            clean_layer_title(
                layer["title"]
            ),
            folder_name,
            [],
        ]

        for system in layer["systems"]:

            system_name = system["name"]

            file_name = (
                f"{sanitize_name(system_name)}.txt"
            )

            file_path = (
                layer_directory
                / file_name
            )

            text = compact_system(
                system
            )

            file_path.write_text(
                text + "\n",
                encoding="utf-8",
            )

            relative_path = (
                file_path
                .relative_to(
                    output_directory
                )
                .as_posix()
            )

            layer_map[3].append([
                system_name,
                relative_path,
            ])

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

    map_path = (
        output_directory
        / MAP_FILE_NAME
    )

    map_path.write_text(
        json.dumps(
            map_data,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    return map_path


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("Unified Inventory Generator")
    print("=" * 60)

    # --------------------------------------------------------
    # Existing Inventory
    # --------------------------------------------------------

    if INPUT_FILE.exists():

        old_text = INPUT_FILE.read_text(
            encoding="utf-8"
        )

        existing_layers = (
            parse_existing_inventory(
                old_text
            )
        )

    else:

        old_text = ""
        existing_layers = []

    existing_system_count = sum(
        len(layer["systems"])
        for layer in existing_layers
    )

    print(
        f"Existing Systems : "
        f"{existing_system_count}"
    )

    # --------------------------------------------------------
    # Scan
    # --------------------------------------------------------

    print(
        "Scanning GDScript..."
    )

    scanned = scan_project()

    print(
        f"Scanned Files    : "
        f"{len(scanned)}"
    )

    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------

    inventory = build_inventory(
        scanned,
        existing_layers,
    )

    system_count = sum(
        len(layer["systems"])
        for layer in inventory
    )

    # --------------------------------------------------------
    # Markdown
    # --------------------------------------------------------

    new_text = (
        generate_inventory_markdown(
            inventory
        )
    )

    INPUT_FILE.write_text(
        new_text,
        encoding="utf-8",
    )

    print(
        f"Inventory Updated: "
        f"{INPUT_FILE}"
    )

    # --------------------------------------------------------
    # AI Output
    # --------------------------------------------------------

    ai_layers = parse_markdown_for_ai(
        new_text
    )

    map_path = write_ai_outputs(
        ai_layers,
        OUTPUT_DIRECTORY,
    )

    print(
        f"AI Map           : "
        f"{map_path}"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    pending = next(
        (
            layer
            for layer in inventory
            if layer["title"]
            == CLASSIFICATION_PENDING_TITLE
        ),
        None,
    )

    pending_count = (
        len(pending["systems"])
        if pending
        else 0
    )

    print()
    print("=" * 60)
    print("Completed")
    print("=" * 60)

    print(
        f"Layers           : "
        f"{len(inventory)}"
    )

    print(
        f"Systems          : "
        f"{system_count}"
    )

    print(
        f"Pending          : "
        f"{pending_count}"
    )

    print(
        f"AI Output        : "
        f"{OUTPUT_DIRECTORY}"
    )


if __name__ == "__main__":
    main()
