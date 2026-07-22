"""Drawing smoke tests: the grid renders to a non-trivial PNG file."""

from digraph_enum.draw import draw_grid
from digraph_enum.graphs import edges_to_mask


def test_draw_grid_writes_png(tmp_path):
    masks = [
        edges_to_mask([(0, 1), (1, 2), (2, 3), (3, 0)]),      # 4-cycle
        edges_to_mask([(0, 1), (1, 0), (2, 3), (3, 2)]),      # antiparallel pairs
        edges_to_mask([(0, 0), (1, 1), (2, 2), (3, 3)]),      # all self-loops
        edges_to_mask([(u, v) for u in range(4) for v in range(4)]),  # complete+loops
    ]
    out = tmp_path / "grid.png"
    result = draw_grid(masks, str(out), title="test grid")
    assert result == str(out)
    assert out.exists()
    # A real rendering is more than a few hundred bytes.
    assert out.stat().st_size > 1000


def test_draw_grid_handles_empty(tmp_path):
    out = tmp_path / "empty.png"
    draw_grid([], str(out))
    assert out.exists()
