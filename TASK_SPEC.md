# Task spec: enumerate 4-vertex digraphs under local subgraph constraints

## Overview

Build a small, fast, well-tested Python tool that enumerates **directed graphs on 4
vertices (self-loops allowed), up to isomorphism**, subject to constraints defined by
their small induced subgraphs, then draws and counts the results. There are two related
enumeration tasks. Ship it as a clean package with a `pytest` suite and a CLI, ready to
commit to git.

The reference behaviour below is already known and verified — the acceptance criteria
give exact expected counts, so the test suite can assert against ground truth.

## Background (context for the implementer)

This is the computational-verification step of a graph-theory argument: characterise a
hereditary class of digraphs by which small patterns are allowed, then check what the
4-vertex members look like and how many there are. 4 vertices is the smallest size where
global obstructions can appear that the 3-vertex rules don't obviously force. You do not
need to understand the maths beyond the precise definitions in this spec.

## Input data

`data/my_graphs.pkl` — a pickled `list` of **21** `networkx.DiGraph` objects, each on
nodes `{0, 1, 2}`. This is the list **L**: the allowed 3-vertex patterns. Commit this
file to the repo. (It is provided alongside this spec.)

- Load with `pickle`. Treat each element as an unlabelled digraph (i.e. only its
  isomorphism class matters).
- Do **not** hardcode L's contents in source; always read it from the pickle so the tool
  stays correct if the list is regenerated.

## Definitions and representation

- **Digraph on n vertices, loops allowed.** Vertices `0..n-1`. Any ordered pair `(u, v)`
  including `u == v` (a self-loop) may or may not be an edge. On 4 vertices there are
  `4*4 = 16` possible edges, so `2^16 = 65536` labelled digraphs.
- **Up to isomorphism.** Two digraphs are the same if a vertex relabelling maps one onto
  the other (edges and loops preserved). All outputs and counts are per isomorphism class.
- **Induced subgraph on a vertex subset S.** Keep the vertices in S and exactly the edges
  (including loops) whose endpoints both lie in S.
- **Subgraph containment (for Task 2 / H).** `G` contains `H` if there is an injective
  vertex map `phi: V(H) -> V(G)` with every edge of `H` mapped to an edge of `G`. `G` may
  have additional edges among the image vertices; those extra edges are simply not part of
  the mapped copy. Since `|V(H)| = |V(G)| = 4` here, `phi` is a bijection (a relabelling).

**Recommended representation (for speed):** encode a digraph as a 16-bit integer `mask`
where bit `4*u + v` is set iff edge `u -> v` is present (loops are the diagonal bits
`0, 5, 10, 15`). This makes enumeration, canonical forms, and subgraph checks fast and
integer-only. The implementer may choose otherwise, but must meet the performance bar.

## Requirements

### R1 — Enumeration up to isomorphism
Enumerate all digraphs on 4 vertices with loops, deduplicated to one representative per
isomorphism class. There must be exactly **3044** classes. Recommended approach: compute a
**canonical form** for each of the 65536 labelled digraphs (minimum over the 24 vertex
relabellings of its bitmask) and group by it. This canonical pass doubles as a correctness
check (`unique canonical forms == 3044`).

### R2 — Task 1
Return every 4-vertex digraph `G` (up to isomorphism) such that **all four of its induced
3-vertex subgraphs are isomorphic to some graph in L**. (The four subgraphs are obtained by
deleting each vertex in turn.)

### R3 — Task 2
Return every 4-vertex digraph `G` (up to isomorphism) satisfying **both**:

- **Property (ii)** — the Task 1 condition (all induced 3-vertex subgraphs are in L).
  "Three-vertex subgraphs" here means **induced**.
- **Property (i)** — a constraint about a fixed pattern
  `H = ({1,2,3,4}, {(1,2), (1,3), (4,3)})` (0-indexed: vertices `1,2,3,4 -> 0,1,2,3`, so
  H's edges are `(0,1), (0,2), (3,2)`). Among all bijections `phi: V(H) -> V(G)` that embed
  `H` into `G` (all three of H's edges present in `G`), the tool checks the arrow
  **`4 -> 1`**, i.e. `phi(4) -> phi(1)` (0-indexed `phi(3) -> phi(0)`), which is *not* an
  edge of H:
  - **Default mode:** at least one embedding has `4 -> 1` **absent** in `G`.
  - **Strict mode (config flag `strict_both`):** at least one embedding has `4 -> 1`
    **absent** *and* at least one (possibly different) embedding has it **present**.

  Provide `strict_both` as a parameter / CLI flag, defaulting to `False` (the default mode).

Task 2 must be a subset of Task 1 (it's Task 1 with property (i) added). Implement it that
way (filter the Task 1 result) or ensure the equivalent.

### R4 — Output
For each task, the tool must:
- report the **count**;
- expose the result as data (e.g. a list of canonical edge-lists) usable by tests;
- **draw** the digraphs — a grid of subplots, one per graph, saved as a PNG
  (`task1.png`, `task2.png`). Self-loops must be visibly rendered, and antiparallel edge
  pairs (`u -> v` and `v -> u` both present) must be drawn so they don't overlap into a
  single line (e.g. curved arcs). Label each subplot with its edge list.

### R5 — Performance
The full run (both tasks, excluding the optional drawing step) must complete in **under a
few seconds** on a normal laptop. The recommended canonical-form + integer-bitmask approach
runs effectively instantly (a vectorised NumPy canonical pass over all 65536 masks is
ideal). No external isomorphism solver is required.

### R6 — CLI
A single entry point, e.g. `python -m digraph_enum` or a console script, that runs both
tasks, prints the counts and edge lists, and (optionally, behind a `--draw` flag) writes
the PNGs. Accept `--strict-both` and `--data path/to/my_graphs.pkl`.

## Acceptance criteria (exact, verified)

These are ground truth from a verified reference implementation. The `pytest` suite must
assert them.

| Quantity | Expected |
|---|---|
| Isomorphism classes of 4-vertex digraphs (loops allowed) | **3044** |
| Distinct isomorphism classes represented in L | **21** |
| **Task 1** count | **62** |
| **Task 2** count, default mode | **8** |
| **Task 2** count, `strict_both=True` | **3** |
| Task 2 ⊆ Task 1 | true |

**Task 1 must include** (by isomorphism):
1. the directed 4-cycle `0->1->2->3->0`;
2. the complete digraph with all loops (every one of the 16 edges);
3. the directed path `0->1->2->3`.

**Task 1 must exclude** (by isomorphism):
1. the directed 4-cycle plus one loop (`4-cycle` + `(0,0)`);
2. the complete digraph with every loop except one vertex (all 16 edges minus one diagonal);
3. the directed path plus a loop at the start (`0->1->2->3` + `(0,0)`).

## Testing requirements (pytest)

Write a `tests/` suite covering at least:

- **Canonical form / isomorphism helper**
  - relabelling a graph yields an equal canonical form (test several random relabellings);
  - two non-isomorphic graphs yield different canonical forms (a few hand-picked pairs);
  - the enumeration produces exactly **3044** classes.
- **Induced subgraph helper** — hand-checked cases (e.g. deleting a vertex from the
  directed 4-cycle gives the directed 3-path; from the all-loops complete graph gives the
  all-loops complete 3-graph).
- **H / property (i) helper** — direct unit tests on small graphs: a graph where every
  H-embedding has `4->1` present (fails default), one where some embedding has it absent
  (passes default), and one exhibiting both (passes strict).
- **Task 1** — count is 62; the three "must include" graphs are present; the three "must
  exclude" graphs are absent.
- **Task 2** — count is 8 in default mode, 3 in strict mode; every Task 2 graph is also in
  Task 1.
- **Data loading** — L loads from the pickle and has 21 entries on nodes `{0,1,2}`.
- **Determinism / golden snapshot (recommended)** — generate the canonical edge-lists for
  Task 1 and Task 2 once, commit them as fixture files (e.g. `tests/golden/task1.json`),
  and assert the tool reproduces them exactly. This locks in the full result, not just the
  counts.

All tests must pass in CI with a single `pytest` invocation.

## Suggested repository layout

```
digraph-enum/
  README.md
  pyproject.toml            # deps: networkx, numpy, matplotlib, pytest
  data/
    my_graphs.pkl           # the list L (committed)
  src/digraph_enum/
    __init__.py
    graphs.py               # bitmask <-> graph, canonical form, enumeration
    constraints.py          # induced-subgraph check, L membership, H / property (i)
    tasks.py                # task1(), task2(strict_both=False)
    draw.py                 # grid drawing (loops + antiparallel handling)
    __main__.py             # CLI
  tests/
    test_canonical.py
    test_constraints.py
    test_tasks.py
    golden/                 # optional committed snapshots
```

(Package layout is a suggestion; the CLI, tests, and acceptance criteria are the contract.)

## Definition of done

- `pytest` passes, covering everything in "Testing requirements", including the exact
  counts 3044 / 62 / 8 / 3.
- CLI runs, prints counts + edge lists, and `--draw` produces `task1.png` / `task2.png`
  with correct self-loop and antiparallel-edge rendering.
- Full run (sans drawing) under a few seconds.
- `README.md` explains the maths in a paragraph, the representation, how to run, and how to
  run the tests.
- `data/my_graphs.pkl` committed; L never hardcoded in source.

## Implementation notes (non-binding hints)

- Canonical form: `min` over the 24 permutations of the 16-bit permuted mask. A vectorised
  NumPy pass over `arange(1<<16)` computing all 24 permuted arrays and taking the
  element-wise minimum is the fast route; the number of distinct results is the 3044 check.
- Both Task properties are isomorphism-invariant, so evaluate them once per class
  representative (~3044 checks), not per labelled graph.
- Property (i): iterate the 24 bijections; a bijection "embeds H" iff H's three edges are
  all present in `G`; then inspect the `4->1` arrow. Track `saw_absent` / `saw_present`
  booleans; default returns `saw_absent`, strict returns `saw_absent and saw_present`.
- Drawing: `networkx` with `matplotlib`; a fixed `circular_layout` for all four nodes
  (stable across subplots). Use `connectionstyle="arc3,rad=..."` so antiparallel arrows
  bow apart; confirm self-loops actually render (they do in current networkx, but verify).

## Appendix — reference constants

- **H** (0-indexed): nodes `{0,1,2,3}`, edges `{(0,1), (0,2), (3,2)}`; interrogated arrow
  `4->1` = `(3,0)`.
- **The six Task 1 test graphs** (edge lists, 0-indexed):
  - include: `[(0,1),(1,2),(2,3),(3,0)]`; all 16 edges; `[(0,1),(1,2),(2,3)]`
  - exclude: `[(0,1),(1,2),(2,3),(3,0),(0,0)]`; all 16 edges minus `(3,3)`;
    `[(0,1),(1,2),(2,3),(0,0)]`
- **L** (from the pickle): 21 digraphs on `{0,1,2}` including the empty graph, single edge,
  single loop, out-/in-stars, 2-cycle, directed 3-path, 3-cycle, and the all-loops complete
  3-graph, among others.
