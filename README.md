# digraph-enum — 4-vertex digraph enumeration

## What this tool does

This is a small command-line tool that lists **directed graphs on 4 vertices**
(arrows between points, self-loops allowed), counted **up to relabelling** — two
graphs that are the same picture with the points renamed count once. It keeps
only the graphs that satisfy some local rules and reports how many there are.

The maths, in one paragraph: take every possible directed graph on 4 points
(there are 65,536 of them). Group them so that graphs which are the same after
renaming the points are treated as one — that leaves exactly **3,044** distinct
shapes. **Task 1** keeps a shape only if *every* way of deleting one of its four
points leaves a 3-point pattern drawn from an allowed list **L** (21 patterns,
supplied in a data file); there are **62** such shapes. **Task 2** keeps the
Task 1 shapes that additionally satisfy a condition ("property (i)") about a
fixed little pattern *H* and one particular arrow — **8** shapes by default, or
**3** in a stricter variant. The tool can also draw all the surviving graphs.

You do **not** need to understand the maths to run it. Just follow the steps.

---

## What you need (pick ONE route)

There are two ways to run this. Route A (Docker / devcontainer) needs no Python
knowledge and installs everything for you. Route B is a normal Python setup.

### Route A — VS Code + Dev Containers (recommended, zero Python setup)

You install two things, and the container brings its own Python and libraries.

1. **Docker Desktop** — the engine that runs the container.
   Download: <https://www.docker.com/products/docker-desktop/> . Install it,
   launch it, and leave it running (you'll see a whale icon in your menu bar /
   system tray).
2. **Visual Studio Code** — the editor. Download: <https://code.visualstudio.com/> .
3. The **Dev Containers** extension for VS Code.
   Get it here: <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>
   (or, in VS Code, click the Extensions icon in the left bar, search
   "Dev Containers", and click Install).

### Route B — plain Python + pip (no Docker)

1. **Python 3.11 or newer.** Download: <https://www.python.org/downloads/> .
   During install on Windows, tick **"Add Python to PATH"**.
   Check it worked by opening a terminal and running:
   ```
   python --version
   ```
   (On some systems the command is `python3` instead of `python`.)

---

## Get the code

Open a terminal (Terminal on macOS/Linux, or PowerShell on Windows) and run:

```
git clone <the-repository-url> digraph-enum
cd digraph-enum
```

If you don't have `git`, install it from <https://git-scm.com/downloads> , or
download the project as a ZIP and unzip it, then `cd` into the folder.

---

## Set it up and run it

### Route A (devcontainer)

1. Open the folder in VS Code: `code .` (or **File → Open Folder…**).
2. VS Code will show a popup **"Reopen in Container"** — click it. (If you miss
   it: press `F1`, type **"Dev Containers: Reopen in Container"**, press Enter.)
3. Wait a minute or two the first time while it builds. When it's done you have a
   terminal inside the container with everything installed.
4. In that terminal, run the tool:
   ```
   python main.py
   ```

### Route B (virtualenv + pip)

From inside the project folder:

```
python -m venv .venv
```

Activate the virtual environment:

- macOS / Linux: `source .venv/bin/activate`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`

Then install the dependencies and run:

```
pip install -r requirements.txt
python main.py
```

(Use `python3` instead of `python` if that's what your system uses.)

---

## How to run it — exact commands

Run both tasks and print the counts and edge lists:

```
python main.py
```

**What to expect.** The output starts with the Task 1 count and its 62 graphs,
then the Task 2 count and its 8 graphs:

```
Task 1  (all induced 3-vertex subgraphs in L): 62 graphs
    1. (no edges)
    2. (0,0)
    ...
Task 2  (Task 1 + property (i), default mode): 8 graphs
    ...
```

Each numbered line is one graph, shown as its list of arrows `(from,to)`;
`(0,0)` is a self-loop on vertex 0.

**Draw the graphs** to PNG images (`task1.png` and `task2.png` in the current
folder):

```
python main.py --draw
```

Self-loops are drawn as small red arcs outside each vertex; a pair of opposite
arrows between two vertices is drawn as two curved arcs so they never merge into
one line.

**Strict mode** for property (i) (this changes Task 2 from 8 graphs to 3):

```
python main.py --strict-both
```

**Use a different data file** (the list L). By default the tool reads
`data/my_graphs.pkl`; point it elsewhere with:

```
python main.py --data path/to/my_graphs.pkl
```

**See all the options:**

```
python main.py --help
```

---

## Running the tests

The project comes with an automated test suite that checks every expected count
and Irene's six hand-verified reference graphs.

Route A: the test tool is already installed in the container. Route B: install
it once with `pip install pytest` (or `pip install -e ".[test]"`).

Then, from the project folder, run:

```
pytest
```

**What a passing run looks like** — a row of dots and a green summary line:

```
........................                                        [100%]
26 passed in 1.10s
```

If you see `26 passed` (or more), everything is working.

---

## Troubleshooting

- **`could not find the data pickle at 'data/my_graphs.pkl'`** — you're running
  from the wrong folder. Make sure you're inside the project directory (the one
  containing `main.py`), or pass the file's location explicitly with
  `--data /full/path/to/my_graphs.pkl`.
- **`python: command not found`** — try `python3` instead of `python`
  everywhere.
- **`ModuleNotFoundError: No module named 'networkx'` (or numpy/matplotlib)** —
  the dependencies aren't installed. On Route B, activate the virtual
  environment and run `pip install -r requirements.txt` again. On Route A, make
  sure you actually reopened the folder *in the container*.
- **`--draw` seems to hang or errors about a display** — it shouldn't; the tool
  renders without a screen. If it does, make sure you installed the pinned
  `matplotlib` from `requirements.txt`.
- **The counts don't match (not 3044 / 62 / 8 / 3)** — you may be pointing at a
  different data file with `--data`. The numbers above assume the bundled
  `data/my_graphs.pkl`.
