#!/usr/bin/env python3
"""
Cross-edge analysis: for each heavy direction d in D6, which other directions
does it "block" (participate in at least one hyperedge with)?

This reveals the structural constraint: selecting d restricts which other
directions can be selected in the same independent set.
"""
import os, math, json
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HEAVY = {(1,1), (1,-1), (3,1), (1,3), (3,-1), (1,-3)}
TARGETS = [16, 20, 24, 28, 32]  # skip 12 (too few for patterns)

def build_orbits(n):
    seen = set(); orbits = []
    for r in range(n):
        for c in range(n):
            p = (r, c)
            if p in seen: continue
            q = (n-1-p[0], n-1-p[1]); seen.add(p); seen.add(q)
            a = 2*p[0] - (n-1); b = 2*p[1] - (n-1)
            g = math.gcd(a,b) or 1; a,b = a//g, b//g
            if a < 0 or (a == 0 and b < 0): a,b = -a,-b
            orbits.append(((a,b), (p, q)))
    return orbits

def collinear3(pts):
    for a in range(3):
        x1, y1 = pts[a]
        for b in range(a+1, 3):
            x2, y2 = pts[b]
            for c in range(b+1, 3):
                x3, y3 = pts[c]
                if (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1): return True
    return False

for n in TARGETS:
    orbits = build_orbits(n)
    m = len(orbits); pts = [o[1] for o in orbits]; dirs = [o[0] for o in orbits]
    
    # Build direction-to-index mapping
    dir_to_idx = {}
    for idx, d in enumerate(dirs):
        dir_to_idx.setdefault(d, []).append(idx)
    
    # For each heavy direction d: which other directions co-occur in a hyperedge?
    # blocked[d] = set of directions (not in D6) that form a hyperedge WITH d
    blocked = {d: Counter() for d in HEAVY}  # d -> {other_dir: count_of_hyperedges}
    
    for i in range(m):
        p_i = pts[i]; d_i = dirs[i]
        for j in range(i+1, m):
            p_j = pts[j]; d_j = dirs[j]
            pts_ij = p_i + p_j
            for k in range(j+1, m):
                if collinear3(pts_ij + pts[k]):
                    # This triple {i,j,k} is a hyperedge
                    dset = {d_i, d_j, dirs[k]}
                    # For each heavy direction in this triple, record the other two
                    for d_heavy in dset & HEAVY:
                        for d_other in dset - {d_heavy}:
                            if d_other not in HEAVY:  # Only track non-heavy others
                                blocked[d_heavy][d_other] += 1
    
    print(f"\n{'='*60}")
    print(f"n={n} (orbits={m})")
    print(f"{'Heavy Dir':>12} | {'Blocked Non-Heavy':>20} | {'Count':>8} | {'Blocked/Total%':>14}")
    print("-"*60)
    
    total_non_heavy = sum(1 for d in dirs if d not in HEAVY)
    
    for d in sorted(HEAVY, key=lambda x: (abs(x[0]), abs(x[1]))):
        bset = set(blocked[d].keys())
        bcount = len(bset)
        ratio = bcount / total_non_heavy * 100 if total_non_heavy > 0 else 0
        top5 = sorted(blocked[d].items(), key=lambda kv: -kv[1])[:5]
        top_str = ', '.join([f'{k}={v}' for k,v in top5])
        print(f"{str(d):>12} | {bcount:>5} dirs blocked | {sum(blocked[d].values()):>8} | {ratio:>13.1f}%")
        print(f"             top5: {top_str}")
    
    # Intersection analysis: directions blocked by ALL heavy directions
    all_blocked_sets = [set(blocked[d].keys()) for d in HEAVY]
    intersection = set.intersection(*all_blocked_sets) if all_blocked_sets else set()
    union = set.union(*all_blocked_sets)
    print(f"\n  Blocked by ALL heavy dirs: {len(intersection)} directions")
    if intersection:
        print(f"    {sorted(list(intersection))[:10]}...")
    print(f"  Blocked by ANY heavy dir: {len(union)} / {total_non_heavy}")
    
    # Direction blocked by exactly 0 heavy dirs
    blocked_by_any = set()
    for d in HEAVY:
        blocked_by_any.update(blocked[d].keys())
    never_blocked = [d for d in set(dirs) if d not in HEAVY and d not in blocked_by_any]
    print(f"  NEVER blocked by heavy dirs: {len(never_blocked)} directions")
    if never_blocked:
        print(f"    e.g. {sorted(never_blocked)[:15]}...")

print(f"\n{'='*60}")
print("CROSS-EDGE SUMMARY")
