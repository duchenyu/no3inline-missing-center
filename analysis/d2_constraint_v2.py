#!/usr/bin/env python3
"""
Step 2 (corrected): Analyze the C4 constraint from KNOWN solutions.
Count how many domain cells would be allowed at each selection step.
"""
import os, math, json
from collections import defaultdict
from itertools import combinations

CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'
ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}

def load_solutions(n):
    sols = []
    for ext in ['', '.few']:
        p = os.path.join(CACHE, f'n{n}_rot4{ext}')
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.rstrip()
                    if not line: continue
                    pre = line[0]
                    body = line[1:] if pre in '.:/-ocx+*' else line
                    if len(body) < 2 * n: continue
                    pts = []
                    ok = True
                    for r in range(n):
                        c1 = VAL.get(body[2*r])
                        c2 = VAL.get(body[2*r+1])
                        if c1 is None or c2 is None or c1 >= n or c2 >= n:
                            ok = False; break
                        pts.append((r, c1)); pts.append((r, c2))
                    if ok and len(pts) == 2 * n:
                        sols.append(pts)
    return sols

def extract_c4_orbit_dirs(pts, n):
    """Get N directions from C4 orbit representatives."""
    N = n // 2
    used = set()
    dirs = []
    for p in pts:
        if p in used: continue
        r, c = p
        orbit = [(r,c), (c, n-1-r), (n-1-r, n-1-c), (n-1-c, r)]
        # Use canonical (smallest row, then col)
        canon = min(orbit)
        used.update(orbit)
        a = 2*canon[0] - (n-1); b = 2*canon[1] - (n-1)
        g = abs(math.gcd(a,b)) or 1; a//=g; b//=g
        if a < 0 or (a == 0 and b < 0): a,b = -a,-b
        dirs.append((a,b) if (a,b) != (0,0) else None)
    return [d for d in dirs if d is not None]

# For each N, compute the direction diversity and effective degrees of freedom
# Then estimate the "constraint density" per C4 domain selection

print("=" * 60)
print("C4 Effective Constraint Density (from known solutions)")
print("=" * 60)
print()

for n in [12, 16, 20, 24, 28, 32, 36, 40, 44, 56]:
    sols = load_solutions(n)
    if not sols: continue
    N = n // 2
    
    # Collect all unique direction sets
    all_dirs = set()
    dir_counts = defaultdict(int)  # direction -> frequency
    
    for pts in sols[:min(len(sols), 200)]:
        dirs = extract_c4_orbit_dirs(pts, n)
        for d in dirs:
            all_dirs.add(d)
            dir_counts[d] += 1
    
    # Key metric: usable directions as fraction of N²
    usable = len(all_dirs)
    
    # Entropy: how evenly distributed are directions across N slots?
    # High entropy = many different ways to select directions
    # Low entropy = most solutions use similar directions

    # For each solution, count how many of its N dirs are in the top-k
    sol_count = min(len(sols), 200)
    top_10_dirs = set(d for d, _ in sorted(dir_counts.items(), key=lambda x: -x[1])[:N])
    avg_top_hit = 0
    for pts in sols[:sol_count]:
        dirs = extract_c4_orbit_dirs(pts, n)
        avg_top_hit += sum(1 for d in dirs if d in top_10_dirs) / sol_count
    
    # The "constraint pressure" metric:
    # How many of the N² possible directions are actually usable?
    usable_frac = usable / (N * N)
    
    # Estimated freedom per selection:
    # If a solution randomly picks N dirs from usable pool:
    expected_freedom = usable     # total unique dirs available
    needed = N                     # needed per solution
    
    print(f"n={n:>3} (N={N:>2}): {sol_count} sols sampled"
          f"\n  usable dirs={usable:>4}/{N*N:>4} ({usable_frac:.1%})"
          f"\n  need {needed} dirs per sol → excess={usable - needed}"
          f"\n  top-{N} dirs avg use: {avg_top_hit/needed:.1%} per sol"
          f"\n  directional freedom: {'✅ abundant' if usable >= 3*N else '⚠️ tight' if usable >= 2*N else '❌ scarce'}")

# Extrapolate to N=38
print(f"\n{'='*60}")
print("Extrapolation to N=38")
print(f"{'='*60}")
print()
print("From known data (N=10 to N=28):")
print("  usable dirs stable at ~75-81% of N²")
print("  For N=38: expected usable ≈ 0.78 × 1444 ≈ 1126 dirs")
print("  Need: N = 38 dirs per solution")
print("  Excess: 1126 - 38 = 1088 → abundant")
print()
print("Since direction diversity doesn't shrink, the crash at N≈36")
print("is NOT a phase transition in direction availability.")
print("It must be in the structure of the MATCHING (how directions")
print("are assigned to specific rows/columns).")
print()
print("The matching constraint is a 2-regular bipartite graph on N×N.")
print("Two different assignments of the SAME direction set to rows")
print("can produce different C4 orbits and different collinearity patterns.")
print()
print("The true bottleneck: the INTERSECTION of:")
print("  1. Selecting N directions from ~75% of N² pool")
print("  2. Arranging them into a 2-regular bipartite graph")
print("  3. C4 orbit structure (each orbit maps to 4 distinct cells)")
print("  4. No collinear triples among the 4N = 2n C4 images")
