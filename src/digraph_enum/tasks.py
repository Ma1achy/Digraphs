"""The two enumeration tasks.

Both properties are isomorphism-invariant, so they are evaluated once per class
representative (~3044 checks), not per labelled graph.

Task 1 (property (ii)): every induced 3-vertex subgraph is in L.
Task 2 (properties (i) and (ii)): Task 1, plus property (i) on the H-pattern.
Task 2 is built by filtering Task 1, so ``task2 ⊆ task1`` structurally.
"""

from __future__ import annotations

from typing import List, Set

from .constraints import all_subgraphs_in_L, load_L, property_i
from .graphs import enumerate_classes

DEFAULT_DATA = "data/my_graphs.pkl"


def task1(data_path: str = DEFAULT_DATA, l_set: Set[int] | None = None) -> List[int]:
    """Representative masks of every class whose 4 induced 3-subgraphs are in L."""
    if l_set is None:
        l_set = load_L(data_path)
    return [m for m in enumerate_classes() if all_subgraphs_in_L(m, l_set)]


def task2(
    data_path: str = DEFAULT_DATA,
    strict_both: bool = False,
    l_set: Set[int] | None = None,
    task1_masks: List[int] | None = None,
) -> List[int]:
    """Task 1 masks that additionally satisfy property (i).

    ``task1_masks`` may be passed to reuse an already-computed Task 1 result.
    """
    if l_set is None:
        l_set = load_L(data_path)
    if task1_masks is None:
        task1_masks = task1(data_path, l_set=l_set)
    return [m for m in task1_masks if property_i(m, strict_both=strict_both)]
