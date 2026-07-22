"""Induced-subgraph helper, L loading, and H / property (i)."""

from itertools import combinations

import networkx as nx

from digraph_enum.constraints import (
    _canonical3,
    all_subgraphs_in_L,
    induced3,
    load_L,
    load_L_digraphs,
    property_i,
)
from digraph_enum.graphs import edges_to_mask


# --- Data loading ----------------------------------------------------------


def test_L_loads_21_digraphs_on_three_nodes(data_path):
    graphs = load_L_digraphs(data_path)
    assert len(graphs) == 21
    for g in graphs:
        assert isinstance(g, nx.DiGraph)
        assert set(g.nodes()) == {0, 1, 2}


def test_L_has_21_distinct_classes(l_set):
    assert len(l_set) == 21


# --- Induced 3-vertex subgraph --------------------------------------------


def test_induced_subgraph_of_4cycle_is_directed_3path():
    # Deleting any vertex from the directed 4-cycle leaves a directed 3-path.
    cycle = edges_to_mask([(0, 1), (1, 2), (2, 3), (3, 0)])
    # 3-path 0->1->2 as a 3-vertex (9-bit) mask.
    path3 = (1 << (3 * 0 + 1)) | (1 << (3 * 1 + 2))
    for subset in combinations(range(4), 3):
        assert _canonical3(induced3(cycle, subset)) == _canonical3(path3)


def test_induced_subgraph_of_all_loops_K4_is_all_loops_K3():
    # All 16 edges; deleting a vertex leaves the all-loops complete 3-graph.
    full = edges_to_mask([(u, v) for u in range(4) for v in range(4)])
    full3 = (1 << 9) - 1  # every one of the 9 possible 3-vertex edges
    for subset in combinations(range(4), 3):
        assert induced3(full, subset) == full3


def test_all_subgraphs_in_L_examples(l_set):
    # 4-cycle: all four induced subgraphs are directed 3-paths, which are in L.
    cycle = edges_to_mask([(0, 1), (1, 2), (2, 3), (3, 0)])
    assert all_subgraphs_in_L(cycle, l_set)
    # 4-cycle + a loop: the loop creates a 3-subgraph not in L.
    cycle_loop = edges_to_mask([(0, 1), (1, 2), (2, 3), (3, 0), (0, 0)])
    assert not all_subgraphs_in_L(cycle_loop, l_set)


# --- H / property (i) ------------------------------------------------------


def test_property_i_all_embeddings_arrow_present_fails_default():
    # H's edges plus the interrogated arrow (3,0), and enough symmetry that no
    # embedding can avoid a present arrow: the complete loopless digraph on 4
    # vertices has every (u,v) with u!=v, so every embedding's arrow is present.
    complete = edges_to_mask([(u, v) for u in range(4) for v in range(4) if u != v])
    assert property_i(complete, strict_both=False) is False
    assert property_i(complete, strict_both=True) is False


def test_property_i_arrow_absent_passes_default_only():
    # Exactly H's three edges and nothing else: the canonical embedding has the
    # arrow (3,0) absent, and there is no embedding with it present.
    only_h = edges_to_mask([(0, 1), (0, 2), (3, 2)])
    assert property_i(only_h, strict_both=False) is True
    assert property_i(only_h, strict_both=True) is False


def test_property_i_both_present_and_absent_passes_strict():
    # A graph rich enough that among its H-embeddings some have the interrogated
    # arrow absent and others have it present -> both flags set, strict passes.
    # (Minimal such witness, found by exhaustive search.)
    both = edges_to_mask([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)])
    assert property_i(both, strict_both=False) is True
    assert property_i(both, strict_both=True) is True


def test_property_i_no_embedding_is_false():
    # The empty graph embeds H nowhere.
    empty = 0
    assert property_i(empty, strict_both=False) is False
    assert property_i(empty, strict_both=True) is False
