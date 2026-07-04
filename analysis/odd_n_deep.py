"""
Odd n structural analysis: Why n=11 is the phase transition
Compares small odd (3,5,7,9) vs large odd (11,13,15,17,19)
"""
from collections import Counter, defaultdict
import math

# ============================================================
# PART 1: Ring Geometry Evolution
# ============================================================
print("=" * 90)
print("PART 1: Distance Ring Geometry (odd n)")
print("=" * 90)

for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
    center = (n-1)/2.0  # center IS a lattice point for odd n
    
    # All rings in the full grid
    all_rings = Counter()
    grid_pts = []
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
            grid_pts.append((i, j, d2))
    
    points_needed = 2 * n  # target
    ring_limit = 2  # max 2 per ring for missing-center
    
    # Ring statistics
    unique_rings = len(all_rings)
    total_slots = unique_rings * ring_limit  # maximum points without center
    slack_ratio = total_slots / points_needed  # >1 means "theoretically possible"
    
    # Ring size distribution (how many rings have 1,2,3,... grid points)
    ring_sizes = Counter(all_rings.values())
    
    # Center point ring
    center_d2 = 0  # center always has d^2=0
    center_pop = all_rings[center_d2]
    
    print(f"\nn={n}: center=({center:.0f},{center:.0f}) lattice point")
    print(f"  Points needed: {points_needed}")
    print(f"  Full grid rings: {unique_rings}")
    print(f"  Max capacity (2/ring): {total_slots}")
    print(f"  Slack ratio: {slack_ratio:.3f} ({'+' if slack_ratio >= 1 else '-'} {'FEASIBLE' if slack_ratio >= 1 else 'INFEASIBLE'})")
    print(f"  Center ring (d^2=0): {center_pop} grid points (must use ≤2)")
    print(f"  Ring size distribution (grid pts per ring):")
    for size in sorted(ring_sizes):
        print(f"    {ring_sizes[size]:3d} rings with {size:2d} grid points")

# ============================================================
# PART 2: The "Tight Rings" Bottleneck
# ============================================================
print("\n" + "=" * 90)
print("PART 2: Bottleneck Rings — the real constraint")
print("=" * 90)
print("Rings with few grid points force points to be dropped.")

for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
    center = (n-1)/2.0
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
    
    points_needed = 2 * n
    unique_rings = len(all_rings)
    
    # "Tight" rings: have exactly 1 or 2 grid points
    # If we use one, it consumes the ring but gives only 1 point
    tight_1 = {d2: pop for d2, pop in all_rings.items() if pop == 1}
    tight_2 = {d2: pop for d2, pop in all_rings.items() if pop == 2}
    tight_restricted = len(tight_1) + len(tight_2)
    
    # "Rich" rings: have >= 3 grid points
    rich = {d2: pop for d2, pop in all_rings.items() if pop >= 3}
    
    # Theoretical max: suppose we use ALL rings at their min(actual, 2) capacity
    max_possible = sum(min(pop, 2) for pop in all_rings.values())
    
    # But tight rings waste capacity: a ring with 1 point → 1 point per ring slot
    # A ring with 3 points → we can only use 2 → 2/3 efficiency
    
    # Count rings by population bracket
    brackets = {1: 0, 2: 0, 3: 0, 4: 0, '5-8': 0, '9+': 0}
    for pop in all_rings.values():
        if pop == 1: brackets[1] += 1
        elif pop == 2: brackets[2] += 1
        elif pop <= 4: brackets[4] += 1
        elif pop <= 8: brackets['5-8'] += 1
        else: brackets['9+'] += 1
    
    print(f"\nn={n}:")
    print(f"  Rings with 1 point:  {brackets[1]:3d}  (→ max 1 usable, wastes 0)")
    print(f"  Rings with 2 points: {brackets[2]:3d}  (→ max 2 usable, wastes 0)")
    print(f"  Rings with 3-4 pts:  {brackets[4]:3d}  (→ max 2 usable, wastes 1-2)")
    print(f"  Rings with 5-8 pts:  {brackets['5-8']:3d}  (→ max 2 usable, wastes 3-6)")
    print(f"  Rings with 9+ pts:   {brackets['9+']:3d}  (→ max 2 usable, wastes 7+)")
    print(f"  Max possible points (sum min(2,pop)): {max_possible}")
    print(f"  Points needed: {points_needed}")
    print(f"  Hard slack: {max_possible - points_needed} ({'+' if max_possible >= points_needed else 'INFEASIBLE'})")

# ============================================================
# PART 3: Distance Values Pattern (d^2 values)
# ============================================================
print("\n" + "=" * 90)
print("PART 3: Distance Ring Values — structural pattern")
print("=" * 90)
print("For odd n, d^2 = (2i-(n-1))^2 + (2j-(n-1))^2 where both terms are squares of even ints")
print()

for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
    center = (n-1)/2.0
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
    
    unique_rings = len(all_rings)
    
    # For odd n, offsets are: 0, ±2, ±4, ..., ±(n-1)
    # So possible squared offsets are: 0, 4, 16, 36, ..., (n-1)^2
    # And d^2 is sum of two such squares
    
    offsets = [(2*i - (n-1))**2 for i in range(n)]  # squared offsets
    unique_offsets = sorted(set(offsets))
    possible_d2 = sorted(set(a + b for a in unique_offsets for b in unique_offsets))
    
    actual_d2 = sorted(all_rings.keys())
    
    print(f"n={n}: {unique_rings} rings")
    print(f"  Unique offset squares: {len(unique_offsets)} values ({unique_offsets[:5]}...)")
    print(f"  Unique d^2 sums possible: {len(possible_d2)}")
    print(f"  Smallest 10 d^2: {actual_d2[:10]}")
    print(f"  Largest 10 d^2:  {actual_d2[-10:]}")

# ============================================================
# PART 4: Ring → Population → Constraint Trade-off
# ============================================================
print("\n" + "=" * 90)
print("PART 4: The n=11 Phase Transition — quantitative breakdown")
print("=" * 90)

for n in [3, 5, 7, 9, 11, 13]:
    center = (n-1)/2.0
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
    
    points_needed = 2 * n
    unique_rings = len(all_rings)
    
    # Selective slack: imagine we're smart and pick the best rings
    # How many rings do we NEED to use (at 2 pts each)?
    rings_needed = points_needed // 2  # minimum rings needed
    
    print(f"\nn={n}: need {rings_needed} rings (out of {unique_rings} available)")
    print(f"  Ratio rings_needed/available: {rings_needed}/{unique_rings} = {rings_needed/unique_rings:.2%}")
    
    # What fraction of rings are "large" (≥3 grid points)?
    small_rings = sum(1 for pop in all_rings.values() if pop < 3)
    large_rings = sum(1 for pop in all_rings.values() if pop >= 3)
    print(f"  Rings with <3 grid pts: {small_rings} (must use all as-is)")
    print(f"  Rings with >=3 pts: {large_rings} (must select {max(0, rings_needed - small_rings)} from these)")
    if large_rings > 0:
        print(f"  Selection ratio: {max(0, rings_needed - small_rings)}/{large_rings} = {max(0, rings_needed - small_rings)/large_rings:.2%}")
    
    # How many distinct d^2 values are there?
    offsets = sorted(set((2*i - (n-1))**2 for i in range(n)))
    print(f"  Squared-offset alphabet: {len(offsets)} symbols: {offsets}")

# ============================================================
# PART 5: Center Point Impact (odd n only)
# ============================================================
print("\n" + "=" * 90)
print("PART 5: Center Point = Unique Bottleneck for Odd n")
print("=" * 90)
print("The center (d^2=0) is a lattice point. For missing-center: at most 2 points.")

for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
    center = (n-1)/2.0
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
    
    # Center ring
    center_pop = all_rings[0]
    # How many rings have population = center_pop?
    same_pop_count = sum(1 for pop in all_rings.values() if pop == center_pop)
    
    print(f"n={n}: center ring has {center_pop} grid points")
    print(f"  Rings sharing this population: {same_pop_count}")
    print(f"  If center_pop >= 3: center ring can accommodate 3+ co-circular points")

# ============================================================
# PART 6: Known Missing-Center Data Analysis
# ============================================================
print("\n" + "=" * 90)
print("PART 6: Known Missing-Center Counts — Pattern Search")
print("=" * 90)

# Full search data (2-per-row constraint)
full_data = {
    3:  (2, 0),
    5:  (32, 4),
    7:  (132, 4),
    9:  (368, 8),
    11: (1120, 36),
    13: (3622, 292),
}

# D4-inequivalent data
inequiv_data = {
    7:  (22, 1, 4.5),
    9:  (51, 1, 2.0),
    11: (158, 6, 3.8),
    13: (499, 46, 9.2),
    15: (3978, 354, 8.9),
    17: (7094, 357, 5.0),
    19: (32577, 2363, 7.3),
}

print("\nFull search (2-per-row):")
for n in sorted(full_data):
    total, missing = full_data[n]
    ratio = missing / total * 100
    print(f"  n={n:2d}: missing={missing:4d} / total={total:6d} = {ratio:5.2f}%")

print("\nD4-inequivalent:")
for n in sorted(inequiv_data):
    total, missing, rate = inequiv_data[n]
    print(f"  n={n:2d}: missing={missing:4d} / total={total:6d} = {rate:5.1f}%")

# Derived metrics
print("\nGrowth analysis (inequivalent):")
prev_missing = None
prev_n = None
for n in sorted(inequiv_data):
    total, missing, rate = inequiv_data[n]
    if prev_missing is not None:
        growth = missing / prev_missing
        print(f"  n={prev_n}→{n}: missing {prev_missing}→{missing} ({growth:.1f}x)")
    prev_missing, prev_n = missing, n

# ============================================================
# PART 7: Hypothesis Testing
# ============================================================
print("\n" + "=" * 90)
print("PART 7: Why n=11? Structural Hypothesis")
print("=" * 90)

print("""
Hypothesis: n=11 is where the "ring pressure" crosses a threshold.
    
For small odd n (3,5,7,9):
  - Few total rings → most rings are "tight" (1-2 grid pts)
  - Tight rings are easy: just use them all, little choice to make
  - The "choice space" is small → few degrees of freedom

For n=11+:
  - Many rings are "rich" (≥3 grid pts) 
  - Must CHOOSE which 2 points per rich ring → combinatorial explosion
  - Collinearity constraints interact with ring choices → constraint density

But there's something more subtle:
  n=3:      4 offset values → 10 d^2 values → 4 rings actually needed
  n=5:      9 offset values → 15 d^2 values → need 5 rings
  n=7:     16 offset values → 28 d^2 values → need 7 rings  
  n=9:     25 offset values → 45 d^2 values → need 9 rings
  n=11:    36 offset values → 66 d^2 values → need 11 rings
  n=13:    49 offset values → 91 d^2 values → need 13 rings

  The d^2 alphabet grows as (n+1)^2/4 ≈ n^2/4 (quadratically)
  But we only need n rings (linearly)
  → At n=11, the ratio "needed/available" is 11/66 = 16.7%
  → At n=9,  it was 9/45 = 20.0%
  → At n=7,  it was 7/28 = 25.0%

  The SELECTION RATIO is actually getting SMALLER (easier!) with n...
  So ring availability is NOT the bottleneck.

  The REAL bottleneck must be:
    COLLINEARITY CONSTRAINTS growing superlinearly with n.
    
  Number of collinear triples in n×n grid ≈ O(n^3) (rough)
  But for missing-center, each ring choice imposes extra collinearity constraints
  because points in different rings interact via collinearity.
  
  At n=3,5,7,9: few rings → few ring pairs → collinearity = manageable
  At n=11+: many rings → O(rings^2) ring-pair interactions → collinearity = dense
""")

# Verify: count ring-pair interactions
print("\nRing-pair interaction count (upper bound):")
for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
    center = (n-1)/2.0
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-center)**2 + (j-center)**2))
            all_rings[d2] += 1
    
    num_rings = len(all_rings)
    pairs = num_rings * (num_rings - 1) // 2
    print(f"  n={n:2d}: {num_rings:3d} rings → {pairs:5d} ring pairs")

# ============================================================
# PART 8: Hidden Structure Search
# ============================================================
print("\n" + "=" * 90)
print("PART 8: Searching for Hidden Patterns in Missing Counts")
print("=" * 90)

import math

# Try various fits
inequiv_missing = {7:1, 9:1, 11:6, 13:46, 15:354, 17:357, 19:2363}

print("\nAttempting to find regularities:")

# 1. Does missing count grow as something like e^(c*n)?
print("\n1. Exponential fit: missing ~ a * exp(b*n)")
for n in sorted(inequiv_missing):
    if n >= 11:
        rate = math.log(inequiv_missing[n])
        print(f"  n={n}: log(missing) = {rate:.3f}")

# 2. Ratio to total solutions
print("\n2. Missing/Total ratio:")
for n in sorted(inequiv_data):
    total, missing, rate = inequiv_data[n]
    print(f"  n={n:2d}: {rate:.1f}%")

# 3. n≡1 vs n≡3 mod 4
print("\n3. By n mod 4:")
for mod_val in [1, 3]:
    matching = {n: v for n, v in inequiv_missing.items() if n % 4 == mod_val}
    growths = []
    prev = None
    for n in sorted(matching):
        if prev:
            growths.append(matching[n] / prev)
        prev = matching[n]
    print(f"  4k+{mod_val}: {matching}")
    if growths:
        print(f"    Growth factors: {[f'{g:.1f}' for g in growths]}")

# 4. Prime factorization
print("\n4. Prime status:")
for n in sorted(inequiv_missing):
    factors = []
    x = n
    d = 2
    while d * d <= x:
        while x % d == 0:
            factors.append(d)
            x //= d
        d += 1
    if x > 1:
        factors.append(x)
    is_prime = len(factors) == 1
    print(f"  n={n}: missing={inequiv_missing[n]:4d}, prime={is_prime}, factors={factors}")

# 5. n-choose-k combinatorial scaling
print("\n5. Combinatorial scaling test:")
# Total D4 solutions ~ something like O(c^n)?
for n in sorted(inequiv_data):
    total, _, _ = inequiv_data[n]
    log_total = math.log10(total)
    per_n = log_total / n
    print(f"  n={n:2d}: log10(total)={log_total:.3f}, per-n={per_n:.4f}")
