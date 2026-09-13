#!/usr/bin/env python3
"""Write and compile a paper for every proved hit that has not got one yet.

The sweep runs continuously now, so results arrive between batches and the papers have to be
built for whatever is there, by whichever builder the engine has. Engines with a builder of
their own get it; the rest get the general one. The date printed is today's, because the date
on a paper is the day the result was obtained.

    PAPER_DATE='7 September 2026' python3 src/build_new.py
"""
import withdrawnset
import importlib
import re
import json
import os
import subprocess
import sys


# An entry whose name reads "4 X (n+1)" has four rows and a growing number of columns, and the
# engines walk along the growing side --- they transpose, correctly, when the growing side is
# second. The special builders then describe the step as appending an "array row", which for
# those entries is the fixed side: 125 papers said a step appends a row of an array whose rows
# cannot grow. The mathematics is right and the sentence is not, so one sentence is added
# saying which way the array is being read. It goes here rather than in fourteen builders,
# because a fifteenth would forget it. `unibuild` already says "lines" and needs nothing.
# "4 X (n+1)" and "(3+1) X (n+1)" both fix the first dimension; the second spelling puts a
# bracket where the first puts a digit, and matching only the digit missed it.
GROWS_SECOND = re.compile(r'(?:(?<![\dn])\d+|\(\s*\d+\s*\+\s*\d+\s*\))'
                          r'\s*[xX]\s*\(?\s*n\b')
ROWWORD = re.compile(r'array rows|consecutive rows|appends? (?:one )?\w{0,6} ?row')
NOTE = (r" Throughout, \emph{row} means a line of the array in the direction the walk grows: "
        r"this entry fixes the first dimension and grows the second, so the array is read "
        r"transposed, and a step appends what the entry's own name writes as a column.")



# Many entries fix the value of one corner cell -- "with upper left element zero" and the like.
# It is part of the condition and it changes the count: for A231140 at n = 1, 1,710 of the
# 2 x 4 arrays satisfy the majority condition and 570 of those have the corner zero, and 570 is
# what the entry publishes. The models enforce it correctly. But 502 papers quote the clause in
# the entry's name and then never mention it again, so a reader cannot tell whether the paper
# noticed it. One sentence, added where every builder passes.
CORNER = re.compile(r'(?i)(upper|top) left (?:element |entry |value )?(zero|0|1)\b')


def _note_corner(tex, name):
    m = CORNER.search(' '.join(name.split()))
    if not m:
        return tex
    # "already explained" has to be judged on the whole document with the QUOTED NAME removed,
    # exactly as the scan that found these did. Looking only after the last quote block called
    # twenty papers unexplained that explain it earlier, and would have given them the sentence
    # twice.
    body = re.sub(r'\\begin\{quote\}.*?\\end\{quote\}', ' ', tex, flags=re.S)
    body = re.sub(r"OEIS A\d+ is\s+``.{0,400}?\.''", ' ', body, flags=re.S)
    if re.search(r'(?i)upper left|top left|corner|start vector|initial cell|first cell', body):
        return tex
    val = '0' if m.group(2).lower() in ('zero', '0') else m.group(2)
    note = (" The entry also fixes one corner: its %s left cell must be $%s$. That is part of "
            "the condition and it changes the count, so the model enforces it in the starting "
            "vector, which admits only the states whose first line carries that value in that "
            "position; every walk counted below begins from one of those."
            % (m.group(1).lower(), val))
    mm = re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}', tex, re.S)
    if not mm:
        return tex
    cut = mm.end() - len('\\end{abstract}')
    return tex[:cut] + note + tex[cut:]


def _note_transpose(tex, name):
    """say which way the array is read, when the entry grows along its second dimension"""
    nm = re.sub(r'\s*[xX]\s*', ' X ', ' '.join(name.split()))
    if not GROWS_SECOND.search(nm) or not ROWWORD.search(tex):
        return tex
    if 'read transposed' in tex:
        return tex
    m = re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}', tex, re.S)
    if not m:
        return tex
    cut = m.end() - len(r'\end{abstract}')
    return tex[:cut] + NOTE + tex[cut:]


import localentry as LE

# transfer17's builder prints the entry's own condition, which the sweep record does not
# carry: the parse is redone here and folded into the record so the paper can quote it
# rather than describe it in general terms.
MERGED = {'transfer9'}

ENRICH = {'transfer17', 'transfer6', 'transfer20', 'transfer21',
          'transfer9', 'transfer14', 'transfer10', 'transfer22', 'transfer19'}

SPECIAL = {'transfer17': 'transfer17build', 'transfer6': 'transfer6build',
           'transfer19': 'transfer19build',
           'transfer10': 'transfer10build', 'transfer11': 'transfer11build',
           'transfer22': 'transfer22build', 'transfer32': 'transfer32build',
           'transfer55': 'transfer55build', 'transfer60': 'transfer60build',
           'transfer14': 'transfer14build',
           'transfer23': 'transfer23build', 'transfer26': 'transfer26build',
           'transfer31': 'transfer31build', 'transfer32': 'transfer32build',
           'transfer33': 'transfer33build', 'transfer45': 'transfer45build', 'transfer53': 'transfer53build',
           'transfer20': 'transfer20build', 'transfer21': 'transfer21build',
           'transfer38': 'transfer38build', 'transfer56': 'transfer56build',
           'transfer62': 'transfer62build',
           'transfer34': 'transfer34build', 'transfer35': 'transfer35build',
           'transfer36': 'transfer36build', 'transfer37': 'transfer37build',
           'transfer81': 't81build', 'transfer82': 't82build', 'transfer83': 't83build',
           'transfer84': 't84build', 'transfer85': 't85build', 'transfer86': 't86build',
           'transfer87': 't87build', 'transfer89': 't89build', 'transfer91': 't91build',
           'transfer92': 't92build', 'transfer93': 't93build', 'denumerant': 'denbuild',
           # the engines whose model is NOT a walk: unibuild's digraph paper is false for
           # them, and qpbuild writes the model each one actually has
           'latpoly': 'qpbuild', 'ordpoly': 'qpbuild', 'necklace': 'qpbuild',
           'multiset': 'qpbuild', 'cuspdim': 'qpbuild', 'ca2d': 'qpbuild',
           'ecarow': 'qpbuild', 'ecacount': 'qpbuild', 'ecablock': 'qpbuild', 'ecarowb': 'qpbuild', 'ordrep': 'qpbuild'}

# rank-map.json is only regenerated by rank.py, so between an install and the next ranking
# it is stale -- and building from a stale roster silently overwrote a hundred papers that
# had just been installed by a different builder. paper-engines.json is the authority and is
# current the moment integrate_rest.py returns.
# A withdrawn result must not be rebuilt: nothing stopped that, and 179 papers withdrawn
# on 13 September were rebuilt within the hour by an unfiltered run of this script.
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
import integrate_rest_names as _labels
# A withdrawn ARGUMENT must not be rebuilt; a different argument on the same entry may be.
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('anum') not in roster and h.get('engine')
        and not withdrawnset.blocked(h['anum'], _labels.name(h['engine']))]
only = set(sys.argv[1:])
if only:
    hits = [h for h in hits if h['engine'] in only]
mods = {}
made, failed = 0, []
for h in sorted(hits, key=lambda x: x['anum']):
    name = SPECIAL.get(h['engine'], 'unibuild')
    mods.setdefault(name, importlib.import_module(name))
    mods.setdefault('unibuild', importlib.import_module('unibuild'))
    if h['engine'] in ENRICH:
        eng = importlib.import_module(h['engine'])
        q = eng.parse_name(LE.get(h['anum'])['name'])
        h = dict(q, **h)
        # transfer6build predates the unified sweep and names the threshold differently
        h.setdefault('threshold', h['nthr'])
    if h['engine'] in MERGED:
        h = dict(h, merged=True)
    dd = f"build/un{h['anum']}"
    os.makedirs(dd, exist_ok=True)
    try:
        tex = mods[name].build(h)
    except Exception as exc:
        # a builder written for an older record shape should not cost the paper: the general
        # builder always works from the fields the sweep does write
        print(f"  {h['anum']}: {name} failed ({exc}); using the general builder")
        tex = mods['unibuild'].build(h)
    nm_ = LE.get(h['anum'])['name']
    tex = _note_transpose(tex, nm_)
    tex = _note_corner(tex, nm_)
    open(f"{dd}/p.tex", 'w').write(tex)
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = f"{dd}/p.pdf"
    if os.path.exists(pdf) and os.path.getsize(pdf) > 50000:
        log = open(f"{dd}/p.log", errors='ignore').read()
        if 'LaTeX Warning: There were undefined references' in log:
            failed.append((h['anum'], 'undefined references'))
        else:
            made += 1
    else:
        failed.append((h['anum'], 'no pdf'))
print(f'{made} papers built, {len(failed)} problems')
for a, why in failed:
    print('  ', a, why)
