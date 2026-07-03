#!/usr/bin/env python3
"""
Direction 3: The Even n Threshold
Why n=12 is the first even n with missing-center solutions
"""
from collections import Counter, defaultdict
import math

def count_rings_even(n):
    """For even n, compute distinct distance rings"""
    # For even n, center at (n/2 - 0.5, n/2 - 0.5)
    # Distance (×4) from center: d(c,r) = (2c-(n-1))² + (2r-(n-1))²
    # Squared offsets: {1², 3², ..., (n-1)²}
    sq_vals = [(2*c - (n-1))**2 for c in range(n)]
    distinct_sq = sorted(set(sq_vals))
    # All distinct sums of two squared values
    rings = set()
    ring_sizes = Counter()
    for r in range(n):
        for c in range(n):
            d = sq_vals[r] + sq_vals[c]
            rings.add(d)
            ring_sizes[d] += 1
    return len(rings), ring_sizes, distinct_sq

def count_rings_odd(n):
    """For odd n, compute distinct distance rings"""
    # For odd n, center at ((n-1)/2, (n-1)/2)
    # Distance (×2) from center: d(c,r) = (2c-(n-1))² + (2r-(n-1))²
    sq_vals = [(2*c - (n-1))**2 for c in range(n)]
    rings = set()
    ring_sizes = Counter()
    for r in range(n):
        for c in range(n):
            d = sq_vals[r] + sq_vals[c]
            rings.add(d)
            ring_sizes[d] += 1
    return len(rings), ring_sizes, sorted(set(sq_vals))

print("=" * 80)
print("Direction 3: Even n Threshold Analysis")
print("Why is n=12 the first even n with missing-center solutions?")
print("=" * 80)

print(f"\n{'n':>3} {'Type':>6} {'Rings':>6} {'MaxCap':>8} {'Need2n':>8} {'Ratio':>8} {'Flex':>8} {'Missing':>10} {'Notes':>20}")
print("-" * 80)

for n in range(2, 15):
    if n % 2 == 0:
        n_rings, ring_sizes, sq_vals = count_rings_even(n)
        ptype = "Even"
        
        # Get our computed missing-center counts
        missing_data = {2: 0, 4: 0, 6: 0, 8: 0, 10: 0, 12: 52}
        missing = missing_data.get(n, "?")
        
        max_capacity = 2 * n_rings  # max points possible (2 per ring)
        points_needed = 2 * n
        ratio = points_needed / max_capacity
        flexibility = (max_capacity - points_needed) / max_capacity * 100
        
        notes = ""
        if n_rings < n:
            notes = "n > rings — tight!"
        elif n_rings < n + 4:
            notes = f"R-n={n_rings-n}"
        elif missing == 0:
            notes = f"R-n={n_rings-n}, still 0"
        elif missing > 0:
            notes = f"R-n={n_rings-n}, FIRST missing!"
        
        print(f"{n:>3} {ptype:>6} {n_rings:>6} {max_capacity:>8} {points_needed:>8} {ratio:>8.4f} {flexibility:>7.1f}% {str(missing):>10} {notes:>20}")
    else:
        n_rings, ring_sizes, sq_vals = count_rings_odd(n)
        ptype = "Odd"
        
        missing_data = {3: 0, 5: 4, 7: 4, 9: 8, 11: 36, 13: 292}
        missing = missing_data.get(n, "?")
        
        max_capacity = 2 * n_rings
        points_needed = 2 * n
        ratio = points_needed / max_capacity
        flexibility = (max_capacity - points_needed) / max_capacity * 100
        
        notes = ""
        if n_rings < n:
            notes = "TIGHT!"
        elif missing == 0:
            notes = f"R-n={n_rings-n}"
        elif missing > 0:
            notes = f"R-n={n_rings-n}"
        
        print(f"{n:>3} {ptype:>6} {n_rings:>6} {max_capacity:>8} {points_needed:>8} {ratio:>8.4f} {flexibility:>7.1f}% {str(missing):>10} {notes:>20}")

print("\n\n=== RING STRUCTURE FOR EVEN n ===")
print("Shows how many points each distance ring has in the grid,")
print("and how many different distance values exist at each grid position.\n")

for n in [6, 8, 10, 12, 14]:
    n_rings, ring_sizes, sq_vals = count_rings_even(n)
    print(f"\nn={n} (even): {n_rings} distinct rings, {len(sq_vals)} x² values: {sq_vals}")
    
    # Ring size distribution
    size_dist = Counter()
    for d, sz in ring_sizes.items():
        size_dist[sz] += 1
    print(f"  Ring size distribution: {dict(sorted(size_dist.items()))}")
    print(f"  2n={2*n}, 2×Rings={2*n_rings}, 2n/(2R)={(2*n)/(2*n_rings):.3f}")
    
    # Show all rings sorted by size
    rings_by_size = sorted(ring_sizes.items(), key=lambda x: (-x[1], x[0]))
    for d, sz in rings_by_size[:10]:
        # Find representative cells
        cells = [(r,c) for r in range(n) for c in range(n) 
                 if (2*c-(n-1))**2 + (2*r-(n-1))**2 == d]
        x_vals = set((2*c-(n-1))**2 for r,c in cells) | set((2*r-(n-1))**2 for r,c in cells)
        print(f"    d={d:4d}: {sz:2d} points, x² values used: {sorted(x_vals)}")
    
    # What if we needed 2 points from each ring?
    print(f"  If 2 pts per ring: need {min(2*n_rings, 2*n)} slots, have {2*n} pts")
    if 2*n_rings >= 2*n:
        print(f"  -> Theoretically possible (capacity {2*n_rings} >= need {2*n})")
    else:
        print(f"  -> IMPOSSIBLE (capacity {2*n_rings} < need {2*n})")
    
    # Analyze whether the row/column structure forces collisions
    print(f"\n  Row x² assignment:")
    for r in range(n):
        x2 = (2*r - (n-1))**2
        print(f"    row {r}: x²={x2}")
    
    print(f"  Column x² assignment:")
    for c in range(n):
        x2 = (2*c - (n-1))**2
        print(f"    col {c}: x²={x2}")

print("\n\n=== KEY INSIGHT ===")
print("For even n, the distance ring capacity (2×R) grows as:")
print("  n=6:  2×6  = 12 = 2n    → max tight, must use ALL rings with 2pts each")
print("  n=8:  2×9  = 18 > 16    → capacity OK, but still 0 missing")
print("  n=10: 2×14 = 28 > 20    → capacity OK, still 0 missing")
print("  n=12: 2×19 = 38 > 24    → capacity OK, 52 missing!")
print()
print("This means the threshold is NOT just about ring count!")
print("The row/column assignment constraints also play a role.")
print()
print("For n=8: The 9 rings are structured such that any valid")
print("  2-per-row, 2-per-column assignment forces 3+ on at least one ring.")
print("  (Even though the raw capacity would allow avoiding 3+ on all rings.)")
print()
print("For n=12: The 19 rings provide ENOUGH diversity that the")
print("  row/column constraints no longer force a collision.")
