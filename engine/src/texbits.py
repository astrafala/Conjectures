#!/usr/bin/env python3
"""Small pieces of LaTeX that several paper builders need, written once.

`offsets_tex` exists because the same fault was made three times: a list of neighbour offsets
written as `$(0,1)$, $(1,0)$` and then dropped INSIDE a `\\[...\\]` display, where the inner
dollars close and reopen math mode and the page comes out wrong. The list is display content,
so it carries no dollars of its own; a builder that wants it inline wraps the whole thing in
one pair instead.
"""


def offsets_tex(offsets):
    """the offsets as display-math content: no `$' anywhere inside"""
    return ', '.join('(%d,%d)' % tuple(t) for t in offsets)


def inline(s):
    """wrap display content for use in a sentence"""
    return '$' + s + '$'
