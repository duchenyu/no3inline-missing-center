#!/usr/bin/env python3
"""
D1: rot2 UNSAT at n=31 — number theory analysis.

Key question: why does rot2 go from 44,828 solutions at n=29 to ZERO at n=31?
Check number-theoretic properties of n=31 vs n=27,29,33.
"""

import os, math
from collections import defaultdict, Counter

OUT_DIR = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis'

# rot2 data from README: odd n from 7 to 33
# For n=7..19: from full enumeration (iden class includes rot2 etc.)
# For n=21..33: rot2-specific data (no .few = full enumeration)
ROT2_SOL_COUNTS = {
    7: None,    # no data
    9: None,
    11: 30,     # from Flammenkamp (3 MC out of 30)
    13: 82,
    15: 283,
    17: 281,
    19: 592,
    21: 2412,   # 190 MC
    23: 3967,   # 229 MC
    25: 8980,   # 557 MC
    27: 17332,  # 773 MC
    29: 44828,  # full enumeration
    31: 0,      # UNSAT
    33: 0,      # UNSAT
}

# Number of available pairs for rot2 at odd n = (n²-1)/2
def available_pairs(n):
    return (n * n - 1) // 2

# Constraints per variable from README
CONSTRAINTS_PER_VAR = {
    27: 68.3,
    29: 73.6,
    31: 78.9,
    33: 84.2,
}

def factorize(n):
    """Return prime factorization of n."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def analyze_odd_n(max_n=51):
    """Analyze number-theoretic properties of odd n and rot2 solvability."""
    print(f"{'='*60}")
    print("rot2 UNSAT Number Theory Analysis")
    print(f"{'='*60}")
    print()
    
    print(f"{'n':>4} {'n²-1':>8} {'avail':>8} {'factors(n)':>25} {'factors(n²-1)':>30} {'n mod':>6} {'solvable':>9}")
    print("-" * 100)
    
    for n in range(7, max_n + 1, 2):
        av = available_pairs(n)
        n_factors = factorize(n)
        nsq_factors = factorize(n * n - 1)
        
        solvable = "✅" if ROT2_SOL_COUNTS.get(n, None) != 0 else ""
        if n in ROT2_SOL_COUNTS:
            if ROT2_SOL_COUNTS[n] is None:
                solvable = "?"
            elif ROT2_SOL_COUNTS[n] > 0:
                solvable = f"✅({ROT2_SOL_COUNTS[n]:,})"
            else:
                solvable = "❌UNSAT"
        
        n_mod_4 = n % 4
        n_mod_8 = n % 8
        
        print(f"{n:>4} {n*n-1:>8} {av:>8} {str(n_factors):>25} {str(nsq_factors):>30} {n_mod_8:>6d} {solvable}")
    
    print()
    print("Key observations:")
    print("  31 = prime, 31²-1 = 960 = 2⁶×3×5")
    print("  29 = prime, 29²-1 = 840 = 2³×3×5×7")
    print("  27 = 3³, 27²-1 = 728 = 2³×7×13")
    print("  33 = 3×11, 33²-1 = 1088 = 2⁶×17")
    print()
    
    # Check: does n²-1 have too few divisors for direction availability?
    # Count distinct directions: number of (a,b) with |a|,|b| ≤ (n-1)/2, gcd=1
    print("Distinct direction counts:")
    for n in range(7, max_n + 1, 2):
        m = (n - 1) // 2
        # Count distinct reduced directions (antipodal pairs = one direction)
        dirs = set()
        center = m
        for r in range(n):
            for c in range(n):
                if r == center and c == center:
                    continue
                a = r - center
                b = c - center
                g = abs(math.gcd(a, b)) or 1
                a //= g; b //= g
                # For antipodal reduction: (a,b) and (-a,-b) are same
                if a < 0 or (a == 0 and b < 0):
                    a, b = -a, -b
                if a == 0: b = 1
                if b == 0: a = 1
                dirs.add((a, b))
        
        needed = n // 2  # half of points, since direction is shared by antipodal pair
        
        print(f"  n={n:>3}: {len(dirs):>5} distinct dirs, need {needed}, ratio={len(dirs)/needed:.2f}")
    
    # Check: is the n²-1 factorization related to the constraint density?
    print()
    print("n²-1 factorization vs constraint density:")
    for n in [27, 29, 31, 33]:
        av = available_pairs(n)
        c_per_v = CONSTRAINTS_PER_VAR.get(n, 0)
        nsq_factors = factorize(n * n - 1)
        total_constraints = int(c_per_v * av)
        print(f"  n={n}: avail={av}, c/var={c_per_v:.1f}, total~={total_constraints:,}")
        print(f"    n²-1 = {n*n-1} = {'×'.join(map(str, nsq_factors))}")


def check_halls_condition():
    """Check if the bipartite matching at n=31 has a Hall violation."""
    print(f"\n{'='*60}")
    print("Hall's condition analysis for rot2 matching")
    print(f"{'='*60}")
    
    for n in [27, 29, 31, 33]:
        m = (n - 1) // 2
        
        # For rot2 on odd n, the bipartite graph connects
        # rows [0, m] (domain rows) to columns [0, 2m]
        # Edge (r,c) exists if direction uniqueness + collinearity allows it
        
        # Count forbidden edges
        forbidden = 0
        total = (m + 1) * (2 * m + 1)
        
        # Count edges that might be blocked by collinearity
        # For now, estimate fraction of available edges
        
        # The bipartite graph is (rows 0..m) × (cols 0..2m)
        # Each edge corresponds to a domain cell (r,c)
        # The constraint comes from direction uniqueness + collinearity
        
        # Simple count
        print(f"n={n}: domain rows={m+1}, columns={2*m+1}, total cells={total}")

if __name__ == '__main__':
    analyze_odd_n(33)
    print()
    check_halls_condition()
