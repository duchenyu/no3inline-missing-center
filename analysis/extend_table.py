"""
Extend the Flammenkamp + mvr data table with missing n values.
Scans local caches, decodes solutions, computes missing-center counts.
"""
import os
from collections import Counter

CACHE = os.path.join(os.path.dirname(__file__), 'flammenkamp_cache')
MVR = os.path.join(os.path.dirname(__file__), 'mvr_cache')

# --- Flammenkamp decoder ---
ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
char_to_val = {c: i for i, c in enumerate(ALPHABET)}

def decode_flam(line):
    """Decode a Flammenkamp-format solution line to point list.
    Each line encodes exactly 2 points per row → returns 2n points."""
    symm = line[0]
    rest = line.strip()[1:]
    n_rows = len(rest) // 2
    points = []
    for row in range(n_rows):
        c1 = char_to_val[rest[2*row]]
        c2 = char_to_val[rest[2*row+1]]
        points.append((row, c1))
        points.append((row, c2))
    return symm, n_rows, points

def has_center(n, points):
    """Check if grid center is a circumcenter of any triple."""
    X = n - 1
    rings = Counter()
    for x, y in points:
        d2 = (2*x - X)**2 + (2*y - X)**2
        rings[d2] += 1
    return any(v >= 3 for v in rings.values())

# --- RLE decoder (for mvr c4near files) ---
def parse_rle_solution(raw, n):
    """Parse a single RLE-encoded solution."""
    points = []
    row = 0
    col = 0
    i = 0
    while i < len(raw):
        num_str = ''
        while i < len(raw) and raw[i].isdigit():
            num_str += raw[i]
            i += 1
        count = int(num_str) if num_str else 1
        if i >= len(raw):
            break
        ch = raw[i]
        if ch == 'o':
            for _ in range(count):
                points.append((row, col))
                col += 1
        elif ch == 'b':
            col += count
        elif ch == '$':
            row += count
            col = 0
        elif ch == '!':
            break
        i += 1
    return points

def parse_rle(content):
    """Parse RLE content into a list of point lists."""
    solutions = []
    raw_sols = content.split('!')
    for raw in raw_sols:
        raw = raw.strip()
        if not raw:
            continue
        pts = parse_rle_solution(raw + '!', None)
        if pts:
            solutions.append(pts)
    return solutions

# ============================================
# 1. Scan Flammenkamp cache for all n
# ============================================
flam_files = {}
for fname in sorted(os.listdir(CACHE)):
    if fname.startswith('n') and '_' in fname:
        parts = fname.replace('n', '').split('_')
        n = int(parts[0])
        cls = parts[1]
        if n not in flam_files:
            flam_files[n] = []
        flam_files[n].append((cls, os.path.join(CACHE, fname)))

flam_data = {}
for n in sorted(flam_files.keys()):
    total_solutions = 0
    missing_solutions = 0
    classes = []
    for cls, fpath in sorted(flam_files[n]):
        with open(fpath) as f:
            lines = [l.strip() for l in f if l.strip()]
        # skip if empty or HTML
        if lines and '<html' not in lines[0].lower():
            class_missing = 0
            for line in lines:
                symm, _, points = decode_flam(line)
                if not has_center(n, points):
                    class_missing += 1
            total_solutions += len(lines)
            missing_solutions += class_missing
            classes.append(cls)
    if total_solutions > 0:
        flam_data[n] = {
            'total': total_solutions,
            'missing': missing_solutions,
            'rate': missing_solutions / total_solutions * 100,
            'classes': classes
        }
    else:
        flam_data[n] = {'total': 0, 'missing': 0, 'rate': 0, 'classes': classes}

# ============================================
# 2. Scan mvr c4near files (rct4 solutions for odd n≥47)
# ============================================
for fname in sorted(os.listdir(MVR)):
    if fname.startswith('c4near-'):
        n_str = fname.replace('c4near-', '').replace('.out', '')
        n = int(n_str)
        with open(os.path.join(MVR, fname)) as f:
            content = f.read()
        solutions = parse_rle(content)
        missing = 0
        for pts in solutions:
            if not has_center(n, pts):
                missing += 1
        # These are rct4 solutions by Flammenkamp convention
        if n not in flam_data:
            flam_data[n] = {}
        flam_data[n] = {
            'total': len(solutions),
            'missing': missing,
            'rate': missing / len(solutions) * 100 if solutions else 0,
            'classes': ['rct4'] + (['?'] if n not in flam_files.get(n, []) else [])
        }
        print(f"mvr c4near n={n}: {len(solutions)} rct4 solutions, {missing} missing-center")

# ============================================
# 3. Also scan mvr d4odd-47
# ============================================
if os.path.exists(os.path.join(MVR, 'd4odd-47.out')):
    with open(os.path.join(MVR, 'd4odd-47.out')) as f:
        content = f.read()
    solutions = parse_rle(content)
    if solutions:
        n = 47
        pts = solutions[0]
        hc = has_center(n, pts)
        print(f"mvr d4odd-47: 1 solution, has_center={hc}")

# ============================================
# 4. Print the complete extended table
# ============================================
print()
print(f"{'n':>3} {'Total':>8} {'Missing':>8} {'Rate%':>7} {'Classes'}")
print("-" * 70)

# All n values that should be in the table (7-45 + beyond)
all_ns = list(range(7, 48)) + [49, 51, 53]
for n in all_ns:
    if n in flam_data:
        d = flam_data[n]
        rate_str = f"{d['rate']:.1f}%" if d['total'] > 0 else "-"
        cls_str = ", ".join(sorted(d['classes']))
        print(f"{n:>3} {d['total']:>8} {d['missing']:>8} {rate_str:>7} {cls_str}")
    else:
        print(f"{n:>3} {'--':>8} {'--':>8} {'--':>7} (no data)")
