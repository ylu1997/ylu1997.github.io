from utils.Polynomial import Polynomial, Term

def syzygy_polynomial(p1: Polynomial, p2: Polynomial) -> Polynomial:
    lcm = p1.initial.mono.LCM(p2.initial.mono)
    c1 = lcm / p1.initial.mono
    c2 = lcm / p2.initial.mono
    s = p1 * Polynomial.mono_to_poly(c1) - p2 * Polynomial.mono_to_poly(c2)
    return s


def do_normalization(f: Polynomial, polys: list) -> Polynomial:
    ans = f.deepcopy()
    for item in polys:
        ans = ans % item
        print(ans, f, item)
    return ans

def Grobner_Basis(F: list):
    G = [item for item in F]
    B = []
    for i in range(len(G)):
        for j in range(i + 1, len(G)):
            B.append((G[i],G[j]))

    while B != []:
        pair = B.pop()
        r = do_normalization(syzygy_polynomial(pair[0],pair[1]), G)

        if r != Polynomial.zero(r.varlist):
            B = B + [(item, r) for item in G]
            G = G + [r]

    return G

def valuation(poly: Polynomial, base_poly: Polynomial) -> (int, Polynomial):
    result = 0
    quotient, remainder = divmod(poly, base_poly)
    while True:
        if remainder != Polynomial.zero(poly.varlist):
            break
        result += 1
        quotient, remainder = divmod(quotient, base_poly)
    return result, remainder

def high_rank_valuation(poly: Polynomial, polys:list[Polynomial]):
    varlist_num = len(poly.varlist)
    if len(polys) > varlist_num:
        raise ValueError("The number of polynomials (%d) is too much than %d." % (varlist_num, len(polys)))
    result = list(0 for i in range(varlist_num))
    remainder = poly
    result[0], remainder = valuation(remainder, polys[0])
    for i in range(1, len(polys)):

        val, remainder = valuation(remainder, divmod(polys[i], polys[i - 1])[1])
        result[i] = val
    return tuple(result)

if __name__ == '__main__':
    # valuation(1,2,3,4)
    pass
    varlist = ('x_1', 'x_2', 'x_3')
    x1 = Polynomial(Term(varlist, (1, 0, 0), 1))
    x2 = Polynomial(Term(varlist, (0, 1, 0), 1))
    x3 = Polynomial(Term(varlist, (0, 0, 1), 1))

    p = x1 * x1 * x2 * x3 + x2 * x3
    print(p)
    print(high_rank_valuation(p,[x1,x2,x3]))
    # print(q1)
    # print(q2)
    # print(valuation(q1 * q2 * q2,q2))
    # print(high_rank_valuation(q1,[q1, q2]))