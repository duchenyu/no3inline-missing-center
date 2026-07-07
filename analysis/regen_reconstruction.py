"""
Focused regeneration of the D4 -> Full reconstruction for n=7..22 using the
CORRECT exact-integer missing-center criterion. Outputs a consistent table with
both D4-inequivalent and Full (orbit-expanded) counts, plus the per-class
breakdown needed to update d4_reconstruction_results.txt and the regression.
"""
import urllib.request
from collections import Counter

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
cv = {c: i for i, c in enumerate(ALPHABET)}

SYMM_MULT = {'.': 8, ':': 4, '/': 4, '-': 4, 'o': 2, 'x': 2, '+': 2, 'c': 1, '*': 1}
SYMM_NAMES = {'.': 'iden', ':': 'rot2', '/': 'dia1', '-': 'ort1',
              'o': 'rot4', 'c': 'rct4', 'x': 'dia2', '+': 'ort2', '*': 'full'}

def decode(line):
    rest = line.strip()[1:]
    n = len(rest) // 2
    pts = []
    for r in range(n):
        pts.append((r, cv[rest[2*r]]))
        pts.append((r, cv[rest[2*r+1]]))
    return n, pts

def is_missing(n, pts):
    # Exact integer squared distance from grid center: d = (2x-(n-1))^2 + (2y-(n-1))^2
    X = n - 1
    rings = Counter()
    for x, y in pts:
        d2 = (2*x - X)**2 + (2*y - X)**2
        rings[d2] += 1
    return all(v < 3 for v in rings.values())

def load(n, symm, url_name):
    # Try local cache first (zero network)
    import os
    cache_dir = os.path.join(os.path.dirname(__file__), 'flammenkamp_cache')
    cache_path = os.path.join(cache_dir, f'n{n}_{url_name}')
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            lines = [l.strip() for l in f if l.strip()]
            return lines
    
    url = f'http://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n{n}_{url_name}'
    try:
        proxy_addr = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
        if proxy_addr:
            proxy = urllib.request.ProxyHandler({'http': proxy_addr, 'https': proxy_addr})
            opener = urllib.request.build_opener(proxy)
        else:
            opener = urllib.request.build_opener()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with opener.open(req, timeout=30) as f:
            raw = f.read().decode().strip()
            lines = [l for l in raw.split('\n') if l.strip()]
            if not lines or '<html' in lines[0].lower():
                return None
            return lines
    except Exception:
        return None

ns = list(range(7, 23))
classes = ['.', ':', '/', '-', 'o', 'c', 'x', '+', '*']
url_names = {'.': 'iden', ':': 'rot2', '/': 'dia1', '-': 'ort1',
             'o': 'rot4', 'c': 'rct4', 'x': 'dia2', '+': 'ort2', '*': 'full'}

print(f"{'n':>3} {'D4_tot':>7} {'D4_miss':>8} {'D4_%':>6} {'Full_tot':>9} {'Full_miss':>10} {'Full_%':>6}  classes")
print('-' * 95)
results = {}
for n in ns:
    d4_tot = d4_miss = full_tot = full_miss = 0
    det = []
    for s in classes:
        lines = load(n, s, url_names[s])
        if lines is None:
            continue
        cnt = len(lines)
        miss = sum(1 for ln in lines if is_missing(*decode(ln)))
        mult = SYMM_MULT[s]
        d4_tot += cnt
        d4_miss += miss
        full_tot += cnt * mult
        full_miss += miss * mult
        det.append(f"{SYMM_NAMES[s]}:{cnt}(m={miss})")
    d4_rate = d4_miss / d4_tot * 100 if d4_tot else 0
    full_rate = full_miss / full_tot * 100 if full_tot else 0
    results[n] = (d4_tot, d4_miss, full_tot, full_miss)
    print(f"{n:>3} {d4_tot:>7} {d4_miss:>8} {d4_rate:>5.2f}% {full_tot:>9} {full_miss:>10} {full_rate:>5.2f}%  {', '.join(det)}")

print('\n# Python dict for sum_of_two_squares.py (D4-consistent):')
print('missing_data = {')
for n in ns:
    d4_tot, d4_miss, full_tot, full_miss = results[n]
    print(f'    {n}: ({d4_tot}, {d4_miss}),  # Full=({full_tot}, {full_miss})')
print('}')
