"""
For each of the 16 lift-index forms, compute the range of D values
across all possible cell coordinates for a given m.
If min_D > 0 or max_D < 0 for a form, that form can NEVER produce collinearity
and can be pruned from the constraint set.
"""
from itertools import product
import json

# The 16 forms: D = expression in a_x,a_y,b_x,b_y,c_x,c_y,n
# Reconstruct the symbolic forms using our symbol class from classify_lift_forms2.py

class Sym:
    def __init__(self, expr=None):
        self.terms = {}
        if expr is not None:
            if isinstance(expr, (int, float)) and expr != 0:
                self.terms['1'] = expr
            elif isinstance(expr, str):
                self.terms[expr] = 1
    
    def __add__(self, other):
        result = Sym()
        if isinstance(other, Sym):
            result.terms = dict(self.terms)
            for t, c in other.terms.items():
                result.terms[t] = result.terms.get(t, 0) + c
        else:
            result.terms = dict(self.terms)
            result.terms['1'] = result.terms.get('1', 0) + other
        result._clean()
        return result
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, Sym):
            return self + (-1) * other
        return self + (-other)
    
    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Sym(other) - self
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = Sym()
            result.terms = {t: c * other for t, c in self.terms.items()}
            result._clean()
            return result
        if isinstance(other, Sym):
            result = Sym()
            for t1, c1 in self.terms.items():
                for t2, c2 in other.terms.items():
                    new_term = self._mul_terms(t1, t2)
                    result.terms[new_term] = result.terms.get(new_term, 0) + c1 * c2
            result._clean()
            return result
        return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def _mul_terms(self, t1, t2):
        if t1 == '1': return t2
        if t2 == '1': return t1
        t1_parts = t1.split('*')
        t2_parts = t2.split('*')
        all_parts = sorted(t1_parts + t2_parts)
        return '*'.join(all_parts)
    
    def _clean(self):
        to_del = [t for t, c in self.terms.items() if c == 0]
        for t in to_del:
            del self.terms[t]
    
    def __neg__(self):
        return self * (-1)
    
    def __repr__(self):
        if not self.terms:
            return "0"
        parts = []
        for t_str, c in sorted(self.terms.items(), key=lambda x: (-abs(x[1]), x[0])):
            if c == 1: parts.append(f"+{t_str}")
            elif c == -1: parts.append(f"-{t_str}")
            else: parts.append(f"{c:+d}·{t_str}")
        s = " ".join(parts)
        # cleanup
        s = s.replace("+ -", "- ")
        if s.startswith("+ "): s = s[2:]
        if s.startswith("- "): s = "-" + s[1:]
        return s.strip()

# Variable objects
xa_s = Sym('a_x')
ya_s = Sym('a_y')
xb_s = Sym('b_x')
yb_s = Sym('b_y')
xc_s = Sym('c_x')
yc_s = Sym('c_y')
N_s = Sym('n')

def px_sym(k, x, y):
    if k == 0: return x
    elif k == 1: return N_s + Sym(-1) - y
    elif k == 2: return N_s + Sym(-1) - x
    elif k == 3: return y

def py_sym(k, x, y):
    if k == 0: return y
    elif k == 1: return x
    elif k == 2: return N_s + Sym(-1) - y
    elif k == 3: return N_s + Sym(-1) - x

# Precompute the 16 forms as term lists
forms = {}
for kb, kc in product(range(4), range(4)):
    ka = 0
    xa_k = px_sym(ka, xa_s, ya_s)
    ya_k = py_sym(ka, xa_s, ya_s)
    xb_k = px_sym(kb, xb_s, yb_s)
    yb_k = py_sym(kb, xb_s, yb_s)
    xc_k = px_sym(kc, xc_s, yc_s)
    yc_k = py_sym(kc, xc_s, yc_s)
    
    dx_ba = xb_k - xa_k
    dy_ba = yb_k - ya_k
    dx_ca = xc_k - xa_k
    dy_ca = yc_k - ya_k
    
    D = dx_ba * dy_ca - dx_ca * dy_ba
    D._clean()
    forms[(kb, kc)] = D.terms

# Parse term structure: for each term in a form, determine its contribution
# as a function of cell coordinates. Terms are like 'a_x*b_y', 'n*n', 'a_x', etc.
# For a given m, compute the min and max possible D value.

def term_value(term_str, cell_vals, n_val):
    """
    Evaluate a single term like 'a_x*b_y' given cell coordinate values
    and n.
    cell_vals = {'a_x':v, 'a_y':v, 'b_x':v, 'b_y':v, 'c_x':v, 'c_y':v}
    """
    if term_str == '1':
        return 1
    if term_str == 'n':
        return n_val
    if term_str == 'n*n':
        return n_val * n_val
    
    parts = term_str.split('*')
    val = 1
    for p in parts:
        if p == 'n':
            val *= n_val
        else:
            val *= cell_vals[p]
    return val

def D_range(m, terms_dict):
    """Compute min/max of D over all cell coordinate assignments in [0,m-1]."""
    n_val = 2 * m
    coord_range = range(0, m)
    
    min_d = None
    max_d = None
    
    # Brute force: 6 nested loops O(m^6). Only feasible for small m.
    # For m up to 6: full enumeration. For larger m: estimate via random sampling.
    
    if m <= 6:
        for ax, ay, bx, by, cx, cy in product(coord_range, repeat=6):
            cv = {'a_x': ax, 'a_y': ay, 'b_x': bx, 'b_y': by, 'c_x': cx, 'c_y': cy}
            d = sum(c * term_value(t, cv, n_val) for t, c in terms_dict.items())
            if min_d is None or d < min_d: min_d = d
            if max_d is None or d > max_d: max_d = d
        return min_d, max_d
    else:
        # Sampling-based estimate for larger m
        import random
        random.seed(42)
        for _ in range(50000):
            cv = {k: random.randrange(m) for k in ['a_x','a_y','b_x','b_y','c_x','c_y']}
            d = sum(c * term_value(t, cv, n_val) for t, c in terms_dict.items())
            if min_d is None or d < min_d: min_d = d
            if max_d is None or d > max_d: max_d = d
        return min_d, max_d

print("=" * 80)
print("RANGE ANALYSIS OF 16 LIFT FORMS")
print("D=0 achievable iff min_D ≤ 0 ≤ max_D")
print("=" * 80)

for m in [5, 6, 7, 10, 15, 20, 37]:
    n_val = 2 * m
    print(f"\n--- m={m} (n={n_val}) ---")
    print(f"{'Form':>8} {'min_D':>10} {'max_D':>10} {'zero_possible?':>16}")
    print("-" * 50)
    for kb in range(4):
        for kc in range(4):
            terms = forms.get((kb, kc), {})
            if not terms:
                continue
            min_d, max_d = D_range(m, terms)
            zero_possible = (min_d <= 0 <= max_d)
            zp_str = "YES" if zero_possible else "NO"
            print(f"  ({kb},{kc}) {min_d:>10} {max_d:>10} {zp_str:>16}")
    
    # Count forms where zero is impossible
    total_forms = 16
    impossible = 0
    for kb in range(4):
        for kc in range(4):
            terms = forms.get((kb, kc), {})
            min_d, max_d = D_range(m, terms)
            if min_d is not None and max_d is not None and not (min_d <= 0 <= max_d):
                impossible += 1
    print(f"  Forms where D=0 is impossible: {impossible}/{total_forms}")
    print(f"  Fraction: {100*impossible/total_forms:.0f}% of all constraints never fire")

print("\n\nDone.")
