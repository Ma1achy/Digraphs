"""Bitmask representation of 4-vertex digraphs, canonical forms, and enumeration.

A digraph on ``N = 4`` vertices (self-loops allowed) is encoded as a 16-bit
integer ``mask``: bit ``N*u + v`` is set iff the edge ``u -> v`` is present.
The four loop bits are the diagonal ``0, 5, 10, 15``. There are ``2**16 = 65536``
labelled digraphs.

Two digraphs are isomorphic iff one can be relabelled onto the other. The
*canonical form* of a mask is the minimum, over all 24 vertex relabellings, of
the permuted mask. Isomorphic graphs share a canonical form; non-isomorphic
graphs do not. Enumerating the distinct canonical forms gives one representative
per isomorphism class (there are exactly 3044).
"""

from __future__ import annotations

from itertools import permutations
from typing import List, Tuple

import numpy as np

N = 4
_EDGES = N * N  # 16 possible ordered pairs, including loops

# The 24 vertex relabellings of {0, 1, 2, 3}.
PERMS: Tuple[Tuple[int, ...], ...] = tuple(permutations(range(N)))


def _bit_moves(perm: Tuple[int, ...]) -> List[Tuple[int, int]]:
    """For a vertex permutation, the (source_bit, dest_bit) pairs it induces.

    Edge ``u -> v`` (bit ``N*u + v``) becomes ``perm[u] -> perm[v]``
    (bit ``N*perm[u] + perm[v]``).
    """
    moves = []
    for u in range(N):
        for v in range(N):
            src = N * u + v
            dst = N * perm[u] + perm[v]
            moves.append((src, dst))
    return moves


# Precomputed bit relocations per permutation — used by both the scalar and the
# vectorised canonical-form routines.
_PERM_MOVES: Tuple[Tuple[Tuple[int, int], ...], ...] = tuple(
    tuple(_bit_moves(p)) for p in PERMS
)


def edges_to_mask(edges, n: int = N) -> int:
    """Build a mask from an iterable of ``(u, v)`` ordered pairs."""
    mask = 0
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"edge ({u}, {v}) out of range for n={n}")
        mask |= 1 << (n * u + v)
    return mask


def mask_to_edges(mask: int, n: int = N) -> List[Tuple[int, int]]:
    """Return the sorted edge list ``[(u, v), ...]`` encoded by ``mask``."""
    edges = []
    for u in range(n):
        for v in range(n):
            if mask >> (n * u + v) & 1:
                edges.append((u, v))
    return edges


def permute_mask(mask: int, perm_index: int) -> int:
    """Relabel ``mask`` by ``PERMS[perm_index]`` and return the new mask."""
    result = 0
    for src, dst in _PERM_MOVES[perm_index]:
        if mask >> src & 1:
            result |= 1 << dst
    return result


def canonical_form(mask: int) -> int:
    """Canonical form of a single 4-vertex mask: min over the 24 relabellings."""
    best = mask
    for moves in _PERM_MOVES:
        relabelled = 0
        for src, dst in moves:
            if mask >> src & 1:
                relabelled |= 1 << dst
        if relabelled < best:
            best = relabelled
    return best


def _all_canonical_forms() -> np.ndarray:
    """Vectorised canonical form for every mask ``0 .. 65535``.

    Returns an array ``canon`` of length 65536 where ``canon[m]`` is the
    canonical form of mask ``m``. Runs effectively instantly.
    """
    masks = np.arange(1 << _EDGES, dtype=np.uint32)
    best = masks.copy()
    for moves in _PERM_MOVES:
        relabelled = np.zeros_like(masks)
        for src, dst in moves:
            bit = (masks >> np.uint32(src)) & np.uint32(1)
            relabelled |= bit << np.uint32(dst)
        np.minimum(best, relabelled, out=best)
    return best


def enumerate_classes() -> List[int]:
    """Return one representative mask per isomorphism class, sorted ascending.

    Each representative is the canonical form of its class, so the list has no
    duplicates. There are exactly 3044 such classes.
    """
    canon = _all_canonical_forms()
    return sorted(int(m) for m in np.unique(canon))
