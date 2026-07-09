#!/usr/bin/env python3
"""
Reverse-engineer the orbit-pair collinearity (conflict) predicate.

For a C4 solution on n=2m, each orbit = 4 points under 90deg rotation about
center. Two orbit-edges {i,j} and {i',j'} (domain cells in [0,m)x[0,m)) are
COMPATIBLE iff their union contains no 3 collinear points. The whole
construction problem reduces to: which 2-factors on m vertices have ALL
edge-pairs compatible?

Here we characterize the COMPATIBILITY predicate P(i,j,i',j',m) by enumerating
all pairs at small m and testing candidate algebraic rules.
"""
import math
from itertools import combinations
from collections import Counter

def orbits_conflict(i1, j1, i2, j2, n):
    pts = [
        (i1, j1), (j1, n-1-i1), (n-1-i1, n-1-j1), (n-1-j1, i1),
        (i2, j2), (j2, n-1-i2), (n-1-i2, n-1-j2), (n-1-j2, i2),
    ]
    for a, b, c in combinations(range(8), 3):
        (x1, y1), (x2, y2), (x3, y3) = pts[a], pts[b], pts[c]
        if (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1):
            return True
    return False

def gcd(a, b):
    return math.gcd(a, b)

def symmetry_invariants(i, j, ip, jp, m):
    """Compute candidate invariants of a pair of domain cells."""
    # raw
    di = i - ip
    dj = j - jp
    si = i + j
    sj = ip + jp
    # rotated by 90 about center: (i,j)->(j,2m-1-i); in fundamental coords the
    # cell (i,j) and its rotations are the same orbit, so consider min over orbit
    # representatives of the difference vector
    invs = set()
    # orbit of (i,j) under R(x,y)=(y,2m-1-x), fundamental cell stays (i,j) by def
    # but the *pair* (cell1, cell2) can be rotated; we want invariants of the pair
    # up to simultaneous 90deg rotation. Compute the 4 rotations of cell2 relative:
    rots = [(ip, jp), (jp, 2*m-1-ip), (2*m-1-ip, 2*m-1-jp), (2*m-1-jp, ip)]
    dis = []
    for (rp, rq) in rots:
        dis.append((i - rp, j - rq))
    # invariant: sorted absolute differences, and gcd of components
    gset = set()
    for (a, b) in dis:
        gset.add(gcd(abs(a), abs(b)))
    return {
        'di': di, 'dj': dj, 'si': si, 'sj': sj,
        'gdis': tuple(sorted(gset)),
        'abs_di': abs(di), 'abs_dj': abs(dj),
    }

def enumerate_predicate(m):
    n = 2 * m
    cells = [(i, j) for i in range(m) for j in range(m)]
    pairs = []
    nconf = 0
    for a in range(len(cells)):
        for b in range(a + 1, len(cells)):
            i, j = cells[a]
            ip, jp = cells[b]
            if orbits_conflict(i, j, ip, jp, n):
                nconf += 1
                pairs.append((i, j, ip, jp))
    return cells, pairs, nconf

def main():
    for m in [10, 14, 18]:
        cells, pairs, nconf = enumerate_predicate(m)
        total = len(cells) * (len(cells) - 1) // 2
        print(f"\n{'='*60}\n m={m} (n={2*m}): {len(cells)} cells, "
              f"{total} pairs, {nconf} CONFLICTING ({100*nconf/total:.2f}%)")
        # Test hypotheses on the conflicting-pair set
        # H: conflict iff gcd of some difference component is 'large'
        # Inspect: for conflicting pairs, what are the gcd values?
        gvals = Counter()
        di0 = Counter()
        for (i, j, ip, jp) in pairs:
            inv = symmetry_invariants(i, j, ip, jp, m)
            g = inv['gdis']
            gvals[g] += 1
            if inv['abs_di'] == 0:
                di0['di0'] += 1
            if inv['abs_dj'] == 0:
                di0['dj0'] += 1
        # Most common gcd-sets
        print(f"   top gcd-invariants among conflicts: "
              f"{gvals.most_common(6)}")
        print(f"   conflicts with di=0: {di0.get('di0',0)}, dj=0: {di0.get('dj0',0)}")
        # Show 8 sample conflicting pairs
        print("   sample conflicting pairs (i,j | i',j'):")
        for (i, j, ip, jp) in pairs[:8]:
            inv = symmetry_invariants(i, j, ip, jp, m)
            print(f"      ({i},{j}) x ({ip},{jp})   di={inv['di']} dj={inv['dj']} "
                  f"gcd-set={inv['gdis']}")

if __name__ == '__main__':
    main()
