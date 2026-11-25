#!/usr/bin/env python3
"""
generate_all_charts.py

既存のArchitecture Chartツールをまとめて実行する。

通常:
    generate_charts_v2.py

--trace:
    flow_trace.py

--skeleton:
    flow_chart.py prompt / check

解析ロジックは既存スクリプトに任せる。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("\n[RUN] " + subprocess.list2cmdline(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate architecture, runtime trace, and gameplay charts."
    )

    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="tools/architecture/output"
    )
    parser.add_argument(
        "--with-tests",
        action="store_true"
    )

    parser.add_argument(
        "--trace",
        nargs="+",
        default=None,
        help="Runtime trace seeds: Class.func or Class"
    )
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--cap", type=int, default=60)
    parser.add_argument("--labels", default=None)

    parser.add_argument(
        "--skeleton",
        default=None,
        help="Gameplay skeleton file"
    )
    parser.add_argument(
        "--inventory",
        default=None,
        help="Optional inventory markdown for gameplay prompt"
    )
    parser.add_argument(
        "--evidence",
        default=None,
        help="LLM evidence JSON. If omitted, generate evidence_prompt.md"
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output

    output.mkdir(parents=True, exist_ok=True)

    arch = root / "tools" / "architecture"

    # 1. 全体構造を最新状態にする
    command = [
        sys.executable,
        str(arch / "generate_charts_v2.py"),
        "--root",
        str(root),
        "--output",
        str(output),
    ]

    if args.with_tests:
        command.append("--with-tests")

    run(command, root)

    # 2. 指定されたRuntime Pathだけを追跡する
    if args.trace:
        command = [
            sys.executable,
            str(arch / "flow_trace.py"),
            "--root",
            str(root),
            "--output",
            str(output),
            "trace",
            "--from",
            *args.trace,
            "--depth",
            str(args.depth),
            "--cap",
            str(args.cap),
        ]

        if args.labels:
            command.extend([
                "--labels",
                str(Path(args.labels).resolve())
            ])

        run(command, root)

    # 3. Gameplay Skeletonが指定された場合だけ実行する
    if args.skeleton:
        skeleton = Path(args.skeleton)
        if not skeleton.is_absolute():
            skeleton = root / skeleton

        if not skeleton.is_file():
            raise SystemExit(
                f"[ERROR] Skeleton not found: {skeleton}"
            )

        if args.evidence:
            evidence = Path(args.evidence)
            if not evidence.is_absolute():
                evidence = root / evidence

            if not evidence.is_file():
                raise SystemExit(
                    f"[ERROR] Evidence not found: {evidence}"
                )

            command = [
                sys.executable,
                str(arch / "flow_chart.py"),
                "check",
                str(skeleton),
                str(evidence),
                "--output",
                str(output),
            ]
        else:
            command = [
                sys.executable,
                str(arch / "flow_chart.py"),
                "prompt",
                str(skeleton),
                "--output",
                str(output),
            ]

            if args.inventory:
                inventory = Path(args.inventory)
                if not inventory.is_absolute():
                    inventory = root / inventory

                command.extend([
                    "--inventory",
                    str(inventory)
                ])

        run(command, root)

    print("\n[DONE] Chart generation completed.")
    print(f"[OUTPUT] {output}")


if __name__ == "__main__":
    main()