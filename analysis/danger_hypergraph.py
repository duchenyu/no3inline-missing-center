#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Faithful conflict object for the Lemma-1-reduced even-n no-three-in-line problem.

The pairwise orbit conflict graph is (provably) almost empty: two distinct central
directions never create an off-centre collinear triple among their 4 orbit points
(Lemma 1 rules out centre-line triples; distinct directions => no other triple is
collinear). So the real obstruction is HIGHER-ORDER: a triple of directions can be
mutually incompatible even though every pair is fine.

This script builds the 3-uniform *off-centre collinearity hypergraph* on the direction
space:
    hyperedge {d_i, d_j, d_k}  <=>  there exist R180-orbits O_i,O_j,O_k with those
                                     central directions whose 6 points contain an
                                     off-centre collinear triple.
and derives, per direction, a DANGER degree = # forbidden triples it participates in.

We then check (a) known solutions are independent sets (sanity), and (b) whether a
solution's directions have LOWER mean danger than a random n-subset (structural
avoidance of dangerous directions).

Scope: n in {12,16,20} (orbit counts 72/128/200 => triple enumeration tractable in
Python; ~1.3M triples at n=20). Larger n need the C++/GPU port (see Task #72).

Output: analysis/danger_hypergraph_report.txt
"""
import os, math, random, itertools
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "flammenkamp_cache")
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}
TARGETS = [12, 16, 20]


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
        c1 = VAL.get(body[2 * r]); c2 = VAL.get(body[2 * r + 1])
        if c1 is None or c2 is None or not (0 <= c1 < n and 0 <= c2 < n):
            return None
        cols += [c1, c2]
    return cols


def load_rot4_all(n):
    for ext in ["", ".few"]:
        p = os.path.join(CACHE, f"n{n}_rot4{ext}")
        if os.path.exists(p):
            out = []
            with open(p) as f:
                for line in f:
                    c = decode_line(line, n)
                    if c:
                        out.append(c)
            if out:
                return out
    return []


def r180(p, n):
    return (n - 1 - p[0], n - 1 - p[1])


def dir_of(p, n):
    a = 2 * p[0] - (n - 1); b = 2 * p[1] - (n - 1)
    g = math.gcd(a, b) or 1; a, b = a // g, b // g
    if a < 0 or (a == 0 and b < 0):
        a, b = -a, -b
    return (a, b)


# DEPRECATED: original collinear3 iterated only range(3) over the 6-point list,
# checking only (p_i,q_i,p_j). That bug fabricated the ">=89% D6 dominance"
# claim (see analysis/d6_dominance_correction.md). Fixed to check ALL 6 points,
# but the "loose" hyperedge notion still over-counts bystander triples; the
# correct constraint is the GENUINE hyperedge in d6_dominance_rigorous.py.
def collinear3(pts):
    n = len(pts)
    for a in range(n):
        x1, y1 = pts[a]
        for b in range(a + 1, n):
            x2, y2 = pts[b]
            for c in range(b + 1, n):
                x3, y3 = pts[c]
                if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
                    return True
    return False


def build_orbits(n):
    """All R180-orbits on the even-n grid, each as (dir, (p, q))."""
    seen = set(); orbits = []
    for r in range(n):
        for c in range(n):
            p = (r, c)
            if p in seen:
                continue
            q = r180(p, n)
            seen.add(p); seen.add(q)
            orbits.append((dir_of(p, n), (p, q)))
    return orbits


def main():
    random.seed(20260708)
    out = []
    for n in TARGETS:
        sols = load_rot4_all(n)
        orbits = build_orbits(n)
        m = len(orbits)
        # enumerate orbit triples, test off-centre collinearity
        forbidden_triples = 0
        danger = Counter()  # direction -> # forbidden triples containing it
        total = 0
        # precompute point pairs
        pts_of = [o[1] for o in orbits]
        dirs_of = [o[0] for o in orbits]
        for i in range(m):
            p_i = pts_of[i]
            for j in range(i + 1, m):
                p_j = pts_of[j]
                for k in range(j + 1, m):
                    p_k = pts_of[k]
                    total += 1
                    six = p_i + p_j + p_k
                    if collinear3(six):
                        forbidden_triples += 1
                        for d in (dirs_of[i], dirs_of[j], dirs_of[k]):
                            danger[d] += 1
        total_triples = total
        forb_frac = forbidden_triples / total_triples if total_triples else 0
        out.append(f"\n{'='*68}\nn={n}  orbits={m}  solutions-loaded={len(sols)}")
        out.append(f"  orbit-triples tested     : {total_triples:,}")
        out.append(f"  FORBIDDEN triples (off-centre collinear): {forbidden_triples:,}  ({100*forb_frac:.2f}% of all triples)")
        out.append(f"  distinct directions with danger>0: {sum(1 for d in danger if danger[d]>0)} / {m}")
        if danger:
            degs = list(danger.values())
            mean_d = sum(degs)/len(degs)
            max_d = max(degs)
            out.append(f"  danger-degree: mean={mean_d:.1f}  max={max_d}  (over directions that appear)")
            # most dangerous directions
            top = sorted(danger.items(), key=lambda kv: -kv[1])[:6]
            out.append(f"  most dangerous directions: {[(d,c) for d,c in top]}")
        # sanity: each known solution's direction-set must be an independent set
        indep_ok = 0
        sol_mean_danger = []
        for cols in sols:
            pts = [(r, cols[2*r]) for r in range(n)] + [(r, cols[2*r+1]) for r in range(n)]
            seen = set(); dsol = []
            for p in pts:
                if p in seen: continue
                q = r180(p, n); seen.add(p); seen.add(q)
                dsol.append(dir_of(p, n))
            # independent set check via orbit lookup
            orb_dir_index = {d: idx for idx, (d, _) in enumerate(orbits)}
            idxs = [orb_dir_index[d] for d in dsol]
            bad = False
            for a in range(len(idxs)):
                for b in range(a+1, len(idxs)):
                    for c in range(b+1, len(idxs)):
                        if collinear3(pts_of[idxs[a]] + pts_of[idxs[b]] + pts_of[idxs[c]]):
                            bad = True; break
                        if bad: break
                    if bad: break
                if bad: break
            if not bad:
                indep_ok += 1
            sol_mean_danger.append(sum(danger[d] for d in dsol) / len(dsol))
        out.append(f"  known solutions that are independent sets: {indep_ok}/{len(sols)} (must be all)")
        if sol_mean_danger:
            out.append(f"  solution mean-danger: {sum(sol_mean_danger)/len(sol_mean_danger):.2f}")
        # random n-subset mean danger (null model)
        orb_idx_by_dir = {}
        for idx, d in enumerate(dirs_of):
            orb_idx_by_dir.setdefault(d, []).append(idx)
        rand_means = []
        for _ in range(50):
            chosen = random.sample(range(m), n)
            dm = sum(danger[dirs_of[idx]] for idx in chosen) / n
            rand_means.append(dm)
        out.append(f"  RANDOM n-subset mean-danger: {sum(rand_means)/len(rand_means):.2f}  (solution should be <= this if it avoids danger)")
    txt = "\n".join(out)
    with open(os.path.join(HERE, "danger_hypergraph_report.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)
    print("\n[written] analysis/danger_hypergraph_report.txt")


if __name__ == "__main__":
    main()
