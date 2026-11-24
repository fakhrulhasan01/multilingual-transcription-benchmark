"""List every word-level difference for one language and one system.

Usage: python scripts/word_diff.py bn_in results/transcriptgo-run1
Prints: file <TAB> reference words <TAB> transcript words  (one row per error run)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import ROOT, normalise, read_tsv

def align(r, h):
    n, m = len(r), len(h)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): d[i][0] = i
    for j in range(m + 1): d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i-1][j-1] + (r[i-1] != h[j-1]), d[i-1][j] + 1, d[i][j-1] + 1)
    i, j, ops = n, m, []
    while i or j:
        if i and j and d[i][j] == d[i-1][j-1] + (r[i-1] != h[j-1]):
            ops.append((r[i-1], h[j-1])); i -= 1; j -= 1
        elif i and d[i][j] == d[i-1][j] + 1:
            ops.append((r[i-1], "")); i -= 1
        else:
            ops.append(("", h[j-1])); j -= 1
    ops.reverse()
    runs, cur = [], None
    for a, b in ops:
        if a == b:
            if cur: runs.append(cur); cur = None
        else:
            cur = cur or ([], [])
            if a: cur[0].append(a)
            if b: cur[1].append(b)
    if cur: runs.append(cur)
    return runs

lang, system = sys.argv[1], sys.argv[2]
refs = {r["file"]: r["reference"] for r in read_tsv(os.path.join(ROOT, "data", lang, "clips.tsv"))}
hyps = {r["file"]: r["hypothesis"] for r in read_tsv(os.path.join(ROOT, system, f"{lang}.tsv"))}
for name, ref in refs.items():
    for a, b in align(normalise(ref, lang), normalise(hyps.get(name, ""), lang)):
        print(f"{name}\t{' '.join(a)}\t{' '.join(b)}")
