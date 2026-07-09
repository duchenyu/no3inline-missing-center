#!/usr/bin/env python3
"""
C₄ Construction Rule Discovery

Instead of searching for solutions, derive the algebraic rules for valid C₄ solutions.
Focus on the n=72 (m=36) full 36-cycle — the only known C₄ solution at this scale.

Key questions:
1. What characterizes allowed edges (i,j)? 
2. What pattern connects successive vertices in the cycle?
3. Can we extend the pattern to m=37, 38, ...?
"""
import os, math
from itertools import combinations

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}
CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'

def get_domain_cells(pts, n):
    m = n // 2
    used = set()
    cells = []
    for pt in pts:
        if pt in used: continue
        r, c = pt
        orbit = [(r,c), (c,n-1-r), (n-1-r,n-1-c), (n-1-c,r)]
        used.update(orbit)
        for p in orbit:
            if p[0] < m and p[1] < m:
                cells.append(p)
                break
    return cells

def collinear(p1, p2, p3):
    (x1,y1),(x2,y2),(x3,y3) = p1, p2, p3
    return (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1)

# === 1. EXTRACT n=72 edges ===
print("=" * 70)
print("C4 CONSTRUCTION RULE ANALYSIS")
print("=" * 70)

n = 72; m = n // 2
p = os.path.join(CACHE, 'n72_rot4.few')
with open(p) as f:
    line = f.readline().strip()
body = line[1:] if line[0] in '.:/-ocx+*' else line

pts = []
for r in range(n):
    c1 = VAL.get(body[2*r]); c2 = VAL.get(body[2*r+1])
    pts.append((r, c1)); pts.append((r, c2))

cells = get_domain_cells(pts, n)
edges = [(min(i,j), max(i,j)) for (i,j) in cells]

print(f"\n1. n=72 (m=36) — {len(edges)} edges")
print(f"   Edges: {sorted(edges)}")

# === 2. ANALYZE EDGE PATTERNS ===

# 2a: Vertex pairing
print(f"\n2. EDGE PATTERN ANALYSIS")

# Sum i+j for each edge
sums = [i+j for i,j in edges]
print(f"   Sum i+j distribution: min={min(sums)}, max={max(sums)}")
sum_counts = {}
for s in sums:
    sum_counts[s] = sum_counts.get(s, 0) + 1
print(f"   Most common sums: {sorted(sum_counts.items(), key=lambda x:-x[1])[:10]}")

# Product i*j
prods = [i*j for i,j in edges]
print(f"   Product i*j distribution: min={min(prods)}, max={max(prods)}")

# 2b: (i - j) mod 36  
diffs = [(i-j) % m for i,j in edges]
diff_counts = {}
for d in diffs:
    diff_counts[d] = diff_counts.get(d, 0) + 1
print(f"   (i-j) mod m: {sorted(diff_counts.items())[:10]}")

# 2c: Check if edges avoid certain regions
# Test: does i > j/2 or i < j/2?
above_diag = sum(1 for i,j in edges if i > j)
below_diag = sum(1 for i,j in edges if i < j)
on_diag = sum(1 for i,j in edges if i == j)
print(f"   Position rel to diagonal: above={above_diag}, below={below_diag}, on={on_diag}")

# 2d: What fraction of edges connect "near" vs "far" vertices?
far_edges = sum(1 for i,j in edges if abs(i-j) > m//3)
near_edges = sum(1 for i,j in edges if abs(i-j) <= m//3)
print(f"   Distance: near(<=m/3)={near_edges}, far(>m/3)={far_edges}")

# === 3. CHECK IF THE CYCLE FOLLOWS A NUMBER-THEORETIC PATTERN ===
print(f"\n3. NUMBER-THEORETIC PATTERNS")

# Get cycle order
adj = {i: [] for i in range(m)}
for i, j in edges:
    adj[i].append(j)
    adj[j].append(i)

cycle = [0]
visited = {0}
prev = -1
curr = 0
while True:
    nxt = [n for n in adj[curr] if n != prev][0]
    if nxt == 0:
        break
    cycle.append(nxt)
    visited.add(nxt)
    prev = curr
    curr = nxt

print(f"   Cycle length: {len(cycle)}")

# Check: is cycle[i+1] a function of cycle[i]?
# Test: multiplicative inverse? quadratic? 
# Test: (cycle[i] * k) mod m = cycle[i+1]?
for k in range(2, 20):
    matches = sum(1 for i in range(len(cycle)) if (cycle[i] * k) % m == cycle[(i+1) % len(cycle)] or (cycle[(i+1) % len(cycle)] * k) % m == cycle[i])
    if matches > 20:
        print(f"   k*m mod m pattern: k={k}, {matches}/{len(cycle)} matches")

# Test: cycle[i+1] = (a*cycle[i] + b) mod m pattern?
# This is a linear congruential generator
for a in range(1, m):
    matches = 0
    for i in range(len(cycle)):
        expected = (a * cycle[i]) % m
        actual = cycle[(i + 1) % len(cycle)]
        if expected == actual or cycle[(i - 1) % len(cycle)] == expected:
            matches += 1
    if matches == len(cycle):
        print(f"   ✅ LCG pattern: cycle[i+1] = {a}*cycle[i] mod m")
        break

# Test: is cycle[i+1] the "complement" of cycle[i]? (m-1-i)
complement_matches = sum(1 for i in range(len(cycle)) if cycle[(i+1) % len(cycle)] == m - 1 - cycle[i])
print(f"   Complement matches: {complement_matches}/{len(cycle)}")

# Test: sum of consecutive vertices
pairs = [(cycle[i], cycle[(i+1)%len(cycle)]) for i in range(len(cycle))]
pair_sums = [i+j for i,j in pairs]
print(f"   Pair sums: min={min(pair_sums)}, max={max(pair_sums)}, median={sorted(pair_sums)[len(pair_sums)//2]}")

# === 4. COLLINEARITY CONDITION ANALYSIS ===
print(f"\n4. COLLINEARITY CONDITIONS BETWEEN ORBITS")

# For two orbits (i,j) and (i',j'), check what makes them conflicting
# Pick some pairs of edges and check if their orbits have collinear triples
def orbits_conflict(i1, j1, i2, j2, n):
    """Check if orbits (i1,j1) and (i2,j2) produce any collinear triple."""
    pts = [
        (i1, j1), (j1, n-1-i1), (n-1-i1, n-1-j1), (n-1-j1, i1),
        (i2, j2), (j2, n-1-i2), (n-1-i2, n-1-j2), (n-1-j2, i2)
    ]
    for a, b, c in combinations(range(8), 3):
        if collinear(pts[a], pts[b], pts[c]):
            return True
    return False

# Check all EDGE PAIRS in n=72 solution
conflict_count = 0
edge_list = list(set(edges))  # deduplicate
for a in range(len(edge_list)):
    for b in range(a+1, len(edge_list)):
        i1, j1 = edge_list[a]
        i2, j2 = edge_list[b]
        if orbits_conflict(i1, j1, i2, j2, n):
            conflict_count += 1

total_pairs = len(edge_list) * (len(edge_list) - 1) // 2
print(f"   Edge pairs checked: {total_pairs}")
print(f"   Conflicting pairs: {conflict_count} ({conflict_count/total_pairs*100:.1f}%)")
print(f"   Non-conflicting: {total_pairs - conflict_count}")

# === 5. DISTANCE PATTERN ===
print(f"\n5. DISTANCE PATTERN (domain cell norm)")

# For each edge (i,j), compute its norm in the domain: i² + j²
norms = [i*i + j*j for i,j in edges]
norm_counts = {}
for nrm in norms:
    norm_counts[nrm] = norm_counts.get(nrm, 0) + 1
print(f"   Norms: {sorted(norm_counts.items())[:15]}")
unique_norms = len(norm_counts)
print(f"   Unique norms: {unique_norms}")

# === 6. CHECK IF EDGES FORM A PERFECT MATCHING-INDUCED CYCLE ===
print(f"\n6. BIPARTITE STRUCTURE")

# Are edges bipartite with respect to vertex parity?
even_even = [(i,j) for i,j in edges if i%2==0 and j%2==0]
odd_odd = [(i,j) for i,j in edges if i%2==1 and j%2==1]
even_odd = [(i,j) for i,j in edges if i%2==0 and j%2==1]
odd_even = [(i,j) for i,j in edges if i%2==1 and j%2==0]
print(f"   (even,even): {len(even_even)}")
print(f"   (odd,odd): {len(odd_odd)}")
print(f"   (even,odd): {len(even_odd)}")
print(f"   (odd,even): {len(odd_even)}")
print(f"   Balanced: {len(even_even)==len(odd_odd)==len(even_odd)==len(odd_even)}")

# === 7. COMPARE WITH SMALLER n PATTERNS ===
print(f"\n7. PATTERN ACROSS DIFFERENT n VALUES")

for test_n in [14, 16, 20, 24, 28, 44, 56]:
    test_m = test_n // 2
    p = os.path.join(CACHE, f'n{test_n}_rot4')
    if not os.path.exists(p):
        p = os.path.join(CACHE, f'n{test_n}_rot4.few')
    if not os.path.exists(p): 
        continue
    
    with open(p) as f:
        line = f.readline().strip()
    body = line[1:] if line[0] in '.:/-ocx+*' else line
    pts = []
    for r in range(test_n):
        c1 = VAL.get(body[2*r]); c2 = VAL.get(body[2*r+1])
        pts.append((r, c1)); pts.append((r, c2))
    
    cells = get_domain_cells(pts, test_n)
    edges = [(min(i,j), max(i,j)) for (i,j) in cells]
    e_sum = sum(i+j for i,j in edges) / len(edges) if edges else 0
    e_prod = sum(i*j for i,j in edges) / len(edges) if edges else 0
    
    even_even_c = sum(1 for i,j in edges if i%2==0 and j%2==0)
    odd_odd_c = sum(1 for i,j in edges if i%2==1 and j%2==1)
    even_odd_c = sum(1 for i,j in edges if i%2==0 and j%2==1)
    odd_even_c = sum(1 for i,j in edges if i%2==1 and j%2==0)
    
    print(f"   n={test_n:>3} (m={test_m:>2}): edges={len(edges):>3}, avg_sum={e_sum:.1f}, "
          f"even_even={even_even_c:>2}, odd_odd={odd_odd_c:>2}, "
          f"even_odd={even_odd_c:>2}, odd_even={odd_even_c:>2}")

print(f"\n{'='*70}")
print("KEY INSIGHTS NEEDED:")
print("1. Why does the n=72 36-cycle work?")
print("2. What edge patterns are FORBIDDEN (create collinear triples)?")
print("3. Can the pattern be extended to m > 36?")
print(f"{'='*70}")
