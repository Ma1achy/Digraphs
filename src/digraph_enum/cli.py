"""Command-line interface: run both tasks, print counts + edge lists, optionally draw."""

from __future__ import annotations

import argparse
from typing import List, Sequence

from .graphs import mask_to_edges
from .tasks import DEFAULT_DATA, task1, task2


def _format_edges(masks: Sequence[int]) -> List[str]:
    lines = []
    for i, mask in enumerate(masks, start=1):
        edges = mask_to_edges(mask)
        rendered = ", ".join(f"({u},{v})" for u, v in edges) if edges else "(no edges)"
        lines.append(f"  {i:>3}. {rendered}")
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Enumerate 4-vertex digraphs (self-loops allowed) up to isomorphism "
            "and filter them by constraints on their induced 3-vertex subgraphs. "
            "Runs both tasks and prints the counts and edge lists."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "tasks:\n"
            "  Task 1  every induced 3-vertex subgraph is isomorphic to one in L\n"
            "  Task 2  Task 1 graphs that also satisfy property (i) on the H-pattern\n\n"
            "examples:\n"
            "  python main.py                 # print both tasks' counts + edge lists\n"
            "  python main.py --draw          # also write task1.png and task2.png\n"
            "  python main.py --strict-both   # use strict mode for property (i)\n"
            "  python main.py --data path/to/my_graphs.pkl\n"
        ),
    )
    parser.add_argument(
        "--strict-both",
        action="store_true",
        help=(
            "Use strict mode for property (i) in Task 2: require an H-embedding "
            "with the interrogated arrow ABSENT *and* one with it PRESENT "
            "(default mode only requires an absent one)."
        ),
    )
    parser.add_argument(
        "--draw",
        action="store_true",
        help="Write task1.png and task2.png (grids of the resulting digraphs).",
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA,
        metavar="PATH",
        help=f"Path to the pickle holding the list L (default: {DEFAULT_DATA}).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        t1 = task1(args.data)
        t2 = task2(args.data, strict_both=args.strict_both, task1_masks=t1)
    except FileNotFoundError:
        parser = build_parser()
        parser.error(
            f"could not find the data pickle at '{args.data}'. "
            "Pass its location with --data PATH (default is data/my_graphs.pkl)."
        )

    mode = "strict" if args.strict_both else "default"

    print(f"Task 1  (all induced 3-vertex subgraphs in L): {len(t1)} graphs")
    print("\n".join(_format_edges(t1)))
    print()
    print(f"Task 2  (Task 1 + property (i), {mode} mode): {len(t2)} graphs")
    print("\n".join(_format_edges(t2)))

    if args.draw:
        from .draw import draw_grid

        p1 = draw_grid(t1, "task1.png", title=f"Task 1 — {len(t1)} digraphs")
        p2 = draw_grid(
            t2, "task2.png",
            title=f"Task 2 ({mode}) — {len(t2)} digraphs",
        )
        print()
        print(f"Wrote {p1} and {p2}.")

    return 0
