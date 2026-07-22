"""Enumerate 4-vertex digraphs (loops allowed) up to isomorphism, then filter
them by constraints on their induced 3-vertex subgraphs.

Public surface:
    graphs      - bitmask <-> edge-list, canonical form, class enumeration
    constraints - load L, induced-subgraph check, H / property (i)
    tasks       - task1(), task2(strict_both=False)
    draw        - grid drawing of a set of digraphs to a PNG
"""

from .graphs import (
    N,
    canonical_form,
    edges_to_mask,
    enumerate_classes,
    mask_to_edges,
)

__all__ = [
    "N",
    "canonical_form",
    "edges_to_mask",
    "enumerate_classes",
    "mask_to_edges",
]
