#!/usr/bin/env python3
"""
Refined conflict-predicate analysis.

Separate BOUNDARY-type conflicts (a cell touches the grid edge, i.e. its
fundamental coords include 0 or m-1) from INTERIOR conflicts, and test whether
interior conflicts obey a simple gcd/divisibility rule. Also confirm the
conflict-rate scaling with m.
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

def is_boundary(i, j, m):
    return i == 0 or i == m-1 or j == 0 or j == m-1

def analyze(m):
    n = 2*m
    cells = [(i, j) for i in range(m) for j in range(m)]
    total = len(cells)*(len(cells)-1)//2
    nconf = 0
    boundary = 0
    interior = 0
    # interior conflict invariants
    interior_gcd_di_dj = Counter()
    interior_diag = 0
    for a in range(len(cells)):
        for b in range(a+1, len(cells)):
            i, j = cells[a]
            ip, jp = cells[b]
            if not orbits_conflict(i, j, ip, jp, n):
                continue
            nconf += 1
            if is_boundary(i, j, m) or is_boundary(ip, jp, m):
                boundary += 1
            else:
                interior += 1
                g = math.gcd(abs(i-ip), abs(j-jp))
                interior_gcd_di_dj[g] += 1
                if abs(i-ip) == abs(j-jp):
                    interior_diag += 1
    return {
        'm': m, 'n_cells': len(cells), 'total': total, 'nconf': nconf,
        'rate_pct': 100*nconf/total,
        'boundary': boundary, 'interior': interior,
        'interior_gcd_top': interior_gcd_di_dj.most_common(8),
        'interior_diag_frac': interior_diag/max(1, interior),
    }

def main():
    rows = []
    for m in [10, 14, 18, 22, 26]:
        r = analyze(m)
        rows.append(r)
        print(f"m={m:>2} (n={2*m:>2}): rate={r['rate_pct']:.3f}%  "
              f"boundary={r['boundary']} interior={r['interior']}  "
              f"(boundary fraction={100*r['boundary']/max(1,r['nconf']):.1f}%)")
        print(f"      interior gcd(|di|,|dj|) top: {r['interior_gcd_top']}")
        print(f"      interior diagonal (|di|=|dj|) frac={r['interior_diag_frac']:.2f}")
    # scaling fit: rate ~ c * m^p
    print("\n=== SCALING (log-log) ===")
    import statistics
    xs = [math.log(r['m']) for r in rows]
    ys = [math.log(r['rate_pct']) for r in rows]
    # least squares
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxx = sum((x-mx)**2 for x in xs)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    p = sxy/sxx
    c = math.exp(my - p*mx)
    print(f"   rate(m) ~ {c:.3f} * m^{p:.3f}")
    print(f"   (m^-1.5 would give exponent -1.5; m^-1 gives -1.0)")

if __name__ == '__main__':
    main()
