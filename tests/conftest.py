"""Shared fixtures and path wiring for the test suite."""

import os
import sys
from pathlib import Path

import pytest

# Allow the package to be imported from src/ without an install.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

DATA_PATH = ROOT / "data" / "my_graphs.pkl"


@pytest.fixture(scope="session")
def data_path() -> str:
    return str(DATA_PATH)


@pytest.fixture(scope="session")
def l_set(data_path):
    from digraph_enum.constraints import load_L

    return load_L(data_path)


@pytest.fixture(scope="session")
def classes():
    from digraph_enum.graphs import enumerate_classes

    return enumerate_classes()


@pytest.fixture(scope="session")
def task1_masks(data_path, l_set):
    from digraph_enum.tasks import task1

    return task1(data_path, l_set=l_set)
