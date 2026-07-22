"""Irene's hand-checked reference cases for Task 1.

These are the six specific graphs Irene verified by hand — three that must be in
Task 1 and three that must not. One assertion per graph, named by case, kept
separate from the count and invariant tests so they read as what they are: a
human's spot-check of the tool.
"""

from digraph_enum.graphs import canonical_form, edges_to_mask

ALL_16 = [(u, v) for u in range(4) for v in range(4)]
ALL_16_MINUS_LOOP = [(u, v) for u in range(4) for v in range(4) if (u, v) != (3, 3)]


def _in_task1(edges, task1_masks) -> bool:
    return canonical_form(edges_to_mask(edges)) in set(task1_masks)


def test_irene_reference_cases(task1_masks):
    # --- must include ---
    assert _in_task1([(0, 1), (1, 2), (2, 3), (3, 0)], task1_masks), \
        "directed 4-cycle should be in Task 1"
    assert _in_task1(ALL_16, task1_masks), \
        "complete digraph with all loops should be in Task 1"
    assert _in_task1([(0, 1), (1, 2), (2, 3)], task1_masks), \
        "directed path 0->1->2->3 should be in Task 1"

    # --- must exclude ---
    assert not _in_task1([(0, 1), (1, 2), (2, 3), (3, 0), (0, 0)], task1_masks), \
        "directed 4-cycle plus one loop should NOT be in Task 1"
    assert not _in_task1(ALL_16_MINUS_LOOP, task1_masks), \
        "complete digraph missing one loop should NOT be in Task 1"
    assert not _in_task1([(0, 1), (1, 2), (2, 3), (0, 0)], task1_masks), \
        "directed path plus a loop at the start should NOT be in Task 1"
