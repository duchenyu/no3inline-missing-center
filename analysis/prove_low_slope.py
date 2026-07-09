#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算机辅助证明：低斜率空性 + 危险方向集中性（H_n^dir 模型, 见 hypergraph_framework.md Model 1）

顶点 = 中心方向 d=(a,b) 本原向量, gcd=1, 规范化半平面 (a>0 或 a=0,b>0)
超边 = 三元组 {d1,d2,d3} 使得存在正整数 k1,k2,k3,
       点 P_i = k_i d_i 在 n×n 网格内(离心) 且三点共线。

共线判别式（直接推导）:
  c12=det(d1,d2), c23=det(d2,d3), c13=det(d1,d3)
  k1*k2*c12 + k2*k3*c23 = k1*k3*c13   <=>   k2 = k1*k3*c13/(k1*c12 + k3*c23) (正整数)

网格约束: k_i*max(|a_i|,|b_i|) <= (n-1)/2  =>  三元组成为超边的最小 n = 2*E+1,
  E = min_{整数解} max_i(k_i * maxcomp_i).

"H_n[L] 空" <=> 对所有 L 三元组 2*E(triple)+1 > n  <=> n <= 2*min_L E  (有限可证, 非采样).
"""
import math
import numpy as np
from itertools import combinations

D6 = {(1, 1), (1, -1), (3, 1), (3, -1), (1, 3), (1, -3)}

def dirs(B):
    D = []
    for a in range(0, B + 1):
        for b in range(-B, B + 1):
            if a == 0 and b <= 0:
                continue
            if a < 0:
                continue
            if math.gcd(a, b) != 1:
                continue
            D.append((a, b))
    return D

def min_extent_np(d1, d2, d3, KMAX=200):
    a1, b1 = d1; a2, b2 = d2; a3, b3 = d3
    c12 = a1 * b2 - a2 * b1
    c23 = a2 * b3 - a3 * b2
    c13 = a1 * b3 - a3 * b1
    m1, m2, m3 = max(abs(a1), abs(b1)), max(abs(a2), abs(b2)), max(abs(a3), abs(b3))
    k1 = np.arange(1, KMAX + 1)
    k3 = np.arange(1, KMAX + 1)
    K1, K3 = np.meshgrid(k1, k3, indexing='ij')
    num = K1 * K3 * c13
    den = K1 * c12 + K3 * c23
    valid = (den != 0) & (num % den == 0) & (num // den > 0)
    if not valid.any():
        return None
    k2 = num // den
    E = np.maximum(np.maximum(K1 * m1, K3 * m3), k2 * m2)
    E = np.where(valid, E, np.inf)
    return int(E.min())

def analyze(B, exclude_D6=False, KMAX=200, label=""):
    D = dirs(B)
    if exclude_D6:
        D = [d for d in D if d not in D6]
    print(f"\n=== {label}: B={B}, |dirs|={len(D)} ===")
    triples = list(combinations(D, 3))
    print(f"#triples = {len(triples)}")
    results = []
    for (d1, d2, d3) in triples:
        E = min_extent_np(d1, d2, d3, KMAX)
        if E is None:
            continue
        results.append((E, d1, d2, d3))
    if not results:
        print("  该集合内无任何超边 (全空)")
        return
    results.sort()
    minE = results[0][0]
    print(f"  最小 extent E_min = {minE}  => H_n[L] 空 对所有 n <= {2 * minE}")
    print(f"  (即 n < {2 * minE + 1} 时该方向集合内无任何超边)")
    print("  最早激活(最小 E)的全部三元组:")
    seen = set()
    for E, d1, d2, d3 in results:
        if E > minE:
            break
        key = tuple(sorted([d1, d2, d3]))
        if key in seen:
            continue
        seen.add(key)
        inv = [d in D6 for d in (d1, d2, d3)]
        print(f"    E={E}  {d1},{d2},{d3}  含D6={any(inv)}")
    if not exclude_D6:
        ninv = sum(1 for E, d1, d2, d3 in results if any(d in D6 for d in (d1, d2, d3)))
        print(f"  含>=1个D6方向的超边 / 总超边 = {ninv}/{len(results)} = {100.0 * ninv / len(results):.1f}%")
        # 最小 E 的若干层分布
        from collections import Counter
        ec = Counter(E for E, *_ in results)
        print("  E 值分布(小端):", dict(sorted(ec.items())[:8]))
    return results

if __name__ == "__main__":
    # 定理1: 低斜率空性 (L = maxcomp<=3 排除 D6). KMAX 大, 保证找到真最小.
    analyze(3, exclude_D6=True, KMAX=400, label="定理1 低斜率空性 L(排除D6, B=3)")

    # 定理2: 危险集中 — 全集含D6, 看最早激活的超边是否都含D6
    analyze(5, exclude_D6=False, KMAX=150, label="定理2 危险集中(全集 B=5)")
    analyze(7, exclude_D6=False, KMAX=100, label="定理2 危险集中(全集 B=7)")
