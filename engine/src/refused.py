#!/usr/bin/env python3
"""Engines whose results may not be installed, and why.

An engine is refused when its argument turns out not to be one. Turning the engine off stops
new results appearing, but it does nothing about results already written to a hits file, and a
sweep started before the change keeps the whole list in memory and writes its old contents back
over any purge. So the refusal is recorded here as well, and the builder and the installer both
read it: nothing from a refused engine reaches the roster whatever a hits file says.
"""
ENGINES = {
    'ca2dcount': ('the active-cell count of a two-dimensional automaton has no proved '
                  'generating function, so no bound on its degree exists and the residual '
                  'test cannot certify -- see the note at the top of ca2dcount.py'),
}


def ok(engine):
    return engine not in ENGINES
