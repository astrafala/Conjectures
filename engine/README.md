# engine

Everything that produces the results. Run from **this directory**:

```
cd engine
python3 src/rank.py          # re-derive the hardness ordering and install it into ../papers
python3 src/makeindex.py     # regenerate the index files in ../papers
python3 src/sync_counts.py   # make every count in the repository agree
```

The code lives in `src/` and its working data — candidate lists, per-engine hit files, sweep
progress caches — lives here. Scripts are run as `python3 src/<name>.py` with `engine/` as the
working directory: that puts `src/` on the import path and leaves the data where the scripts
expect it. `src/repopaths.py` is the one place that knows where the repository root is.

## What is in src/

| Prefix | What it does |
| --- | --- |
| `transfer*.py` | The models. Each reads one family of OEIS entry names and builds the object that decides it. |
| `uniform.py` | Routes an entry name to the engine that reads it, and gives every engine one interface. |
| `sweep_*.py` | Runs an engine across the corpus: parse, build, check against the entry's data, decide the conjecture. |
| `*build*.py` | Turn a settled result into a LaTeX paper. |
| `bf*.py` | Independent brute forces, written from the entry's English rather than from the engine. |
| `audit_*.py` | Re-checks of results already counted. |
| `integrate_*.py` | Add settled results to the roster. |
| `rank.py`, `makeindex.py`, `paperpath.py` | The roster: ordering, layout, index. |
| `lumpauto.py` | Merges states with identical futures — what makes the larger models decidable. |

## What is not stored

The build tree (`engine/build/`), the `was`-keyed master (`engine/papers-old-numbering/`) and
the OEIS b-file cache (`engine/bcache/`) are working state, not results. Between them they were
about 2 GB and 39 000 files, including a duplicate PDF of every paper. Each is regenerable:
`src/restore_master.py` rebuilds the master exactly from `../papers` and `rank-map.json`, and
every paper's LaTeX source is kept in `../paper-sources/`.
