"""
Classify all 16 C4 lift triples for D=0 (collinear condition).
ka=0 fixed (C4 reduction). Compute algebraic forms explicitly.
"""
from itertools import product

def px(k, x, y, n):
    """x-coordinate of cell (x,y) with lift index k"""
    if k == 0: return x
    elif k == 1: return n - 1 - y
    elif k == 2: return n - 1 - x
    elif k == 3: return y

def py(k, x, y, n):
    """y-coordinate of cell (x,y) with lift index k"""
    if k == 0: return y
    elif k == 1: return x
    elif k == 2: return n - 1 - y
    elif k == 3: return n - 1 - x

def D_symbolic(ka, kb, kc):
    """Compute the symbolic expression for D as a tuple of (coeff, var_string) for each monomial term.
    Returns list of strings forming the expression. Variables: a_x, a_y, b_x, b_y, c_x, c_y, n"""
    # D = (px(b)-px(a))*(py(c)-py(a)) - (px(c)-px(a))*(py(b)-py(a))
    # We'll compute by expanding: D = px(b)*py(c) - px(b)*py(a) - px(a)*py(c) + px(a)*py(a) 
    #                                - px(c)*py(b) + px(c)*py(a) + px(a)*py(b) - px(a)*py(a)
    #                              = px(b)*py(c) - px(b)*py(a) - px(a)*py(c) + px(c)*py(a) + px(a)*py(b) - px(c)*py(b)
    # Let's expand symbolically by substituting the actual forms.
    pass

# Better approach: use Python's symbolic computation with eval on term-by-term basis.
# Represent each coordinate as a string and expand symbolically.

class Sym:
    """Simple symbolic expression: dict mapping term_key -> coefficient"""
    def __init__(self, expr=None):
        self.terms = {}  # {term_str: coefficient}
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
            k = '1'
            result.terms[k] = result.terms.get(k, 0) + other
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
                    new_term = _mul_terms(t1, t2)
                    result.terms[new_term] = result.terms.get(new_term, 0) + c1 * c2
            result._clean()
            return result
        return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def _clean(self):
        # Remove zero coefficients and merge
        to_del = [t for t, c in self.terms.items() if c == 0]
        for t in to_del:
            del self.terms[t]
    
    def __repr__(self):
        if not self.terms:
            return "0"
        parts = []
        for t_str, c in sorted(self.terms.items(), key=lambda x: (-abs(x[1]), x[0])):
            if c == 1:
                parts.append(t_str)
            elif c == -1:
                parts.append(f"-{t_str}")
            else:
                parts.append(f"{c:+d}·{t_str}")
        s = " ".join(parts).replace("+ -", "- ").replace(" +", " ").strip()
        if s.startswith("+ "):
            s = s[2:]
        if s.startswith("- "):
            s = "-" + s[1:]
        return s
    
    def __neg__(self):
        return self * (-1)

def _mul_terms(t1, t2):
    """Multiply two term strings"""
    if t1 == '1': return t2
    if t2 == '1': return t1
    # Parse terms like "x_a" or "a_x*b_y"
    t1_parts = t1.split('*')
    t2_parts = t2.split('*')
    all_parts = sorted(t1_parts + t2_parts)
    return '*'.join(all_parts)

# Variable names
xa, ya = Sym('a_x'), Sym('a_y')
xb, yb = Sym('b_x'), Sym('b_y')
xc, yc = Sym('c_x'), Sym('c_y')
N = Sym('n')

def px_sym(k, x, y):
    """Symbolic x-coordinate"""
    if k == 0: return x
    elif k == 1: return N + Sym(-1) - y
    elif k == 2: return N + Sym(-1) - x
    elif k == 3: return y

def py_sym(k, x, y):
    """Symbolic y-coordinate"""
    if k == 0: return y
    elif k == 1: return x
    elif k == 2: return N + Sym(-1) - y
    elif k == 3: return N + Sym(-1) - x

print("=" * 80)
print("16 C4 LIFT TRIPLES — COLLINEAR CONDITION D=0")
print("ka=0 fixed; kb,kc ∈ {0,1,2,3}")
print("=" * 80)

results = []
for kb, kc in product(range(4), range(4)):
    ka = 0
    xa_k = px_sym(ka, xa, ya)
    ya_k = py_sym(ka, xa, ya)
    xb_k = px_sym(kb, xb, yb)
    yb_k = py_sym(kb, xb, yb)
    xc_k = px_sym(kc, xc, yc)
    yc_k = py_sym(kc, xc, yc)
    
    dx_ba = xb_k - xa_k
    dy_ba = yb_k - ya_k
    dx_ca = xc_k - xa_k
    dy_ca = yc_k - ya_k
    
    D = dx_ba * dy_ca - dx_ca * dy_ba
    
    # Clean up
    D._clean()
    
    # Count terms
    n_terms = len(D.terms)
    
    # Check for identity zero
    is_zero = n_terms == 0
    
    # Check if n factors out
    has_n = any('n' in t for t in D.terms)
    
    print(f"\n--- (kb={kb}, kc={kc}) ---")
    print(f"  D = {D}")
    
    # Simple classification for now
    results.append({
        'kb': kb, 'kc': kc,
        'n_terms': n_terms,
        'is_zero': is_zero,
        'has_n': has_n,
        'str': str(D),
    })

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"{'kb':>3} {'kc':>3} {'zero?':>6} {'has_n':>6} {'n_terms':>8}  D expression")
print("-" * 80)
for r in results:
    zero_s = "YES" if r['is_zero'] else "no"
    n_s = "YES" if r['has_n'] else "no"
    print(f"{r['kb']:>3} {r['kc']:>3} {zero_s:>6} {n_s:>6} {r['n_terms']:>8}  {r['str']}")

# Group identical forms
print("\n" + "=" * 80)
print("IDENTICAL FORMS (same up to cell-renaming)")
print("=" * 80)
form_groups = {}
for r in results:
    key = r['str']
    if key not in form_groups:
        form_groups[key] = []
    form_groups[key].append((r['kb'], r['kc']))

for expr, pairs in sorted(form_groups.items(), key=lambda x: -len(x[1])):
    s = "IDENTICALLY_ZERO" if expr == "0" else expr
    print(f"  {pairs}:  {s}")

# Count how many forms are symmetrically equivalent
# kb and kc play symmetric roles WHEN their cells are different
# Check if (kb, kc) and (kc, kb) give same form
print("\n" + "=" * 80)
print("ROLE SYMMETRY CHECK: D(ka=0,kb=a,kc=b) vs D(ka=0,kb=b,kc=a)")
print("(Should be equal up to sign since swapping b,c flips D)")
print("=" * 80)
for kb, kc in product(range(4), range(4)):
    form_bc = results[kb*4+kc]['str']
    form_cb = results[kc*4+kb]['str']
    # Check if negated
    # Simple check: compare strings (not rigorous but indicative)
    # Better: compare term dicts
    r1 = results[kb*4+kc]
    r2 = results[kc*4+kb]
    t1 = r1['str']
    t2 = r2['str']
    neg = t1 == t2.replace('+', '@').replace('-', '+').replace('@', '-')  # rough
    print(f"  (kb={kb},kc={kc}): {t1}")
    print(f"  (kb={kc},kc={kb}): {t2}")
    print()

print("\nDone.")
