#!/usr/bin/env python3
"""Where a paper lives inside papers/, and why it lives there.

The GitHub web UI lists at most 1000 entries in a directory, so a flat folder of 8887 papers
is half invisible in a browser -- which defeats the point of having the papers in the repo at
all. They are therefore filed in bands of BAND ranks each. The rank still IS the hardness
order, 1 hardest; the bands only break it into pages.

Rank numbers are zero padded to a fixed width so that a plain lexicographic listing -- which
is what a file browser gives you -- is the hardness order. Without padding `10` sorts before
`2` and the ordering the whole roster is built around is invisible on screen.
"""
import repopaths

BAND = 500
WIDTH = 4


def band(rank):
    lo = (rank - 1) // BAND * BAND + 1
    return f"{lo:0{WIDTH}d}-{lo + BAND - 1:0{WIDTH}d}"


def name(rank, verdict):
    return f"{rank:0{WIDTH}d}-{verdict}.pdf"


def path(rank, verdict, root=None):
    if root is None:
        root = repopaths.PAPERS
    return f"{root}/{band(rank)}/{name(rank, verdict)}"
