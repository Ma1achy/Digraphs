"""Grid drawing of a collection of 4-vertex digraphs to a single PNG.

Rendering choices that carry the visual load:

* a fixed ``circular_layout`` for the four nodes, identical across every subplot,
  so shapes are comparable at a glance;
* antiparallel pairs (``u -> v`` and ``v -> u`` both present) drawn as curved
  arcs that bow apart, never collapsing into one line;
* self-loops rendered explicitly as small circles at each looped node (networkx's
  own loop rendering is unreliable across versions, so we draw them ourselves);
* each subplot titled with its edge list.

Uses the headless ``Agg`` backend so it works inside a container with no display.
"""

from __future__ import annotations

import math
from typing import List, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

from .graphs import N, mask_to_edges  # noqa: E402

# Stable node positions shared by every subplot.
_LAYOUT = nx.circular_layout(nx.empty_graph(N))
_ARC_RAD = 0.25  # how far antiparallel arcs bow apart


def _edge_label(edges: Sequence) -> str:
    """Compact one-line label, e.g. ``(0,1) (1,2) (2,3)``; ``∅`` when empty."""
    if not edges:
        return "∅"
    return " ".join(f"({u},{v})" for u, v in edges)


def _draw_one(ax, mask: int) -> None:
    edges = mask_to_edges(mask)
    loops = [(u, v) for u, v in edges if u == v]
    non_loops = [(u, v) for u, v in edges if u != v]
    present = set(non_loops)

    graph = nx.DiGraph()
    graph.add_nodes_from(range(N))
    graph.add_edges_from(non_loops)

    nx.draw_networkx_nodes(graph, _LAYOUT, ax=ax, node_color="#dbe4ff",
                           edgecolors="#33447a", node_size=650)
    nx.draw_networkx_labels(graph, _LAYOUT, ax=ax, font_size=11)

    # Directed edges: bow antiparallel pairs apart so both stay visible.
    for u, v in non_loops:
        rad = _ARC_RAD if (v, u) in present else 0.0
        ax.annotate(
            "",
            xy=_LAYOUT[v],
            xytext=_LAYOUT[u],
            arrowprops=dict(
                arrowstyle="-|>",
                color="#33447a",
                shrinkA=13,
                shrinkB=13,
                connectionstyle=f"arc3,rad={rad}",
                lw=1.4,
            ),
        )

    # Self-loops: a directed arc that bulges outward from the node, sitting
    # clear of the node marker (which is large enough to occlude a plain circle).
    # Drawn with a high zorder and an arrowhead so it reads as a directed loop.
    _node_r = 0.22  # approx node-marker radius in data coords, for anchoring
    for u, _ in loops:
        x, y = _LAYOUT[u]
        norm = math.hypot(x, y) or 1.0
        ux, uy = x / norm, y / norm          # outward radial unit vector
        tx, ty = -uy, ux                      # tangent unit vector
        off = 0.10
        start = (x + ux * _node_r - tx * off, y + uy * _node_r - ty * off)
        end = (x + ux * _node_r + tx * off, y + uy * _node_r + ty * off)
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            zorder=5,
            arrowprops=dict(
                arrowstyle="-|>",
                color="#a8324a",
                connectionstyle="arc3,rad=3.0",
                lw=1.5,
            ),
        )

    ax.set_title(_edge_label(edges), fontsize=7)
    ax.set_xlim(-1.85, 1.85)
    ax.set_ylim(-1.85, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")


def draw_grid(masks: List[int], path: str, title: str | None = None,
              cols: int = 8) -> str:
    """Draw every mask in ``masks`` as a subplot grid and save to ``path``.

    Returns ``path``. An empty ``masks`` still writes a (near-empty) figure.
    """
    n = len(masks)
    cols = max(1, min(cols, n)) if n else 1
    rows = max(1, math.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 2.3 * rows),
                             squeeze=False)
    for idx in range(rows * cols):
        ax = axes[idx // cols][idx % cols]
        if idx < n:
            _draw_one(ax, masks[idx])
        else:
            ax.axis("off")

    if title:
        fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97 if title else 1.0))
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path
