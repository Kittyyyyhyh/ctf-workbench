#!/usr/bin/env python3
"""mathkit - CTF crypto math one-liners (baked into ctf-crypto at /opt/mathkit).

Dependencies: gmpy2, sympy, factordb (all present in ctf-crypto).

Usage:
  mathkit factor <n>                      # factordb first, sympy for small n
  mathkit cuberoot <c>                    # small-e attack: integer e-th root
  mathkit rsadecrypt <n> <e> <c> [p q]    # decrypt; factors from factordb if omitted
  mathkit wiener <n> <e>                  # Wiener attack (large d small)
  mathkit fermat <n> [steps]              # Fermat factorization (close p,q)
  mathkit commonmod <n> <e1> <e2> <c1> <c2>   # common modulus (gcd(e1,e2)=1)
  mathkit hastad <c1,n1> <c2,n2> ...      # e pairs, CRT + integer root
  mathkit dlog <g> <h> <p>                # discrete log
  mathkit lll matrix.json                 # LLL reduce; file = [[row],[row],...]

Ints print as decimal; if they decode to printable bytes, bytes are shown too.
"""
from __future__ import annotations

import argparse
import json
import sys


def show(m: int) -> None:
    print(m)
    try:
        b = m.to_bytes((m.bit_length() + 7) // 8, "big")
        if all(32 <= ch < 127 for ch in b) and b:
            print(f"bytes: {b.decode()}")
    except Exception:
        pass


def to_int(s: str) -> int:
    s = s.strip()
    for base in (10, 16):
        try:
            return int(s, base)
        except ValueError:
            continue
    raise ValueError(f"not an int: {s[:40]}")


def _factordb(n: int):
    """factordb-python and factordb-pycli ship different method names; duck-type."""
    from factordb.factordb import FactorDB
    f = FactorDB(str(n))
    f.connect()
    fl = getattr(f, "get_factor_list", None) or getattr(f, "getfactorlist")
    st = getattr(f, "get_status", None) or getattr(f, "getstatus")
    return fl(), st()


# ---------------------------------------------------------------- factor

def cmd_factor(args):
    import gmpy2
    n = to_int(args.n)
    if gmpy2.is_prime(n):
        print(f"{n} is prime"); return
    try:
        fl, st = _factordb(n)
        if fl and st in ("FF", "P"):
            print("factordb:", " * ".join(map(str, fl)))
            return
    except Exception as e:
        print(f"factordb unreachable ({e}); trying sympy", file=sys.stderr)
    from sympy import factorint
    fs = factorint(n)
    if len(fs) == 1 and list(fs.values())[0] == 1:
        print("no factorization found (n too large for sympy; try yafu or RsaCtfTool)")
        return
    print("sympy:", " * ".join(f"{p}^{k}" if k > 1 else str(p) for p, k in fs.items()))


# ---------------------------------------------------------------- small e

def cmd_cuberoot(args):
    import gmpy2
    c = to_int(args.c)
    m, exact = gmpy2.iroot(c, args.k)
    if not exact:
        print(f"not a perfect {args.k}-th root (no padding-less small-e here?)")
        return
    show(int(m))


# ---------------------------------------------------------------- rsa decrypt

def cmd_rsadecrypt(args):
    n, e, c = to_int(args.n), to_int(args.e), to_int(args.c)
    if args.p and args.q:
        p, q = to_int(args.p), to_int(args.q)
    else:
        fl, st = _factordb(n)
        if len(fl) < 2:
            print(f"cannot factor n (factordb status {st}); pass p and q")
            return
        p, q = fl[0], fl[1]
    d = pow(e, -1, (p - 1) * (q - 1))
    show(pow(c, d, n))


# ---------------------------------------------------------------- wiener

def cmd_wiener(args):
    import gmpy2
    n, e = to_int(args.n), to_int(args.e)
    a, b = e, n
    cf = []
    while b:
        cf.append(a // b)
        a, b = b, a % b
    p0, p1, q0, q1 = 0, 1, 1, 0
    for ai in cf:
        p, q = ai * p1 + p0, ai * q1 + q0
        p0, p1, q0, q1 = p1, p, q1, q
        k, d = p, q
        if k == 0 or (e * d - 1) % k:
            continue
        phi = (e * d - 1) // k
        s = n - phi + 1
        disc = s * s - 4 * n
        if disc >= 0:
            r = gmpy2.isqrt(gmpy2.mpz(disc))
            if r * r == disc and (s + r) % 2 == 0:
                print(f"d = {d}")
                show(pow(to_int(args.c) if args.c else 1, d, n)) if args.c else None
                return
    print("wiener failed (d may not be small enough)")


# ---------------------------------------------------------------- fermat

def cmd_fermat(args):
    import gmpy2
    n = to_int(args.n)
    a = gmpy2.isqrt(n)
    if a * a < n:
        a += 1
    for i in range(args.steps):
        b2 = a * a - n
        b = gmpy2.isqrt(b2)
        if b * b == b2:
            print(f"p = {a + b}\nq = {a - b}\n({i} iterations)")
            return
        a += 1
    print(f"fermat failed in {args.steps} steps (p,q not close enough)")


# ---------------------------------------------------------------- common modulus

def cmd_commonmod(args):
    import gmpy2
    n, e1, e2, c1, c2 = (to_int(x) for x in (args.n, args.e1, args.e2, args.c1, args.c2))
    g, s, t = gmpy2.gcdext(e1, e2)
    assert g == 1, f"gcd(e1,e2)={g} != 1"
    m = pow(c1, int(s), n) * pow(c2, int(t), n) % n
    show(m)


# ---------------------------------------------------------------- hastad

def cmd_hastad(args):
    import gmpy2
    from sympy.ntheory.modular import crt
    pairs = []
    for spec in args.pairs:
        c_s, n_s = spec.split(",", 1)
        pairs.append((to_int(c_s), to_int(n_s)))
    e = args.e
    assert len(pairs) >= e, f"hastad needs >= e={e} (n,c) pairs"
    ns = [p[1] for p in pairs[:e]]
    cs = [p[0] for p in pairs[:e]]
    m, _ = crt(ns, cs)
    m = int(m)
    root, exact = gmpy2.iroot(m, e)
    if not exact:
        print("CRT ok but not a perfect e-th root (check e / pairs)")
        return
    show(int(root))


# ---------------------------------------------------------------- dlog

def cmd_dlog(args):
    from sympy.ntheory.residue_ntheory import discrete_log
    g, h, p = to_int(args.g), to_int(args.h), to_int(args.p)
    show(discrete_log(p, h, g))


# ---------------------------------------------------------------- lll (pure python)

def lll(B, delta=0.75):
    from fractions import Fraction
    B = [list(map(int, row)) for row in B]
    n = len(B)
    dot = lambda u, v: sum(x * y for x, y in zip(u, v))

    def gso(rows):
        orth, mu = [], [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            orth.append(rows[i][:])
            for j in range(i):
                d = dot(orth[j], orth[j])
                if d:
                    mu[i][j] = Fraction(dot(rows[i], orth[j]), d)
                    orth[i] = [a - mu[i][j] * b for a, b in zip(orth[i], orth[j])]
        return orth, mu

    rows = B[:]
    orth, mu = gso(rows)
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                r = round(mu[k][j])
                rows[k] = [a - r * b for a, b in zip(rows[k], rows[j])]
                orth, mu = gso(rows)
        if dot(orth[k], orth[k]) >= (Fraction(delta) - mu[k][k - 1] ** 2) * dot(orth[k - 1], orth[k - 1]):
            k += 1
        else:
            rows[k], rows[k - 1] = rows[k - 1], rows[k]
            orth, mu = gso(rows)
            k = max(k - 1, 1)
    return rows


def cmd_lll(args):
    B = json.load(open(args.matrix))
    for row in lll(B):
        print(row)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="mathkit", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("factor").add_argument("n")
    p = sp.add_parser("cuberoot"); p.add_argument("c"); p.add_argument("--k", type=int, default=3)
    p = sp.add_parser("rsadecrypt"); p.add_argument("n"); p.add_argument("e"); p.add_argument("c")
    p.add_argument("p", nargs="?"); p.add_argument("q", nargs="?")
    p = sp.add_parser("wiener"); p.add_argument("n"); p.add_argument("e"); p.add_argument("c", nargs="?")
    p = sp.add_parser("fermat"); p.add_argument("n"); p.add_argument("--steps", type=int, default=100000)
    p = sp.add_parser("commonmod"); p.add_argument("n"); p.add_argument("e1"); p.add_argument("e2")
    p.add_argument("c1"); p.add_argument("c2")
    p = sp.add_parser("hastad"); p.add_argument("pairs", nargs="+"); p.add_argument("--e", type=int, default=None)
    p = sp.add_parser("dlog"); p.add_argument("g"); p.add_argument("h"); p.add_argument("p")
    p = sp.add_parser("lll"); p.add_argument("matrix")
    args = ap.parse_args()
    if args.cmd == "hastad" and args.e is None:
        args.e = len(args.pairs)
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
