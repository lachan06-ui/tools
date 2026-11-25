from pathlib import Path

ROOT = Path(".")  # プロジェクトルートで実行

IGNORE = {
    ".godot",
    ".git",
    "__pycache__",
    ".import",
    ".vs",
    ".idea"
}

def print_tree(path: Path, prefix=""):
    items = sorted(
        [p for p in path.iterdir() if p.name not in IGNORE],
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, item in enumerate(items):
        last = i == len(items) - 1
        if item.name.endswith((".png", ".import", ".uid", ".tmp", ".res", ".svg")):
            continue
        connector = "└── " if last else "├── "

        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if last else "│   "
            print_tree(item, prefix + extension)

print(ROOT.resolve().name)
print_tree(ROOT)