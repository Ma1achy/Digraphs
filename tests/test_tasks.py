"""Task 1 / Task 2 counts, subset relation, and the golden snapshots."""

import json
from pathlib import Path

from digraph_enum.graphs import canonical_form, edges_to_mask, mask_to_edges
from digraph_enum.tasks import task1, task2

GOLDEN = Path(__file__).resolve().parent / "golden"


# --- Counts ----------------------------------------------------------------


def test_task1_count(task1_masks):
    assert len(task1_masks) == 62


def test_task2_default_count(data_path, l_set, task1_masks):
    t2 = task2(data_path, strict_both=False, l_set=l_set, task1_masks=task1_masks)
    assert len(t2) == 8


def test_task2_strict_count(data_path, l_set, task1_masks):
    t2 = task2(data_path, strict_both=True, l_set=l_set, task1_masks=task1_masks)
    assert len(t2) == 3


def test_task2_subset_of_task1(data_path, l_set, task1_masks):
    t1 = set(task1_masks)
    default = task2(data_path, strict_both=False, l_set=l_set, task1_masks=task1_masks)
    strict = task2(data_path, strict_both=True, l_set=l_set, task1_masks=task1_masks)
    assert set(default).issubset(t1)
    assert set(strict).issubset(t1)
    # strict is itself a subset of default.
    assert set(strict).issubset(set(default))


# --- Must include / must exclude (count-level; the named per-graph version
#     lives in test_irene.py) --------------------------------------------------


def test_task1_representatives_are_canonical(task1_masks):
    for mask in task1_masks:
        assert canonical_form(mask) == mask


# --- Golden snapshots ------------------------------------------------------


def _load_golden(name):
    with open(GOLDEN / name) as fh:
        return [[tuple(e) for e in edges] for edges in json.load(fh)]


def test_task1_matches_golden(task1_masks):
    golden = _load_golden("task1.json")
    produced = [mask_to_edges(m) for m in task1_masks]
    assert produced == golden


def test_task2_matches_golden(data_path, l_set, task1_masks):
    golden = _load_golden("task2.json")
    t2 = task2(data_path, strict_both=False, l_set=l_set, task1_masks=task1_masks)
    produced = [mask_to_edges(m) for m in t2]
    assert produced == golden


def test_golden_is_internally_consistent():
    # The golden files must themselves canonicalise to a subset relation,
    # guarding against a stale/hand-edited snapshot.
    g1 = {canonical_form(edges_to_mask(e)) for e in _load_golden("task1.json")}
    g2 = {canonical_form(edges_to_mask(e)) for e in _load_golden("task2.json")}
    assert g2.issubset(g1)
    assert len(g1) == 62
    assert len(g2) == 8
