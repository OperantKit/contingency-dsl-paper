"""Command-line entrypoint: JSON AST file/stdin -> Method section text.

Usage:
    contingency-dsl-paper INPUT [--style jeab|jaba] [--output PATH]
                                [--heading-level N] [--all-experiments]

    INPUT is a path to a JSON file, or "-" to read from stdin.

Exit codes:
    0  success
    1  I/O error (missing file, permission denied)
    2  invalid JSON
    3  unknown style
    4  invalid AST (empty or unsupported root type)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .compiler import compile_method, compile_paper
from .model import MethodSection
from .style import STYLES, get_style

EXIT_OK = 0
EXIT_IO = 1
EXIT_JSON = 2
EXIT_STYLE = 3
EXIT_AST = 4


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contingency-dsl-paper",
        description=(
            "Compile a contingency-dsl JSON AST into a Method section "
            "for academic papers (JEAB/JABA style)."
        ),
    )
    parser.add_argument(
        "input",
        help='Path to JSON AST file, or "-" to read from stdin.',
    )
    parser.add_argument(
        "--style",
        default="jeab",
        help=(
            f"Output style (default: jeab). "
            f"Built-in: {', '.join(sorted(STYLES.keys()))}."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path (default: stdout).",
    )
    parser.add_argument(
        "--heading-level",
        type=int,
        default=2,
        help="Markdown heading depth for the Method header (default: 2).",
    )
    parser.add_argument(
        "--all-experiments",
        action="store_true",
        help=(
            "For Paper inputs, render every experiment. "
            "Default renders only the first."
        ),
    )
    return parser


def _load_json(source: str) -> dict:
    if source == "-":
        return json.load(sys.stdin)
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(source)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _render_paper(
    ast: dict, *, style_name: str, heading_level: int
) -> str:
    sections = compile_paper(ast, style=style_name)
    if not sections:
        return ""
    style = get_style(style_name)
    top = "#" * heading_level
    blocks: list[str] = []
    for label, method in sections:
        body = method.to_text(heading_level=heading_level + 1)
        if label:
            blocks.append(f"{top} {style.heading_method}: {label}\n\n{body}")
        else:
            blocks.append(body)
    return "\n".join(blocks)


def _render_single(
    ast: dict, *, style_name: str, heading_level: int
) -> str:
    method: MethodSection = compile_method(ast, style=style_name)
    return method.to_text(heading_level=heading_level)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        ast = _load_json(args.input)
    except FileNotFoundError as e:
        print(f"error: input file not found: {e}", file=sys.stderr)
        return EXIT_IO
    except OSError as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return EXIT_IO
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return EXIT_JSON

    try:
        get_style(args.style)
    except KeyError:
        print(f"error: unknown style: {args.style!r}", file=sys.stderr)
        return EXIT_STYLE

    if not isinstance(ast, dict) or not ast.get("type"):
        print("error: AST root must be a dict with a 'type' field", file=sys.stderr)
        return EXIT_AST

    if ast.get("type") == "Paper" and args.all_experiments:
        text = _render_paper(
            ast, style_name=args.style, heading_level=args.heading_level
        )
    else:
        text = _render_single(
            ast, style_name=args.style, heading_level=args.heading_level
        )

    if args.output is None:
        sys.stdout.write(text)
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
