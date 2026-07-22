#!/usr/bin/env python3
"""Single entry point for the digraph enumeration tool.

Running ``python main.py`` runs both tasks and prints the counts and edge lists.
See ``python main.py --help`` for the flags. All real logic lives in the
``digraph_enum`` package; this file only wires the CLI to it.
"""

import os
import sys

# Make the package importable when running straight from a checkout
# (no ``pip install`` required for the plain-python route).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from digraph_enum.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
