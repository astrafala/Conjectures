# Deep-check working data

The evidence the 10,000 deep check produces: the frozen roster every phase reads, the
snapshot of what was frozen, and the per-phase results.

* `frozen-roster.json` — the roster as it stood when the check began. Every phase reads this
  rather than the live roster, so the corpus cannot shift underneath the check.
* `phase0.json` — the commit, whether the tree was clean, the library versions, and a
  SHA-256 of every tracked file.
* `phase2-*.json`, `phase5-*.json` — per-phase results, one file per shard.
* `phase7-never-processed.txt` — entries an engine reads, carrying a testable conjecture,
  that have never been processed at all.

The plan and the running report are documents and live at the repository root, in
`DEEP-CHECK.md`.
