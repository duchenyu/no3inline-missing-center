#!/usr/bin/env python3
"""
D1-v2: Formalize the v₂-based Hall obstruction for rot2 UNSAT at n=31.

Key insight: for rot2 on odd n = 2m+1, each direction (a,b) is available to
exactly floor(m / max(a,|b|)) domain rows. The question is whether the
bipartite b-matching (each row needs 2, each direction used ≤1) has a
Hall violation at m=15 (n=31) that doesn't exist at m=14 (n=29).
"""
import os, math, json
from collections import defaultdict, Counter

OUT_DIR = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis'

def enumerate_directions(m):
    """Enumerate all reduced directions for rot2 on n = 2m+1."""
    dirs = set()
    for r in range(-m, m + 1):
        for c in range(-m, m + 1):
            if r == 0 and c == 0:
                continue
            g = abs(math.gcd(r, c)) or 1
            a, b = r // g, c // g
            # Normalize: a ≥ 0, and (a=0 => b > 0)
            if a < 0 or (a == 0 and b < 0):
                a, b = -a, -b
            dirs.add((a, b))
    return dirs

def build_availability(m):
    """
    Build the bipartite graph: for each direction, which rows can use it.
    Row r ∈ [0, m], direction d = (a,b).
    
    Cell (r,c) produces direction (a,b) if:
      normalize(r-m, c-m) = (a,b)
    i.e., r-m = a·g, c-m = b·g for some g ≥ 1
    So r = m - a·g (since a > 0 means r = m - a·g to keep r < m)
    Wait, r = m + a·g where a = r-m. For a ≥ 0:
    a = m - r (for r < m), so r = m - a.
    
    Actually: a = normalize(r-m, c-m). The first component is |r-m|/gcd.
    For r ≤ m: first component = (m-r)/gcd(m-r, |c-m|).
    
    A direction (a,b) is available to row r if there exists c such that:
      a = (m-r)/gcd(m-r, c-m)  and  b = (c-m)/gcd(m-r, c-m)
    
    This means: m-r = a·g, c-m = b·g for some g ≥ 1.
    So r = m - a·g and c = m + b·g.
    We need: r ≥ 0 (row in domain), c ∈ [0, 2m] (column in range).
    
    For a ≥ 0, r = m - a·g ≥ 0 ⇒ g ≤ m/a (if a > 0).
    For b any sign, c = m + b·g ∈ [0, 2m] ⇒ -m ≤ b·g ≤ m ⇒ g ≤ m/|b| (for b ≠ 0).
    
    So g ranges from 1 to min(⌊m/a⌋, ⌊m/|b|⌋) for a > 0, b ≠ 0.
    """
    avail = {}  # direction -> list of (r, g) pairs
    
    for a in range(0, m + 1):
        for b in range(-m, m + 1):
            if a == 0 and b == 0:
                continue
            # Normalize
            g0 = abs(math.gcd(a, b)) or 1
            a0, b0 = a // g0, b // g0
            if a0 < 0 or (a0 == 0 and b0 < 0):
                a0, b0 = -a0, -b0
            
            if (a0, b0) not in avail:
                avail[(a0, b0)] = []
            
            # This cell produces reduced direction (a0, b0)
            # only if (a,b) = (a0·g, b0·g) for some g
            # i.e., g must divide both a and b
            # But we're iterating over all (a,b) directly
    
    # Actually, let me reconsider. The cells are (r,c) in the domain.
    # Direction of cell (r,c): normalize(r-m, c-m).
    # The normalized direction is (a,b). Then r = m - a·g for some g.
    # Given a direction (a,b), which rows can produce it?
    
    avail = defaultdict(list)
    for a in range(0, m + 1):
        for b in range(-m, m + 1):
            if a == 0 and b == 0:
                continue
            g0 = abs(math.gcd(a, b)) or 1
            a0, b0 = a // g0, b // g0
            if a0 < 0 or (a0 == 0 and b0 < 0):
                a0, b0 = -a0, -b0
            if a0 == 0 and b0 == 1:
                continue   # direction (0,1) reserved for center row
            
            # For this direction (a0,b0), which rows can produce it?
            # We need: r = m - a0·g where g ≥ 1
            # And r ≥ 0, so g ≤ m/a0
            # Also c = m + b0·g must be in [0, 2m], so g ≤ m/|b0|
            
            if a0 > 0 and b0 != 0:
                max_g = min(m // a0, m // abs(b0))
            elif a0 > 0 and b0 == 0:
                max_g = m // a0  # c = m, c-m = 0, b0 = 0
            else:
                continue  # a0=0 already handled
            
            rows = []
            for g in range(1, max_g + 1):
                r = m - a0 * g
                if r >= 0:
                    rows.append((r, g))
            
            if rows:
                avail[(a0, b0)] = rows
    
    return avail

def analyze_hall(m):
    """Check Hall's condition for the rot2 b-matching."""
    avail = build_availability(m)
    
    # Enumerate all directions
    all_dirs = list(avail.keys())
    
    # For each row, collect available directions
    row_to_dirs = defaultdict(list)
    for d, rows in avail.items():
        for r, g in rows:
            row_to_dirs[r].append(d)
    
    direction_pool = len(all_dirs)
    needed = m + 1 - 1 + 2 * m  # center row needs 1, non-center rows need 2 each
    # Actually: center row (r=m) needs 1 antipodal pair = 1 direction
    # Non-center rows (r=0..m-1) each need 2 directions
    needed_center = 1  # direction (0,1) for center row
    needed_noncenter = 2 * m  # 2 directions per non-center row
    needed_total = needed_center + needed_noncenter  # = 2m+1 = n
    
    print(f"\n{'='*60}")
    print(f"m={m} (n={2*m+1}): Hall Analysis")
    print(f"{'='*60}")
    print(f"Total directions (excl (0,1)): {direction_pool}")
    print(f"Needed: {needed_total} ({needed_center} center + {needed_noncenter} non-center)")
    
    # Check per-row availability
    print(f"\nPer-row direction availability:")
    min_avail = float('inf')
    max_avail = 0
    for r in range(m):  # non-center rows
        nd = len(row_to_dirs.get(r, []))
        min_avail = min(min_avail, nd)
        max_avail = max(max_avail, nd)
        if nd < 2:
            print(f"  Row {r}: ⚠️ ONLY {nd} directions available (< 2 needed)")
    
    center_avail = len(row_to_dirs.get(m, []))
    print(f"  Center row {m}: {center_avail} directions avail (only (0,1) usable)")
    print(f"  Non-center rows: min={min_avail}, max={max_avail}")
    
    # Check for rows with very few directions
    scarce_rows = [r for r in range(m) if len(row_to_dirs.get(r, [])) < 2]
    if scarce_rows:
        print(f"\n❌ HALL VIOLATION: {len(scarce_rows)} rows have < 2 directions!")
        for r in scarce_rows[:10]:
            dirs = row_to_dirs.get(r, [])
            print(f"  Row {r}: only {len(dirs)} dirs: {sorted(dirs)[:10]}")
    
    # Check: for a subset S of rows, is |N(S)| ≥ 2|S|?
    # We need to check the most constrained subsets
    # The most constrained are likely the highest rows (smallest r)
    for subset_size in [1, 2, 3, 5, 10, m//2, m]:
        if subset_size > m:
            continue
        # Check the top `subset_size` rows (r = 0..subset_size-1)
        top_rows = list(range(subset_size))
        neighbor_dirs = set()
        for r in top_rows:
            for d in row_to_dirs.get(r, []):
                neighbor_dirs.add(d)
        
        demand = subset_size * 2  # each needs 2
        supply = len(neighbor_dirs)
        slack = supply - demand
        if slack < 0:
            print(f"  ❌ HALL: top {subset_size} rows need {demand}, share {supply} dirs (deficit={-slack})")
        elif slack < subset_size:
            print(f"  ⚠️ TIGHT: top {subset_size} rows need {demand}, share {supply} dirs (slack={slack})")
    
    # v₂ analysis
    mm1 = m * (m + 1)
    v2 = 0
    temp = mm1
    while temp % 2 == 0:
        v2 += 1
        temp //= 2
    
    print(f"\n  v₂(m(m+1)) = v₂({mm1}) = {v2}")
    
    # Check parity of directions
    even_a = sum(1 for d in all_dirs if d[0] % 2 == 0 and d[0] > 0)
    odd_a = sum(1 for d in all_dirs if d[0] % 2 == 1)
    print(f"  Even-a dirs: {even_a}, Odd-a dirs: {odd_a}")
    
    return {
        'm': m,
        'n': 2*m+1,
        'direction_pool': direction_pool,
        'needed': needed_total,
        'min_avail_per_row': min_avail,
        'hall_deficit': slack if subset_size == m else None,
        'v2': v2,
        'even_a_dirs': even_a,
    }

print("=" * 60)
print("rot2 Hall Condition Analysis — v₂ Connection")
print("=" * 60)

for m in [12, 13, 14, 15, 16, 17]:
    analyze_hall(m)

# Also test some larger m values
print(f"\n{'='*60}")
print("Extended predictions")
for m in [18, 20, 22, 24, 30]:
    mm1 = m * (m + 1)
    v2 = 0
    temp = mm1
    while temp % 2 == 0:
        v2 += 1
        temp //= 2
    avail = build_availability(m)
    all_dirs = list(avail.keys())
    even_a = sum(1 for d in all_dirs if d[0] % 2 == 0 and d[0] > 0)
    odd_a = sum(1 for d in all_dirs if d[0] % 2 == 1)
    print(f"m={m:>3} (n={2*m+1:>3}): v₂={v2:>2}, dirs={len(all_dirs):>5}, even_a={even_a:>4}, odd_a={odd_a:>4}")
