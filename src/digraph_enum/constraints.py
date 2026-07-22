"""Constraints on a 4-vertex digraph, defined by its small induced subgraphs.

Two ingredients:

* **L** — the list of allowed 3-vertex patterns, loaded from the pickle. Each of
  a graph's four induced 3-vertex subgraphs (obtained by deleting one vertex)
  must be isomorphic to some member of L. This is the Task 1 condition,
  property (ii).

* **H / property (i)** — a fixed 4-vertex pattern
  ``H = ({0,1,2,3}, {(0,1), (0,2), (3,2)})`` with an interrogated arrow ``(3,0)``
  that is *not* an edge of H. Over all bijections that embed H into G, we inspect
  whether that arrow is present or absent.

L is never hardcoded here — it is always read from the pickle so the tool stays
correct if the list is regenerated.
"""

from __future__ import annotations

import pickle
from itertools import combinations, permutations
from pathlib import Path
from typing import List, Set, Tuple

import networkx as nx

from .graphs import N, PERMS

# --- 3-vertex canonical forms (for L membership) ---------------------------

_N3 = 3
_PERMS3: Tuple[Tuple[int, ...], ...] = tuple(permutations(range(_N3)))


def _canonical3(mask3: int) -> int:
    """Canonical form of a 3-vertex mask (9 bits): min over the 6 relabellings."""
    best = mask3
    for perm in _PERMS3:
        relabelled = 0
        for u in range(_N3):
            for v in range(_N3):
                if mask3 >> (_N3 * u + v) & 1:
                    relabelled |= 1 << (_N3 * perm[u] + perm[v])
        if relabelled < best:
            best = relabelled
    return best


def _digraph_to_mask3(g: "nx.DiGraph") -> int:
    """Encode a networkx DiGraph on nodes {0,1,2} as a 9-bit mask."""
    mask = 0
    for u, v in g.edges():
        mask |= 1 << (_N3 * u + v)
    return mask


# --- Loading L -------------------------------------------------------------


def load_L_digraphs(path) -> List["nx.DiGraph"]:
    """Load the raw list L of 3-vertex DiGraphs from the pickle."""
    with open(Path(path), "rb") as fh:
        graphs = pickle.load(fh)
    return list(graphs)


def load_L(path) -> Set[int]:
    """Load L and return the set of canonical 3-vertex masks it represents.

    Membership in this set is exactly "isomorphic to some graph in L".
    """
    return {_canonical3(_digraph_to_mask3(g)) for g in load_L_digraphs(path)}


# --- Induced 3-vertex subgraphs (of a 4-vertex mask) -----------------------


def induced3(mask: int, subset: Tuple[int, int, int]) -> int:
    """Induced subgraph of ``mask`` on the 3 vertices ``subset``.

    Vertices in ``subset`` are relabelled to ``0, 1, 2`` by their position, and
    exactly the edges (including loops) with both endpoints in ``subset`` are
    kept. Returns a 9-bit mask.
    """
    index = {v: i for i, v in enumerate(subset)}
    result = 0
    for a in subset:
        for b in subset:
            if mask >> (N * a + b) & 1:
                result |= 1 << (_N3 * index[a] + index[b])
    return result


def all_subgraphs_in_L(mask: int, l_set: Set[int]) -> bool:
    """True iff all four induced 3-vertex subgraphs of ``mask`` lie in L.

    This is property (ii) — the Task 1 condition.
    """
    for subset in combinations(range(N), _N3):
        if _canonical3(induced3(mask, subset)) not in l_set:
            return False
    return True


# --- H / property (i) ------------------------------------------------------

# H = ({0,1,2,3}, {(0,1), (0,2), (3,2)}); interrogated arrow (3,0).
H_EDGES: Tuple[Tuple[int, int], ...] = ((0, 1), (0, 2), (3, 2))
H_ARROW: Tuple[int, int] = (3, 0)


def _edge_present(mask: int, u: int, v: int) -> bool:
    return bool(mask >> (N * u + v) & 1)


def property_i(mask: int, strict_both: bool = False) -> bool:
    """Evaluate property (i) for the digraph ``mask``.

    Over all 24 bijections ``phi`` that embed H into ``mask`` (all three H-edges
    present), inspect the interrogated arrow ``phi(3) -> phi(0)``:

    * default (``strict_both=False``): at least one embedding has it **absent**;
    * strict (``strict_both=True``): at least one embedding has it **absent** and
      at least one (possibly different) embedding has it **present**.

    A graph with no H-embedding at all satisfies neither, so returns ``False``.
    """
    saw_absent = False
    saw_present = False
    a_src, a_dst = H_ARROW
    for phi in PERMS:
        if not all(_edge_present(mask, phi[u], phi[v]) for u, v in H_EDGES):
            continue
        if _edge_present(mask, phi[a_src], phi[a_dst]):
            saw_present = True
        else:
            saw_absent = True
    if strict_both:
        return saw_absent and saw_present
    return saw_absent
