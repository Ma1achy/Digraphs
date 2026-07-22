"""Canonical form and enumeration."""

from itertools import permutations

from digraph_enum.graphs import (
    canonical_form,
    edges_to_mask,
    enumerate_classes,
    mask_to_edges,
    permute_mask,
)

# A fixed set of relabellings to exercise invariance without any randomness.
_SAMPLE_PERMS = [
    (0, 1, 2, 3),
    (1, 0, 2, 3),
    (3, 2, 1, 0),
    (1, 2, 3, 0),
    (2, 3, 0, 1),
    (0, 2, 1, 3),
]


def _relabel_edges(edges, perm):
    return [(perm[u], perm[v]) for u, v in edges]


def test_relabelling_preserves_canonical_form():
    # The directed 4-cycle, relabelled every which way, keeps one canonical form.
    base = edges_to_mask([(0, 1), (1, 2), (2, 3), (3, 0)])
    target = canonical_form(base)
    for perm in permutations(range(4)):
        relabelled = edges_to_mask(_relabel_edges(mask_to_edges(base), perm))
        assert canonical_form(relabelled) == target


def test_permute_mask_matches_edge_relabelling():
    edges = [(0, 1), (0, 2), (3, 2), (1, 1)]
    mask = edges_to_mask(edges)
    for i, perm in enumerate(permutations(range(4))):
        expected = edges_to_mask(_relabel_edges(edges, perm))
        assert permute_mask(mask, i) == expected


def test_non_isomorphic_graphs_differ():
    pairs = [
        # one loop vs one non-loop edge
        ([(0, 0)], [(0, 1)]),
        # directed 3-path+isolated vs directed 4-cycle
        ([(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 2), (2, 3), (3, 0)]),
        # two antiparallel edges vs two parallel-ish edges
        ([(0, 1), (1, 0)], [(0, 1), (2, 3)]),
        # all loops vs no loops complete
        ([(0, 0), (1, 1), (2, 2), (3, 3)], [(0, 1), (1, 2), (2, 3), (3, 0)]),
    ]
    for a, b in pairs:
        assert canonical_form(edges_to_mask(a)) != canonical_form(edges_to_mask(b))


def test_isomorphic_hand_pair_agree():
    # Same graph, different labels -> equal canonical form.
    a = edges_to_mask([(0, 1), (1, 2), (2, 0)])  # 3-cycle on {0,1,2}
    b = edges_to_mask([(1, 2), (2, 3), (3, 1)])  # 3-cycle on {1,2,3}
    assert canonical_form(a) == canonical_form(b)


def test_enumeration_has_3044_classes(classes):
    assert len(classes) == 3044


def test_canonical_forms_are_their_own_canon(classes):
    # Every representative is already canonical and the list is unique + sorted.
    assert classes == sorted(set(classes))
    for mask in classes:
        assert canonical_form(mask) == mask
