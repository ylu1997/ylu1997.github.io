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

if __name__ == '__main__':
    varlist = ('x','y', 'z')

    q1 = Polynomial(Term(varlist, (2,0,0), 1)) + Polynomial(Term(varlist, (0,1,0),-1))
    q2 = Polynomial(Term(varlist, (3, 0,0), 1)) + Polynomial(Term(varlist, (0,0, 1), -1))
    print(q1)
    print(q2)

    G = Grobner_Basis([q1,q2])
    print('xxxxx')
    print(G)
    print((G[1]%G[0]))
