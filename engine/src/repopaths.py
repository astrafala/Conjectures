#!/usr/bin/env python3
"""Where the published parts of the repository live, relative to engine/.

The code sits in engine/src/ and its working data in engine/, which is the
working directory every script is run from; the things a reader is meant to see --- the
papers, their sources and the documents --- sit at the repository root. Scripts run with
engine/ as the working directory, so anything outside it goes through here rather than being
spelled out in twenty places.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PAPERS = os.path.join(ROOT, 'papers')
SOURCES = os.path.join(ROOT, 'paper-sources')


def doc(name):
    """a document at the repository root, by name"""
    return os.path.join(ROOT, name)


# The deep check's working data. It lives under engine/ because all code and working data
# does; the plan and the running report are a document and live at the repository root.
DEEPCHECK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'deep-check')
