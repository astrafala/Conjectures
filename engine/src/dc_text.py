#!/usr/bin/env python3
"""The text of a paper, in a form that can be searched.

The papers are set with T1 font encoding, whose ligature block occupies codepoints
0x1b-0x1f. Text extracted from the PDF therefore spells "Verification" as
"Veri\\x1ccation", and a search for the word finds nothing --- which is how a check for a
missing Verification section came to report 9091 papers that all have one. Every text
check in the deep check goes through here, so that failure cannot happen twice.
"""
import re

LIGATURES = {'\x1b': 'ff', '\x1c': 'fi', '\x1d': 'fl', '\x1e': 'ffi', '\x1f': 'ffl',
             'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi',
             'ﬄ': 'ffl', '’': "'", '‘': "'", '“': '"',
             '”': '"', '–': '-', '—': '--', '−': '-'}
TABLE = str.maketrans(LIGATURES)


def normalise(t):
    """extracted text with ligatures and typographic punctuation spelled out"""
    return t.translate(TABLE)


def flat(t):
    """normalised, with all runs of whitespace collapsed --- for phrase searching

    Words broken across a line come back with a space in them ("for mula"), so a phrase
    search must not assume single spaces between letters of a word.
    """
    return ' '.join(normalise(t).split())


def loose(phrase):
    """a pattern matching a phrase even where the typesetting broke a word in two"""
    return r'\s*'.join(re.escape(c) for c in phrase if not c.isspace())
