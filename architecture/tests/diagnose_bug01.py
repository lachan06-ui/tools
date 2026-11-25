"""Diagnose the clean-vs-original issue for BUG-01 fix."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "m", pathlib.Path(__file__).parent.parent / "generate_charts_fixed.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

strip = m.strip_comments_and_strings

# The key insight: strip_comments_and_strings removes the CONTENT of strings,
# not just the quotes. So `preload("res://foo.gd")` becomes `preload(              )`
# after cleaning. Therefore, PRELOAD cannot match on clean.

src1 = 'const Live = preload("res://live.gd")\n'
clean1 = strip(src1)
print("src1    :", repr(src1))
print("clean1  :", repr(clean1))
# → clean1 will be: 'const Live = preload(              )\n'
# PRELOAD cannot match this.

print()
print("CONCLUSION:")
print("  preloads must be scanned on `original`, not `clean`.")
print("  The correct BUG-01 fix is to use strip_comments_per_line()")
print("  — strip only the comment part of each line, preserving string content.")
print("  OR: use original but apply a line-level comment filter.")

# Demonstrate the correct approach: line-level comment stripping
import re

COMMENT_ONLY_LINE = re.compile(r'^\s*#.*$', re.M)

def strip_comment_lines(source: str) -> str:
    """Remove lines that are purely comments (start with optional whitespace then #).
    This preserves string content (including paths in preload/emit_signal) while
    excluding false positives from comment-only lines."""
    lines = source.splitlines(keepends=True)
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            # Replace with blank line to preserve line numbers
            result.append('\n')
        else:
            result.append(line)
    return ''.join(result)

src2 = '# const Dead = preload("res://dead.gd")\nconst Live = preload("res://live.gd")\n'
filtered = strip_comment_lines(src2)
print()
print("strip_comment_lines result:", repr(filtered))
found = [x.group(1) for x in m.PRELOAD.finditer(filtered)]
print("PRELOAD found:", found)
# Should give: ['res://live.gd'] only

# Also test inline comment (non-comment-only line with trailing #)
src3 = 'const X = preload("res://ok.gd")  # some comment\n'
filtered3 = strip_comment_lines(src3)
found3 = [x.group(1) for x in m.PRELOAD.finditer(filtered3)]
print()
print("Inline comment line kept:", repr(filtered3))
print("PRELOAD found:", found3)  # Should find res://ok.gd
