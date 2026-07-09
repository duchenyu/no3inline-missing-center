#!/usr/bin/env python3
"""C4 construction laws: CORRECT structural analysis of n=72 solution.

Correct model check before deriving rules:
- Parse 144 points of n=72 C4 solution (full board).
- Verify C4 symmetry.
- Extract fundamental-domain cells (one per orbit).
- Check row/column distribution of domain cells to identify the TRUE
  2-factor model (Row-Degree Theorem: C4 sol <-> 2-regular graph on m=n/2 vertices).
"""
import os
from collections import Counter

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}
CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'

def load_points(n, fname=None):
    p = os.path.join(CACHE, fname or f'n{n}_rot4.few')
    with open(p) as f:
        line = f.readline().strip()
    body = line[1:] if line[0] in '.:/-ocx+*' else line
    pts = []
    for r in range(n):
        c1 = VAL[body[2*r]]; c2 = VAL[body[2*r+1]]
        pts.append((r, c1)); pts.append((r, c2))
    return pts

def domain_cells(pts, n):
    N = n // 2
    used = set(); cells = []
    for p in pts:
        if p in used: continue
        r, c = p
        orbit = [(r,c),(c,n-1-r),(n-1-r,n-1-c),(n-1-c,r)]
        used.update(orbit)
        for cell in orbit:
            if cell[0] < N and cell[1] < N:
                cells.append(cell); break
    return cells

n = 72; N = n//2
pts = load_points(n)
print(f"n={n}: {len(pts)} points")
ptset = set(pts)
viol = sum(1 for (r,c) in pts for nr,nc in [(c,n-1-r),(n-1-r,n-1-c),(n-1-c,r)] if (nr,nc) not in ptset)
print(f"C4 symmetry violations: {viol}")

cells = domain_cells(pts, n)
print(f"domain cells: {len(cells)}")

rowcount = Counter(r for r,c in cells)
colcount = Counter(c for r,c in cells)
rows_bad = sorted([r for r in range(N) if rowcount[r]!=2])
cols_bad = sorted([c for c in range(N) if colcount[c]!=2])
print(f"rows with cell count != 2: {rows_bad}")
print(f"cols with cell count != 2: {cols_bad}")
print(f"row count values: {dict(Counter(rowcount.values()))}")
print(f"col count values: {dict(Counter(colcount.values()))}")

# Hypothesis A: each domain ROW r has exactly 2 cells -> 2-regular on rows,
# edges = the two columns chosen in that row.
if all(rowcount[r]==2 for r in range(N)):
    print("\n[Model A] each domain row has exactly 2 cells -> 2-regular on rows")
    adj = {r: [] for r in range(N)}
    for r,c in cells:
        adj[r].append(c)
    # edges as (min,max) of the two columns
    edgesA = [tuple(sorted(adj[r])) for r in range(N)]
    print(f"  edgesA (row-pair of cols): {sorted(edgesA)}")
    # cycle decomposition on rows? No—edges connect columns. Build graph on columns:
    g = {c: [] for c in range(N)}
    for r in range(N):
        a,b = adj[r]
        g[a].append(b); g[b].append(a)
    visited=set(); cycles=[]
    for v in range(N):
        if v in visited: continue
        cyc=[v]; visited.add(v); prev=v; cur=g[v][0]
        while cur!=v:
            cyc.append(cur); visited.add(cur)
            nxt = g[cur][0] if g[cur][1]==prev else g[cur][1]
            prev,cur=cur,nxt
        cycles.append(len(cyc))
    print(f"  column-graph cycle decomposition: {tuple(sorted(cycles))}")

# Hypothesis B: each domain CELL is a vertex; edges via some real relation.
# Print the raw cells for manual inspection.
print(f"\nRaw domain cells (r,c):")
for i,(r,c) in enumerate(sorted(cells)):
    print(f"  {i:2d}: ({r},{c})")
