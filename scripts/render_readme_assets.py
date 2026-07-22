#!/usr/bin/env python3
"""Regenerate every image used by README.md into ``assets/``.

Deterministic: given the committed ``data/my_graphs.pkl`` it always produces the
same PNGs. Reuses the package's own drawing code (``digraph_enum.draw``) for the
four-vertex panels, and mirrors its visual style (same palette, same self-loop
and antiparallel-arc treatment) for the three-vertex alphabet, the H figure, and
the include/exclude figure.

Run from anywhere:

    python scripts/render_readme_assets.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from digraph_enum.draw import _ARC_RAD, _LAYOUT, _draw_one, draw_grid  # noqa: E402
from digraph_enum.constraints import load_L_digraphs  # noqa: E402
from digraph_enum.graphs import edges_to_mask  # noqa: E402
from digraph_enum.tasks import task1, task2  # noqa: E402

ASSETS = ROOT / "assets"
DATA = ROOT / "data" / "my_graphs.pkl"

# Palette, matched to digraph_enum.draw.
NODE_FILL = "#dbe4ff"
NODE_EDGE = "#33447a"
EDGE_COLOR = "#33447a"
LOOP_COLOR = "#a8324a"
FREE_COLOR = "#8a8f9a"
OK_COLOR = "#2f8f4e"
NO_COLOR = "#b23a48"

# Stable triangle layout for three-vertex drawings.
_LAYOUT3 = nx.circular_layout(nx.empty_graph(3))
_NODE_R = 0.22


def _draw_loops(ax, layout, looped_nodes, color=LOOP_COLOR):
    """Directed self-loops bulging outward from each node (same style as draw.py)."""
    for u in looped_nodes:
        x, y = layout[u]
        norm = math.hypot(x, y) or 1.0
        ux, uy = x / norm, y / norm
        tx, ty = -uy, ux
        off = 0.10
        start = (x + ux * _NODE_R - tx * off, y + uy * _NODE_R - ty * off)
        end = (x + ux * _NODE_R + tx * off, y + uy * _NODE_R + ty * off)
        ax.annotate(
            "", xy=end, xytext=start, zorder=5,
            arrowprops=dict(arrowstyle="-|>", color=color,
                            connectionstyle="arc3,rad=3.0", lw=1.5),
        )


def _draw_three(ax, digraph, node_size=650, font_size=11):
    """Draw a three-vertex DiGraph on nodes {0,1,2} in the shared triangle layout."""
    edges = list(digraph.edges())
    loops = [u for u, v in edges if u == v]
    non_loops = [(u, v) for u, v in edges if u != v]
    present = set(non_loops)

    g = nx.DiGraph()
    g.add_nodes_from(range(3))
    g.add_edges_from(non_loops)

    nx.draw_networkx_nodes(g, _LAYOUT3, ax=ax, node_color=NODE_FILL,
                           edgecolors=NODE_EDGE, node_size=node_size)
    nx.draw_networkx_labels(g, _LAYOUT3, ax=ax, font_size=font_size)
    for u, v in non_loops:
        rad = _ARC_RAD if (v, u) in present else 0.0
        ax.annotate("", xy=_LAYOUT3[v], xytext=_LAYOUT3[u],
                    arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR,
                                    shrinkA=13, shrinkB=13,
                                    connectionstyle=f"arc3,rad={rad}", lw=1.4))
    _draw_loops(ax, _LAYOUT3, loops)
    ax.set_xlim(-1.85, 1.85)
    ax.set_ylim(-1.85, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")


# --- the two big grids -----------------------------------------------------


def render_grids():
    t1 = task1(str(DATA))
    t2 = task2(str(DATA), task1_masks=t1)
    draw_grid(t1, str(ASSETS / "task1.png"), title=None, cols=9)
    # Four across (two rows) so the dense edge-list captions have room to breathe.
    draw_grid(t2, str(ASSETS / "task2.png"), title=None, cols=4)
    return len(t1), len(t2)


# --- H, with the free 4->1 arrow -------------------------------------------


def render_H():
    # H on vertices 1,2,3,4 (1-indexed for the figure): edges 1->2, 1->3, 4->3.
    # The interrogated arrow 4->1 is NOT an edge of H — drawn dashed and grey.
    pos = {1: (-1.0, 1.0), 2: (1.0, 1.0), 3: (1.0, -1.0), 4: (-1.0, -1.0)}
    solid = [(1, 2), (1, 3), (4, 3)]

    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    g = nx.DiGraph()
    g.add_nodes_from(pos)
    nx.draw_networkx_nodes(g, pos, ax=ax, node_color=NODE_FILL,
                           edgecolors=NODE_EDGE, node_size=1200)
    nx.draw_networkx_labels(g, pos, ax=ax, font_size=15,
                            labels={n: str(n) for n in pos})
    for u, v in solid:
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR,
                                    shrinkA=18, shrinkB=18, lw=2.0))
    # The free adjacency 4 -> 1, dashed and grey.
    ax.annotate("", xy=pos[1], xytext=pos[4],
                arrowprops=dict(arrowstyle="-|>", color=FREE_COLOR,
                                shrinkA=18, shrinkB=18, lw=2.0,
                                linestyle=(0, (4, 3))))
    ax.text(-1.62, 0.0, "4→1\nfree", color=FREE_COLOR, fontsize=11,
            ha="center", va="center", style="italic")
    ax.set_xlim(-2.1, 1.7)
    ax.set_ylim(-1.7, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("H = (1→2, 1→3, 4→3);  4→1 is the arrow Task 2 probes",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(ASSETS / "H.png", dpi=130)
    plt.close(fig)


# --- the 21-pattern alphabet L ---------------------------------------------


def render_alphabet():
    graphs = load_L_digraphs(str(DATA))
    cols = 7
    rows = math.ceil(len(graphs) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(2.0 * cols, 2.2 * rows),
                             squeeze=False)
    for idx in range(rows * cols):
        ax = axes[idx // cols][idx % cols]
        if idx < len(graphs):
            _draw_three(ax, graphs[idx], node_size=430, font_size=9)
            edges = sorted(graphs[idx].edges())
            label = " ".join(f"({u},{v})" for u, v in edges) if edges else "∅"
            ax.set_title(f"L{idx}   {label}", fontsize=7)
        else:
            ax.axis("off")
    fig.suptitle("L — the 21 allowed 3-vertex patterns", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(ASSETS / "alphabet.png", dpi=120)
    plt.close(fig)


# --- must-include / must-exclude -------------------------------------------


def render_include_exclude():
    include = [
        ("directed 4-cycle", [(0, 1), (1, 2), (2, 3), (3, 0)]),
        ("complete + all loops", [(u, v) for u in range(4) for v in range(4)]),
        ("directed path 0→1→2→3", [(0, 1), (1, 2), (2, 3)]),
    ]
    exclude = [
        ("4-cycle + one loop", [(0, 1), (1, 2), (2, 3), (3, 0), (0, 0)]),
        ("complete, one loop missing",
         [(u, v) for u in range(4) for v in range(4) if (u, v) != (3, 3)]),
        ("path + loop at start", [(0, 1), (1, 2), (2, 3), (0, 0)]),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(9.6, 6.6), squeeze=False)
    for col, (name, edges) in enumerate(include):
        ax = axes[0][col]
        _draw_one(ax, edges_to_mask(edges))
        ax.set_title(f"✓  {name}", fontsize=10, color=OK_COLOR)
    for col, (name, edges) in enumerate(exclude):
        ax = axes[1][col]
        _draw_one(ax, edges_to_mask(edges))
        ax.set_title(f"✗  {name}", fontsize=10, color=NO_COLOR)

    fig.text(0.5, 0.965, "In Task 1 — every 3-vertex window is legal",
             ha="center", fontsize=11, color=OK_COLOR, weight="bold")
    fig.text(0.5, 0.475, "Out — one 3-vertex window is not in L",
             ha="center", fontsize=11, color=NO_COLOR, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.subplots_adjust(hspace=0.35)
    fig.savefig(ASSETS / "include-exclude.png", dpi=120)
    plt.close(fig)


def main():
    ASSETS.mkdir(exist_ok=True)
    n1, n2 = render_grids()
    render_H()
    render_alphabet()
    render_include_exclude()
    written = ["task1.png", "task2.png", "H.png", "alphabet.png",
               "include-exclude.png"]
    print(f"Task 1 = {n1} graphs, Task 2 = {n2} graphs.")
    for name in written:
        p = ASSETS / name
        print(f"  wrote assets/{name}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
