#!/usr/bin/env python3
"""The roster label each engine is installed under.

Split out of `integrate_rest` so a builder can ask what label a result WOULD carry
without importing the installer and running it.
"""
ENGNAME = {'transfer81': 'canonical-subblock', 'transfer82': 'subblock-condition',
           'transfer83': 'neighbour-condition', 'transfer84': 'column-domination',
           'transfer85': 'distance-repeat', 'transfer86': 'local-array-condition',
           'transfer87': 'parity-difference', 'transfer89': 'white-squares',
           'transfer91': 'neighbour-reach', 'transfer92': 'straight-line',
           'transfer93': 'subblock-multiset', 'denumerant': 'lattice-count',
           'transfer17': 'subblock-3x3', 'transfer38': 'edge-count-pattern',
           'transfer56': 'forbidden-run', 'transfer62': 'distance-inequality',
           'transfer23': 'subblock-matrix', 'transfer26': 'image-count',
           'transfer28': 'image-count', 'transfer30': 'subblock-coloring',
           'transfer31': 'monotone-subblock', 'transfer32': 'monotone-subblock',
           'transfer33': 'subblock-difference', 'transfer41': 'cell-condition',
           'transfer42': 'cell-condition-pattern', 'transfer45': 'consecutive-triple',
           'transfer53': 'modular-neighbour', 'transfer32': 'monotone-subblock',
           'transfer55': 'repeated-value', 'transfer60': 'capped-pair-count',
           # the engines whose model is not a walk: without these the default
           # 'transfer-matrix' label would be as false as unibuild's digraph was
           'latpoly': 'lattice-quasipolynomial', 'ordpoly': 'fixed-length-polynomial',
           'necklace': 'necklace-burnside', 'multiset': 'multiset-profile',
           'cuspdim': 'cusp-form-dimension', 'ca2d': 'automaton-axis',
           'ecarow': 'automaton-row', 'ecacount': 'automaton-cell-count', 'ecablock': 'automaton-block-count', 'ecarowb': 'automaton-block-row', 'ordrep': 'repeated-value-polynomial', 'permdisp': 'bounded-displacement',
           'window': 'window-condition', 'repval': 'repeated-value-chain'}


def name(engine):
    return ENGNAME.get(engine, 'transfer-matrix')
