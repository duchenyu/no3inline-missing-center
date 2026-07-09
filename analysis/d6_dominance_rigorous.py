#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rigorous re-check of Empirical Fact 1 (Heavy-Direction Dominance):
  ">= 89% of all hyperedges of H_n involve at least one direction from D6."

Two notions of "hyperedge" are computed and compared:

(A) GENUINE hyperedge = orbit-triple {Oi,Oj,Ok} (3 DISTINCT orbits) such that
    at least one point from each lies on a common grid line (real higher-order
    collinearity constraint). Enumerated exactly via line grouping.

(B) LOOSE hyperedge = exactly what hypergraph_structure.py counted: for every
    orbit-triple (i<j<k), test if ANY 3 of the 6 orbit points are collinear
    (collinear3(six)). This over-counts because a collinearity between only 2
    orbits (e.g. a center-line through Oi,Oj) still flags {i,j,k} for ANY k.

We report D/L/S classification (by the 3 central directions) for both, separate
center-line vs off-centre, and characterise the non-D6 (L+S) genuine hyperedges.

Even n only: the R180 orbit central directions are all ODD vectors, so D6 is
comparable across even n. (For odd n central directions are all EVEN, so D6
membership is vacuous -> not comparable; noted, not computed.)
"""
import os, math, json, itertools
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D6 = {(1, 1), (1, -1), (3, 1), (1, 3), (3, -1), (1, -3)}
LOW_COORD = 3  # |a|<=3 and |b|<=3 (primitive) defines "low-slope"


def dir_of(p, n):
    a = 2 * p[0] - (n - 1)
    b = 2 * p[1] - (n - 1)
    g = math.gcd(a, b) or 1
    a, b = a // g, b // g
    if a < 0 or (a == 0 and b < 0):
        a, b = -a, -b
    return (a, b)


def build_orbits(n):
    seen = set()
    orbits = []          # list of (dir, [pts])
    pt2oid = {}
    pt2dir = {}
    for r in range(n):
        for c in range(n):
            p = (r, c)
            if p in seen:
                continue
            q = (n - 1 - p[0], n - 1 - p[1])
            oid = len(orbits)
            pts = [p]
            seen.add(p)
            if q != p:
                seen.add(q)
                pts.append(q)
            d = dir_of(p, n)
            for pp in pts:
                pt2oid[pp] = oid
                pt2dir[pp] = d
            orbits.append((d, pts))
    return orbits, pt2oid, pt2dir


def line_is_center(x0, y0, dx, dy, n):
    """True if the geometric center ((n-1)/2,(n-1)/2) lies on the line
    through (x0,y0) with step (dx,dy). For even n center has half-integer coords."""
    cx = (n - 1) - 2 * x0   # 2*(center_x - x0), integer
    cy = (n - 1) - 2 * y0
    if dx == 0 and dy == 0:
        return False
    if dx == 0:
        return cx == 0          # vertical line through grid point x0 == center_x
    if dy == 0:
        return cy == 0          # horizontal
    return cx * dy == cy * dx


def generate_lines(n):
    """Yield (points_on_line, is_center, (dx,dy)) for every distinct grid line
    that contains >=2 grid points."""
    pts = [(r, c) for r in range(n) for c in range(n)]
    for (x0, y0) in pts:
        # canonical primitive directions
        for dx in range(0, n):
            for dy in range(-(n - 1), n):
                if dx == 0 and dy <= 0:
                    continue
                g = math.gcd(dx, dy)
                if g != 1:
                    continue
                # walk backward to minimal point
                mx, my = x0, y0
                while True:
                    nx, ny = mx - dx, my - dy
                    if 0 <= nx < n and 0 <= ny < n:
                        mx, my = nx, ny
                    else:
                        break
                if (mx, my) != (x0, y0):
                    continue  # not the minimal point; skip
                # collect forward
                line = []
                x, y = mx, my
                while 0 <= x < n and 0 <= y < n:
                    line.append((x, y))
                    x += dx
                    y += dy
                if len(line) < 2:
                    continue
                is_c = line_is_center(mx, my, dx, dy, n)
                yield line, is_c, (dx, dy)


def classify(dirs3):
    if any(d in D6 for d in dirs3):
        return "D"
    if all(abs(a) <= LOW_COORD and abs(b) <= LOW_COORD for a, b in dirs3):
        return "L"
    return "S"


def genuine_hyperedges(n, orbits, pt2oid, pt2dir):
    m = len(orbits)
    seen = set()
    cnt_all = Counter()       # type
    cnt_center = Counter()
    cnt_off = Counter()
    nonD_examples = Counter()  # dirs3 tuple -> count, for non-D6
    for line, is_c, _ in generate_lines(n):
        oids = [pt2oid[p] for p in line]
        uniq = sorted(set(oids))
        if len(uniq) < 3:
            continue
        for a in range(len(uniq)):
            for b in range(a + 1, len(uniq)):
                for c in range(b + 1, len(uniq)):
                    t = (uniq[a], uniq[b], uniq[c])
                    if t in seen:
                        continue
                    seen.add(t)
                    d3 = (orbits[uniq[a]][0], orbits[uniq[b]][0], orbits[uniq[c]][0])
                    typ = classify(d3)
                    cnt_all[typ] += 1
                    if is_c:
                        cnt_center[typ] += 1
                    else:
                        cnt_off[typ] += 1
                    if typ != "D":
                        key = tuple(sorted(d3))
                        nonD_examples[key] += 1
    return cnt_all, cnt_center, cnt_off, nonD_examples, len(seen)


def loose_hyperedges(n, orbits):
    """Faithful replica of hypergraph_structure.analyze_structure counting."""
    m = len(orbits)
    pts_of = [o[1] for o in orbits]
    dirs_of = [o[0] for o in orbits]

    def collinear3(pts):
        for a in range(3):
            x1, y1 = pts[a]
            for b in range(a + 1, 3):
                x2, y2 = pts[b]
                for c in range(b + 1, 3):
                    x3, y3 = pts[c]
                    if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
                        return True
        return False

    cnt = Counter()
    total = 0
    for i in range(m):
        pi = pts_of[i]
        for j in range(i + 1, m):
            pj = pts_of[j]
            pij = pi + pj
            for k in range(j + 1, m):
                six = pij + pts_of[k]
                if collinear3(six):
                    total += 1
                    d3 = (dirs_of[i], dirs_of[j], dirs_of[k])
                    cnt[classify(d3)] += 1
    return cnt, total


def main():
    out = []
    rows = []
    for n in [12, 16, 20, 24, 28, 32]:
        orbits, pt2oid, pt2dir = build_orbits(n)
        cnt_all, cnt_c, cnt_off, nonD, ngen = genuine_hyperedges(n, orbits, pt2oid, pt2dir)
        tot = sum(cnt_all.values())
        rows.append((n, len(orbits), ngen, tot, dict(cnt_all), dict(cnt_c), dict(cnt_off)))
        out.append(f"\n{'='*70}\nn={n}  orbits={len(orbits)}  genuine-hyperedges={ngen:,}")
        out.append(f"  ALL   : D={cnt_all.get('D',0):,} L={cnt_all.get('L',0):,} S={cnt_all.get('S',0):,}  "
                   f"D%={100*cnt_all.get('D',0)/tot:.2f}  L%={100*cnt_all.get('L',0)/tot:.2f}  S%={100*cnt_all.get('S',0)/tot:.2f}")
        to = sum(cnt_off.values())
        out.append(f"  OFF-C : D={cnt_off.get('D',0):,} L={cnt_off.get('L',0):,} S={cnt_off.get('S',0):,}  "
                   f"D%={100*cnt_off.get('D',0)/to:.2f}  L%={100*cnt_off.get('L',0)/to:.2f}  S%={100*cnt_off.get('S',0)/to:.2f}")
        tc = sum(cnt_c.values())
        out.append(f"  CENTER: D={cnt_c.get('D',0):,} L={cnt_c.get('L',0):,} S={cnt_c.get('S',0):,}  "
                   f"D%={100*cnt_c.get('D',0)/tc:.2f}")

        # loose replica (only feasible for small n)
        if n <= 24:
            lc, ltot = loose_hyperedges(n, orbits)
            out.append(f"  LOOSE(replica) total={ltot:,}  D%={100*lc.get('D',0)/ltot:.2f}  L%={100*lc.get('L',0)/ltot:.2f}  S%={100*lc.get('S',0)/ltot:.2f}")

        # characterise non-D6 genuine hyperedges for the largest n
        if n == 32:
            out.append(f"\n  --- non-D6 genuine hyperedge direction-combinations (n=32) ---")
            out.append(f"  distinct non-D6 combos = {len(nonD)}")
            top = sorted(nonD.items(), key=lambda kv: -kv[1])[:25]
            for (d3, c) in top:
                out.append(f"    {d3}  x{c}")
            # how many are center-line vs off?
            # (recompute quickly via cnt diff already printed)
    txt = "\n".join(out)
    print(txt)

    # Save structured results
    path = os.path.join(HERE, "d6_dominance_rigorous.json")
    data = {
        "D6": [list(d) for d in D6],
        "note": "genuine = 3 distinct orbits each contributing a point to a common grid line",
        "rows": [
            {
                "n": n, "orbits": orb, "genuine_total": gt, "genuine_counted": tot,
                "all": ca, "center": cc, "offcentre": co,
            } for (n, orb, gt, tot, ca, cc, co) in rows
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n[written] {path}")


if __name__ == "__main__":
    main()
