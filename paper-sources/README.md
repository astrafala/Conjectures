# paper-sources

The LaTeX source of every paper, named and banded exactly as in [`../papers`](../papers) — so
`papers/0001-0500/0001-PROOF.pdf` was compiled from `paper-sources/0001-0500/0001-PROOF.tex`.

The papers are generated: an engine settles a conjecture, and a builder in
[`../engine/src`](../engine/src) turns the settled result into a document. Keeping the sources
means a reader can see exactly what was written and how, rather than taking the PDF on trust.

`MISSING.txt` lists the papers whose source is not here — their build directories were removed
before sources were archived. The papers themselves are in `../papers` and each is
self-contained.
