"""
Part 3: Conjecture Synthesis — A Unified Theory of Odd n Missing-Center Abundance

Three interacting factors control the missing-center count:
1. m parity (m even=4k+1, m odd=4k+3)
2. Composite vs prime
3. Ring-pair collinearity density (quadratic in ring count)
"""
from collections import Counter

# D4-inequivalent missing-center data
missing_data = {
    7: 1, 9: 1, 11: 6, 13: 46, 15: 354, 17: 357, 19: 2363
}

total_data = {
    7: 22, 9: 51, 11: 158, 13: 499, 15: 3978, 17: 7094, 19: 32577
}

print("=" * 100)
print("CONJECTURE: Odd n Missing-Center Abundance Formula")
print("=" * 100)
print()

# Compute ring count for each n
ring_counts = {}
for n in range(7, 20, 2):
    m = (n-1)//2
    all_d2 = set()
    for i in range(n):
        for j in range(n):
            a, b = i-m, j-m
            d2 = a*a + b*b
            all_d2.add(d2)
    ring_counts[n] = len(all_d2)

print("Factor 1: m parity (4k+1 vs 4k+3)")
print("-" * 60)
print(f"{'n':>3} {'m':>3} {'Parity':>8} {'Rings':>6} {'Missing':>8} {'Rate%':>6}")
for n in sorted(missing_data):
    m = (n-1)//2
    par = "even" if m % 2 == 0 else "odd"
    rate = missing_data[n] / total_data[n] * 100
    print(f"{n:>3} {m:>3} {par:>8} {ring_counts[n]:>6} {missing_data[n]:>8} {rate:>5.1f}%")

print()
print("Factor 2: Composite vs Prime")
print("-" * 60)
for n in sorted(missing_data):
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
    par = "4k+1" if n % 4 == 1 else "4k+3"
    print(f"n={n} ({par}): missing={missing_data[n]:4d}, prime={is_prime}, factors={factors}")

print()
print("Factor 3: Ring-pair Collinearity Density")
print("-" * 60)
prev = None
for n in sorted(missing_data):
    r = ring_counts[n]
    pairs = r * (r - 1) // 2
    density = pairs / (2 * n)  # ring-pairs per point needed
    if prev:
        growth = missing_data[n] / prev
        print(f"n={n}: rings={r:2d}, {pairs:4d} pairs, density/point={density:.1f}, missing growth={growth:.1f}x")
    else:
        print(f"n={n}: rings={r:2d}, {pairs:4d} pairs, density/point={density:.1f}")
    prev = missing_data[n]

print()
print("=" * 100)
print("THE CONJECTURE")
print("=" * 100)
print("""
The missing-center count M(n) for odd n follows:

  M(n) ∝ exp(α · n) · (composite_boost)^(is_composite) · (parity_factor)^(n_mod_4)

Where:
  - α ≈ 0.4-0.5 (base exponential growth rate from ring-pair density)
  - composite_boost ≈ 2-5 (composite n have more missing)
  - parity_factor ≈ 0.8 (4k+1) vs 1.2 (4k+3) ??? (needs more data)

But this is IMPRECISE because the ring-pair collinearity is a threshold effect,
not a smooth function. The 15→17 freeze suggests a "geometric resonance" where
certain n values have nearly identical effective constraint density despite
different grid sizes.

Prediction for n=21 (4k+1, composite=3): abundant missing-center
Prediction for n=23 (4k+3, prime): growth resumes
Prediction for n=25 (4k+1, perfect square, composite=5): very abundant
Prediction for n=29 (4k+1, prime): growth pause similar to n=17??
""")

# More precise: compute expected ratio
print()
print("Rate relative to n-2 neighbor:")
for n in sorted(missing_data):
    if n > 7:
        prev_n = n - 2
        if prev_n in missing_data:
            ratio = missing_data[n] / missing_data[prev_n]
            rate_diff = (missing_data[n]/total_data[n]) - (missing_data[prev_n]/total_data[prev_n])
            print(f"  n={prev_n}→{n}: missing ×{ratio:.1f}, rate change {rate_diff:+.1f}%")
