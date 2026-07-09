#!/usr/bin/env python3
"""
C4 Construction-Law Discovery (v2) — cross-n analysis.

Goal: derive construction rules for C4 (4-fold rotational) NTIL solutions
from the STRUCTURE of known solutions, not by searching.

For a C4 solution on n x n (n even), the 4-fold rotation partitions the grid
into orbits of size 4; the solution uses exactly m = n/2 orbits. By the
Row-Degree Theorem, these m orbits form a 2-regular graph (2-factor) on the
vertex set {0,...,m-1}: each orbit contributes one "domain cell" (r,c) with
r,c in [0,m), and we draw the edge {r,c}. Each vertex then has degree exactly 2.

We extract this 2-factor for EVERY rot4 solution in n=58..72 and look for
INVARIANT structural patterns that hold across all n — those are the
construction laws.
"""
import os, math, json
from itertools import combinations
from collections import Counter

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}
CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'

def parse_solution(line, n):
    """Return list of (row, col) points for a .few format line."""
    line = line.strip()
    body = line[1:] if line and line[0] in '.:/-ocx+*' else line
    pts = []
    for r in range(n):
        c1 = VAL[body[2*r]]; c2 = VAL[body[2*r+1]]
        pts.append((r, c1)); pts.append((r, c2))
    return pts

def verify_no3(pts, n):
    """True if pts is a valid no-3-in-line set."""
    P = [(x, y) for (x, y) in pts]
    for a, b, c in combinations(P, 3):
        if (b[0]-a[0])*(c[1]-a[1]) == (c[0]-a[0])*(b[1]-a[1]):
            return False
    return True

def domain_cells(pts, n):
    """One fundamental-domain cell (r,c) with r,c in [0,m) per orbit."""
    m = n // 2
    used = set()
    cells = []
    for pt in pts:
        if pt in used:
            continue
        r, c = pt
        orbit = [(r, c), (c, n-1-r), (n-1-r, n-1-c), (n-1-c, r)]
        used.update(orbit)
        for p in orbit:
            if p[0] < m and p[1] < m:
                cells.append(p)
                break
    return cells

def extract_2factor(cells):
    """edges = {min(i,j), max(i,j)} for each domain cell (i,j)."""
    edges = []
    for (i, j) in cells:
        edges.append((min(i, j), max(i, j)))
    return edges

def cycle_decomp(edges, m):
    """Return list of cycle lengths of the 2-regular graph on {0..m-1}."""
    adj = {v: [] for v in range(m)}
    for i, j in edges:
        adj[i].append(j); adj[j].append(i)
    # verify 2-regular
    degs = [len(adj[v]) for v in range(m)]
    is_2reg = all(d == 2 for d in degs)
    seen = set()
    cycles = []
    for v in range(m):
        if v in seen:
            continue
        # walk
        start = v
        prev = -1
        curr = v
        cyc = []
        while True:
            cyc.append(curr)
            seen.add(curr)
            nxts = [x for x in adj[curr] if x != prev]
            if not nxts:
                break
            nxt = nxts[0]
            if nxt == start:
                break
            prev = curr
            curr = nxt
        cycles.append(len(cyc))
    return cycles, is_2reg, degs

def orbits_conflict(i1, j1, i2, j2, n):
    """Do orbits {i1,j1} and {i2,j2} (domain cells) produce a collinear triple?"""
    pts = [
        (i1, j1), (j1, n-1-i1), (n-1-i1, n-1-j1), (n-1-j1, i1),
        (i2, j2), (j2, n-1-i2), (n-1-i2, n-1-j2), (n-1-j2, i2),
    ]
    for a, b, c in combinations(range(8), 3):
        (x1, y1), (x2, y2), (x3, y3) = pts[a], pts[b], pts[c]
        if (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1):
            return True
    return False

def analyze_solution(pts, n):
    m = n // 2
    cells = domain_cells(pts, n)
    edges = extract_2factor(cells)
    cyc, is_2reg, degs = cycle_decomp(edges, m)
    # parity classes
    cls = Counter()
    for i, j in edges:
        cls[(i % 2, j % 2)] += 1
    # triangularity: edge {i,j} with i<j means "strictly lower triangular"
    lower = sum(1 for i, j in edges if i < j)
    upper = sum(1 for i, j in edges if i > j)
    diag = sum(1 for i, j in edges if i == j)
    # anti-diagonal pairing: i+j == m-1 (perfect anti-diag in [0,m))
    anti = sum(1 for i, j in edges if i + j == m - 1)
    # sum distribution
    sums = Counter(i + j for i, j in edges)
    # collinearity conflicts between edges
    ec = list(set(edges))
    conflicts = 0
    for a in range(len(ec)):
        for b in range(a+1, len(ec)):
            if orbits_conflict(ec[a][0], ec[a][1], ec[b][0], ec[b][1], n):
                conflicts += 1
    total_pairs = len(ec) * (len(ec) - 1) // 2
    return {
        'm': m, 'n_edges': len(edges), 'n_cells': len(cells),
        'is_2reg': is_2reg, 'cycles': sorted(cyc, reverse=True),
        'n_cycles': len(cyc),
        'parity': dict(cls),
        'lower': lower, 'upper': upper, 'diag': diag,
        'anti_diag': anti,
        'sum_top': sums.most_common(5),
        'conflicts': conflicts, 'total_pairs': total_pairs,
        'edges': sorted(edges),
    }

def main():
    results = {}
    summary_rows = []
    for n in [58, 60, 62, 64, 66, 68, 70, 72]:
        p = os.path.join(CACHE, f'n{n}_rot4.few')
        if not os.path.exists(p):
            continue
        lines = [l for l in open(p) if l.strip()]
        sols = []
        for ln in lines:
            pts = parse_solution(ln, n)
            # sanity: count + no-3-collinear
            valid = (len(pts) == 2 * n) and verify_no3(pts, n)
            a = analyze_solution(pts, n)
            a['valid'] = valid
            a.pop('edges', None)  # not serializable-friendly huge list
            sols.append(a)
        results[n] = sols
        # aggregate stats
        ncyc_dist = Counter(str(tuple(s['cycles'])) for s in sols)
        anti_vals = [s['anti_diag'] for s in sols]
        lower_all = all(s['lower'] == s['n_edges'] for s in sols)
        parity_balanced = all(
            s['parity'].get((0,0),0) == s['parity'].get((1,1),0) ==
            s['parity'].get((0,1),0) == s['parity'].get((1,0),0)
            for s in sols)
        summary_rows.append({
            'n': n, 'm': n//2, 'n_sol': len(sols),
            'all_valid': all(s['valid'] for s in sols),
            'all_2reg': all(s['is_2reg'] for s in sols),
            'cycle_decomp_dist': {str(k): v for k, v in ncyc_dist.items()},
            'all_single_cycle': all(len(s['cycles']) == 1 for s in sols),
            'all_lower_tri': lower_all,
            'anti_diag_range': f"{min(anti_vals)}-{max(anti_vals)}",
            'parity_balanced': parity_balanced,
            'conflict_rate_range': f"{min(s['conflicts']/max(1,s['total_pairs']) for s in sols):.3f}-{max(s['conflicts']/max(1,s['total_pairs']) for s in sols):.3f}",
        })
        print(f"n={n}: {len(sols)} sols, all_valid={all(s['valid'] for s in sols)}, "
              f"cycle_decomps={dict(ncyc_dist)}, all_lower_tri={lower_all}, "
              f"parity_bal={parity_balanced}")

    # Detailed dump for n=72 (the richest single-cycle case) and one n=58 sample
    out = {'summary': summary_rows, 'detail': {}}
    for n in [58, 60, 64, 72]:
        out['detail'][n] = results[n][:3]  # first 3 sols for inspection
    with open('c4_construction_laws_v2.json', 'w') as f:
        json.dump(out, f, indent=1, default=str)
    print("\n[written] c4_construction_laws_v2.json")

    # Print the key cross-n invariants
    print("\n=== CROSS-n INVARIANTS ===")
    for row in summary_rows:
        print(f"  n={row['n']:>2} (m={row['m']:>2}): sols={row['n_sol']:>2} | "
              f"valid={row['all_valid']} 2reg={row['all_2reg']} | "
              f"single_cycle={row['all_single_cycle']} | lower_tri={row['all_lower_tri']} | "
              f"parity_bal={row['parity_balanced']} | anti_diag={row['anti_diag_range']}")

if __name__ == '__main__':
    main()
