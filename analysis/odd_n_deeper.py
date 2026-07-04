"""
Deeper analysis of odd n structure:
1. Sum-of-two-squares representations per ring (determines ring population)
2. d^2 mod 4 parity classes
3. Why 4k+1 vs 4k+3 determines missing-center abundance
4. Predictive conjecture for odd n ≥ 21
"""
from collections import Counter, defaultdict
import math

# ================================================================
# PART 1: Sum of Two Squares — the Fundamental Driver
# ================================================================
print("=" * 100)
print("PART 1: Sum-of-Two-Squares Ring Populations — The Fundamental Driver")
print("=" * 100)
print("""
For odd n=2m+1, offsets from center: {-m,...,m}. 
d^2 = a^2 + b^2 where |a|,|b| ≤ m.

Ring population = number of distinct (|a|,|b|) pairs with a^2+b^2 = d^2,
multiplied by symmetry: 8 for off-axis (a≠0,b≠0,a≠b), 4 for axes/diagonals, 1 for center.
""")

for n in [7, 9, 11, 13, 15, 17, 19]:
    m = (n-1)//2
    center = m
    
    # All possible squared offsets
    sq_offsets = [a*a for a in range(-m, m+1)]  # 0, 1, 4, 9, ..., m^2
    sq_set = set(sq_offsets)
    
    # For each d^2, count representations
    d2_repr = defaultdict(list)
    for a in range(-m, m+1):
        for b in range(-m, m+1):
            d2 = a*a + b*b
            d2_repr[d2].append((a, b))
    
    # Classify by (|a|,|b|) type
    d2_pop = {}  # d2 -> population
    d2_type = {}  # d2 -> classification
    for d2, reps in sorted(d2_repr.items()):
        unique_abs = set()
        for a, b in reps:
            unique_abs.add((abs(a), abs(b)))
        
        pop = len(reps)  # total points on this ring
        
        # Count by sub-type
        center_pts = sum(1 for (a,b) in reps if a==0 and b==0)
        axis_pts = sum(1 for (a,b) in reps if (a==0) != (b==0))
        diag_pts = sum(1 for (a,b) in reps if a!=0 and b!=0 and abs(a)==abs(b))
        off_pts = sum(1 for (a,b) in reps if a!=0 and b!=0 and abs(a)!=abs(b))
        
        d2_pop[d2] = pop
        d2_type[d2] = {
            'center': center_pts,
            'axis': axis_pts,
            'diag': diag_pts,
            'off_axis': off_pts,
            'total': pop,
            'mod4': d2 % 4
        }
    
    # Statistics
    mod4_dist = Counter()
    pop_dist = Counter()
    for d2, info in d2_type.items():
        mod4_dist[info['mod4']] += 1
        pop_dist[info['total']] += 1
    
    print(f"\nn={n} (m={m}): {len(d2_type)} rings")
    print(f"  d^2 mod 4 distribution: {dict(sorted(mod4_dist.items()))}")
    print(f"  Population distribution: {dict(sorted(pop_dist.items()))}")
    
    # Key: mod4=0 rings come from even-even coordinates
    # mod4=2 rings come from odd-odd coordinates
    # mod4=1 rings come from mixed coordinates
    
    # The center (d^2=0) is mod4=0
    center_info = d2_type.get(0, {})
    print(f"  Center ring (d^2=0): {center_info.get('total', 0)} points ({center_info.get('center', 0)} center, {center_info.get('axis', 0)} axis)")
    
    # Largest and smallest rings
    sorted_pops = sorted(d2_pop.items(), key=lambda x: x[1])
    print(f"  Smallest: {sorted_pops[:3]}")
    print(f"  Largest:  {sorted_pops[-3:]}")

# ================================================================
# PART 2: The 4k+1 vs 4k+3 Structural Difference
# ================================================================
print("\n" + "=" * 100)
print("PART 2: 4k+1 vs 4k+3 — The Parity Effect")
print("=" * 100)
print("""
n=4k+1 → m=2k (even)  → even-even: (m+1)^2 points, odd-odd: m^2 points
n=4k+3 → m=2k+1 (odd) → even-even: (m+1)^2 points, odd-odd: m^2 points

But for 4k+3, m+1 is even, so even-even points are a SUBSQUARE of the full grid.
For 4k+1, m is even, so odd-odd points are a SUBSQUARE.

The key metric: what fraction of points are in MOD4=0 rings (even-even)?
This determines how many points are "innate" to the center-circumcenter structure.
""")

for k in range(1, 6):
    n1 = 4*k + 1  # 4k+1
    n3 = 4*k + 3  # 4k+3
    
    for n, label in [(n1, f"4k+1 (n={n1})"), (n3, f"4k+3 (n={n3})")]:
        if n > 30:
            continue
        m = (n-1)//2
        total = n * n
        
        # Even-even: both coordinates even offset from center
        # Count: how many i,j in [0,n-1] have (i-m) even and (j-m) even?
        even_even = 0
        odd_odd = 0
        mixed = 0
        for i in range(n):
            for j in range(n):
                a, b = i-m, j-m
                if a % 2 == 0 and b % 2 == 0:
                    even_even += 1
                elif a % 2 == 1 and b % 2 == 1:
                    odd_odd += 1
                else:
                    mixed += 1
        
        even_ratio = even_even / total * 100
        
        # Points entirely on "even-even" subgrid (d^2 ≡ 0 mod 4)
        # These rings are "self-contained" — they can be analyzed separately
        print(f"{label}: m={m:2d}, total={total:3d}, "
              f"even-even={even_even:3d} ({even_ratio:.0f}%), "
              f"odd-odd={odd_odd:3d} ({odd_odd/total*100:.0f}%), "
              f"mixed={mixed:3d} ({mixed/total*100:.0f}%)")

# ================================================================  
# PART 3: Subgrid Structure
# ================================================================
print("\n" + "=" * 100)
print("PART 3: Subgrid Constraints — the Missing-Center Game")
print("=" * 100)
print("""
For odd n, the grid splits into 3 subgrids by parity:
  GG: even-even (d^2 ≡ 0 mod 4) — (m+1)^2 pts for 4k+1, (m+1)^2 for 4k+3
  BB: odd-odd   (d^2 ≡ 2 mod 4) — m^2 pts
  GB: mixed     (d^2 ≡ 1 mod 4) — 2m(m+1) pts

The missing-center constraint only restricts that no single ring has ≥3 points.
Since GG and BB rings are disjoint from mixed rings by mod, each subgrid
has its own ring structure that interacts through COLLINEARITY only.
""")

for n in range(3, 21, 2):
    m = (n-1)//2
    n_pts = 2*n
    
    # Even-even subgrid ring analysis
    gg_points = []
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            if a % 2 == 0 and b % 2 == 0:
                gg_points.append((i,j,a,b))
    
    gg_rings = Counter()
    for i,j,a,b in gg_points:
        d2 = a*a + b*b
        gg_rings[d2] += 1
    
    # Odd-odd subgrid
    bb_points = []
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            if a % 2 == 1 and b % 2 == 1:
                bb_points.append((i,j,a,b))
    
    bb_rings = Counter()
    for i,j,a,b in bb_points:
        d2 = a*a + b*b
        bb_rings[d2] += 1
    
    # Mixed subgrid
    gb_points = []
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            if (a % 2 == 0) != (b % 2 == 0):
                gb_points.append((i,j,a,b))
    
    gb_rings = Counter()
    for i,j,a,b in gb_points:
        d2 = a*a + b*b
        gb_rings[d2] += 1
    
    # Capacity of each subgrid (max pts without center in subgrid)
    gg_cap = sum(min(v, 2) for v in gg_rings.values())
    bb_cap = sum(min(v, 2) for v in bb_rings.values())
    gb_cap = sum(min(v, 2) for v in gb_rings.values())
    total_cap = gg_cap + bb_cap + gb_cap
    
    gg_ge3 = sum(1 for v in gg_rings.values() if v >= 3)
    bb_ge3 = sum(1 for v in bb_rings.values() if v >= 3)
    gb_ge3 = sum(1 for v in gb_rings.values() if v >= 3)
    
    print(f"\nn={n} (4k+{n%4}):")
    print(f"  GG (d^2≡0): {len(gg_rings):2d} rings, {len(gg_points):3d} pts, cap={gg_cap:3d}, {gg_ge3} dangerous")
    print(f"  BB (d^2≡2): {len(bb_rings):2d} rings, {len(bb_points):3d} pts, cap={bb_cap:3d}, {bb_ge3} dangerous")
    print(f"  GB (d^2≡1): {len(gb_rings):2d} rings, {len(gb_points):3d} pts, cap={gb_cap:3d}, {gb_ge3} dangerous")
    print(f"  Total capacity (2/ring): {total_cap} (need {n_pts}) → surplus {total_cap - n_pts}")

# ================================================================
# PART 4: Concrete Prediction for n=21 and beyond
# ================================================================
print("\n" + "=" * 100)
print("PART 4: Predictions for Larger Odd n")
print("=" * 100)
print("""
Based on the identified patterns, we can predict:

1. n=21 (4k+1, composite 3×7): 
   - Ring pairs ≈ 1275+(51+53) ≈ ??? (let's compute)
   - 4k+1 → mod4=0 rings > mod4=2 rings
   - COMPOSITE → should have MORE missing than adjacent primes
   
2. n=23 (4k+3, prime):
   - 4k+3 → mod4=2 rings > mod4=0 rings  
   - PRIME → fewer missing than adjacent composites

3. n=25 (4k+1, perfect square):
   - Largest n before 71 that's a perfect square
   - Square → may behave anomalously
""")

for n in [21, 23, 25, 27, 29]:
    m = (n-1)//2
    
    # Ring pairs
    all_rings = Counter()
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            d2 = a*a + b*b
            all_rings[d2] += 1
    
    num_rings = len(all_rings)
    pairs = num_rings * (num_rings - 1) // 2
    
    # Parity subgrids
    gg = bb = gb = 0
    gg_rings = Counter()
    bb_rings = Counter()
    gb_rings = Counter()
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            d2 = a*a + b*b
            if a%2==0 and b%2==0:
                gg += 1
                gg_rings[d2] += 1
            elif a%2==1 and b%2==1:
                bb += 1
                bb_rings[d2] += 1
            else:
                gb += 1
                gb_rings[d2] += 1
    
    gg_cap = sum(min(v,2) for v in gg_rings.values())
    bb_cap = sum(min(v,2) for v in bb_rings.values())
    gb_cap = sum(min(v,2) for v in gb_rings.values())
    total_cap = gg_cap + bb_cap + gb_cap
    
    # Mod4 distribution
    mod4_dist = Counter(v % 4 for v in all_rings.keys())
    
    m_parity = "even" if m % 2 == 0 else "odd"
    n_form = f"4k+{n%4}"
    is_prime_raw = all(n % d != 0 for d in range(2, int(n**0.5)+1))
    is_prime_flag = "PRIME" if is_prime_raw else f"composite={next(d for d in range(2,int(n**0.5)+1) if n%d==0)}"
    if n == 1: is_prime_flag = "unit"
    
    print(f"\nn={n:2d} ({n_form}): m={m} ({m_parity}), {is_prime_flag}")
    print(f"  Rings: {num_rings} ({pairs} pairs)")
    print(f"  Mod4 dist: {dict(mod4_dist)}")
    print(f"  GG={gg}({gg_cap}) BB={bb}({bb_cap}) GB={gb}({gb_cap}) | Total cap={total_cap} need={2*n} | surplus={total_cap-2*n}")
    
    # Prediction
    ring_pair_density = pairs / (2*n)  # pairs per needed point
    print(f"  Ring-pair per point: {ring_pair_density:.1f}")
    
    # Composite boost factor (rough heuristic)
    composite_boost = 1.0
    if not is_prime_raw:
        composite_boost = 1.5  # rough
    
    mod_boost = 1.0
    if n % 4 == 3:
        mod_boost = 1.2  # 4k+3 slightly higher
    
    predicted_base = 0.05 * 2 * n  # ~5% of needed points
    print(f"  Estimated missing-center range: ~{int(predicted_base * composite_boost * mod_boost)}-{int(predicted_base * composite_boost * mod_boost * 10)}")
