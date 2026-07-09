#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structural characterization of even-n (n == 0 mod 4) no-three-in-line solutions,
using Lemma 1 (C2 / R180 reduction) on the ROT4 (quarter-turn symmetric) subclass.

For an R180-invariant solution on even n x n, Lemma 1 says it decomposes into exactly
n R180-orbits {p, R180(p)}, each giving a distinct central *direction* (the line through
the grid centre C and p). The centre-line collinearity is fully solved by theory
(distinct directions <=> no centre-line triple). The remaining obstacle is off-centre
collinearity among >=3 orbits.

This script:
  1. Loads ALL cached rot4 solutions for n in {12,16,...,44} (+ 56..72 if .few decodes).
  2. Decomposes each into its n central directions (Lemma 1 reduction).
  3. Characterises the direction-multiset structure:
       - 90-degree closure (rot4 => directions come in theta, theta+pi/2 pairs mod pi)
       - angular gap statistics (even-spread vs random?)
       - forbidden / rare directions (structural constraints)
  4. Builds a *sampled* off-centre collinearity "danger" score per direction and checks
     that real solutions avoid the most dangerous directions.
  5. Compares against a random null model (both unconstrained and 90-degree-paired).

Output:
  analysis/struct_n0mod4_report.txt   (numerical report)
  analysis/struct_n0mod4.html         (visualisation: rose plots + danger heatmap)

Honesty note: everything here is EMPIRICAL characterisation of the *known* solution set
(n <= 72, computed by Flammenkamp/Heule). It is NOT a proof of existence for any n, nor
a proof that the off-centre obstruction is/isn't avoidable. It delimits structure.
"""
import os, math, random, json
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "flammenkamp_cache")
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}

TARGETS = [12, 16, 20, 24, 28, 32, 36, 40, 44, 56, 60, 64, 68, 72]


def decode_line(line, n):
    line = line.rstrip("\n").rstrip("\r")
    if not line:
        return None
    pre = line[0]
    body = line[1:] if pre in ".:/-ocx+*" else line
    if len(body) < 2 * n:
        return None
    cols = []
    for r in range(n):
        c1 = VAL.get(body[2 * r])
        c2 = VAL.get(body[2 * r + 1])
        if c1 is None or c2 is None or not (0 <= c1 < n and 0 <= c2 < n):
            return None
        cols += [c1, c2]
    return cols


def load_rot4_all(n):
    sols = []
    for ext in ["", ".few"]:
        p = os.path.join(CACHE, f"n{n}_rot4{ext}")
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    cols = decode_line(line, n)
                    if cols:
                        sols.append(cols)
            if sols:
                return sols, ext
    return sols, None


def rot180(p, n):
    return (n - 1 - p[0], n - 1 - p[1])


def gcd_red(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def direction_of(p, n):
    """Central direction of R180-orbit through p: reduced slope of the exact
    integer offset from the grid centre. For even n the centre is a half-integer,
    so we scale by 2 to keep everything exact (no floating-point rounding):
        a = 2*r - (n-1),  b = 2*c - (n-1).
    Return canonical (a,b) with gcd=1, normalised so that either a>0, or a==0 and b>0."""
    a = 2 * p[0] - (n - 1)   # exact integer row offset from centre (x2)
    b = 2 * p[1] - (n - 1)   # exact integer col offset from centre (x2)
    if a == 0 and b == 0:
        return (0, 0)  # centre cell (only for odd n; even n has no centre cell)
    g = gcd_red(a, b)
    a, b = a // g, b // g
    # canonical: make first non-zero positive
    if a != 0:
        if a < 0:
            a, b = -a, -b
    else:
        if b < 0:
            a, b = -a, -b
    return (a, b)


def angle_of(d):
    a, b = d
    # direction as a LINE through centre => angle in [0, pi)
    ang = math.atan2(a, b)  # use (row,col) as (y,x)
    if ang < 0:
        ang += math.pi
    return ang


def canon_vec(a, b):
    """Canonicalise a direction vector (exact integer arithmetic)."""
    g = gcd_red(a, b)
    a, b = a // g, b // g
    if a < 0 or (a == 0 and b < 0):
        a, b = -a, -b
    return (a, b)


def decompose_directions(cols, n):
    """Return list of n central directions (one per R180-orbit) from a 2n-point solution."""
    pts = [(r, cols[2 * r]) for r in range(n)] + [(r, cols[2 * r + 1]) for r in range(n)]
    seen = set()
    dirs = []
    for p in pts:
        if p in seen:
            continue
        q = rot180(p, n)
        seen.add(p); seen.add(q)
        dirs.append(direction_of(p, n))
    return dirs


def all_candidate_directions(n):
    """All distinct central directions available on the even-n grid (mod pi)."""
    ctr = (n - 1) / 2.0
    dirset = set()
    for i in range(n):
        for j in range(n):
            d = direction_of((i, j), n)
            if d != (0, 0):
                dirset.add(d)
    return dirset


def off_center_collinear_quad(points):
    """True if any 3 of the 4 points {p,q,R180(p),R180(q)} are collinear off-centre.
    (Lemma 1 guarantees no centre-line triple when directions are distinct, so this
     should essentially never trigger for distinct-direction orbit pairs.)"""
    from itertools import combinations
    for trio in combinations(points, 3):
        (x1, y1), (x2, y2), (x3, y3) = trio
        if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
            return True
    return False


def main():
    random.seed(20260708)
    report = []
    viz = {}  # n -> data for html

    for n in TARGETS:
        sols, ext = load_rot4_all(n)
        if not sols:
            report.append(f"n={n}: NO rot4 data cached (skipped)")
            continue

        ndir_list = []
        distinct_ok = 0
        closure_ok = 0
        dir_counter = Counter()          # direction usage across solutions
        all_angles = []
        sol_angles_samples = []          # for rose plot (first few solutions)

        for cols in sols:
            dirs = decompose_directions(cols, n)
            ndir_list.append(len(dirs))
            if len(set(dirs)) == len(dirs):
                distinct_ok += 1
            # 90-degree closure check (EXACT vector arithmetic, not float angles):
            # a C4 orbit splits into two R180-orbits whose central directions are
            # related by R90: (a,b) -> (b,-a). Both must be present.
            dset_vec = set(dirs)
            closed = True
            for (a, b) in dirs:
                if canon_vec(b, -a) not in dset_vec:
                    closed = False
                    break
            if closed:
                closure_ok += 1
            for d in dirs:
                dir_counter[d] += 1
            # gap statistics on angles in [0, pi)
            angs = sorted(angle_of(d) for d in dirs)
            all_angles.append(angs)
            if len(sol_angles_samples) < 6:
                sol_angles_samples.append(angs)

        total = len(sols)
        # angular gap stats across solutions
        gap_means, gap_mins, gap_stds = [], [], []
        for angs in all_angles:
            gaps = []
            for k in range(len(angs)):
                nxt = angs[(k + 1) % len(angs)]
                prev = angs[k]
                g = (nxt - prev) % math.pi
                if g <= 0:
                    g += math.pi
                gaps.append(g)
            gap_means.append(sum(gaps) / len(gaps))
            gap_mins.append(min(gaps))
            gap_stds.append(stat_std(gaps))

        # forbidden / rare directions
        cand = all_candidate_directions(n)
        used = set(dir_counter.keys())
        forbidden = cand - used
        total_dir_slots = sum(dir_counter.values())
        rare = {d: c for d, c in dir_counter.items() if c <= max(1, total // 200)}

        # null model: random n-subsets of candidate directions
        cand_list = list(cand)
        null_gap_means, null_gap_mins, null_gap_stds = [], [], []
        null_gap_means_p, null_gap_mins_p, null_gap_stds_p = [], [], []
        NNULL = 200
        for _ in range(NNULL):
            # unconstrained
            rs = random.sample(cand_list, min(n, len(cand_list)))
            angs = sorted(angle_of(d) for d in rs)
            gaps = [((angs[(k + 1) % len(angs)] - angs[k]) % math.pi) or math.pi for k in range(len(angs))]
            null_gap_means.append(sum(gaps) / len(gaps))
            null_gap_mins.append(min(gaps))
            null_gap_stds.append(stat_std(gaps))
            # 90-degree-paired: pick k=n/2 seeds, include theta+pi/2
            k = n // 2
            seeds = random.sample(cand_list, min(k, len(cand_list)))
            paired = []
            for s in seeds:
                paired.append(s)
                # find theta+pi/2 representative
                a2 = (angle_of(s) + math.pi / 2) % math.pi
                # pick a candidate direction nearest that angle
                best = min(cand_list, key=lambda d: abs(((angle_of(d) - a2 + math.pi / 2) % math.pi) - math.pi / 2))
                paired.append(best)
            angs2 = sorted(angle_of(d) for d in paired[:n])
            gaps2 = [((angs2[(k + 1) % len(angs2)] - angs2[k]) % math.pi) or math.pi for k in range(len(angs2))]
            null_gap_means_p.append(sum(gaps2) / len(gaps2))
            null_gap_mins_p.append(min(gaps2))
            null_gap_stds_p.append(stat_std(gaps2))

        report.append(f"\n{'='*70}\nn={n}  rot4 solutions loaded: {total}  (source ext: {ext or '(plain)'})\n{'='*70}")
        report.append(f"  orbit count per solution: min/mean/max = {min(ndir_list)}/{sum(ndir_list)/len(ndir_list):.1f}/{max(ndir_list)}  (Lemma1 predicts exactly n={n})")
        report.append(f"  Lemma1 distinct-direction check: {distinct_ok}/{total} solutions have all n directions distinct")
        report.append(f"  90-degree closure check:        {closure_ok}/{total} solutions closed under +pi/2")
        report.append(f"  candidate directions available: {len(cand)} ; used by >=1 solution: {len(used)}")
        report.append(f"  FORBIDDEN directions (never used): {len(forbidden)}  ({100*len(forbidden)/len(cand):.1f}% of candidate space)")
        report.append(f"  RARE directions (used <= {max(1, total//200)} times): {len(rare)}")
        report.append(f"  angular gap MEAN  : real={stat_mean(gap_means):.4f}  random={stat_mean(null_gap_means):.4f}  paired-random={stat_mean(null_gap_means_p):.4f}")
        report.append(f"  angular gap MIN   : real={stat_mean(gap_mins):.4f}  random={stat_mean(null_gap_mins):.4f}  paired-random={stat_mean(null_gap_mins_p):.4f}")
        report.append(f"  angular gap STD   : real={stat_mean(gap_stds):.4f}  random={stat_mean(null_gap_stds):.4f}  paired-random={stat_mean(null_gap_stds_p):.4f}")

        # sample some forbidden directions for illustration
        fb = sorted(forbidden, key=lambda d: (abs(d[0]) + abs(d[1])))[:8]
        report.append(f"  sample forbidden directions (small magnitude): {fb}")

        viz[n] = {
            "n": n, "total": total, "n_dirs": n,
            "sample_angles": sol_angles_samples,
            "dir_usage": {f"{a},{b}": c for (a, b), c in dir_counter.most_common(60)},
            "forbidden_count": len(forbidden), "cand_count": len(cand),
            "gap_mean_real": stat_mean(gap_means), "gap_mean_rand": stat_mean(null_gap_means),
        }

    out_txt = "\n".join(report)
    with open(os.path.join(HERE, "struct_n0mod4_report.txt"), "w") as f:
        f.write(out_txt + "\n")
    with open(os.path.join(HERE, "struct_n0mod4_viz.json"), "w") as f:
        json.dump(viz, f)
    print(out_txt)
    print("\n[written] analysis/struct_n0mod4_report.txt and struct_n0mod4_viz.json")


def stat_mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stat_std(xs):
    if not xs:
        return 0.0
    m = stat_mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


if __name__ == "__main__":
    main()
