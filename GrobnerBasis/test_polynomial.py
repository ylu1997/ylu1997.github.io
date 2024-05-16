import PolynomialRing as pr
from Morphism import Homomorphism

TEST_1 = False
TEST_2 = False
TEST_3 = False
TEST_4 = True

if TEST_1:
    alg = pr.PolyAlg(('x_1', 'x_2', 'x_3'), pr.Rational, pr.monomial_ordering('lex'))

    m = alg.get_monomial((1,2,3,))
    t = alg.get_term((2,2,1), pr.Rational(1))
    print(m)
    print(m(2,1,3))
    print(t)
    print(t(pr.Rational(1), pr.Rational(2), pr.Rational(1,2)))
    x1 = alg.get_poly((1,0,0), pr.Rational(1))
    x2 = alg.get_poly((0,1,0), pr.Rational(1))
    x3 = alg.get_poly((0,0,1),pr.Rational(1))

    f = x1**2 + x2*x3
    print(f(x1, x1**2, x1**2))

if TEST_2:
    alg1 = pr.PolyAlg(('x_1', 'x_2', 'x_3'), pr.Rational, pr.monomial_ordering('lex'))
    alg2 = pr.PolyAlg(('y_1', 'y_2'), pr.Rational, pr.monomial_ordering('lex'))
    gen1 = alg1.generators()
    gen2 = alg2.generators()
    x1, x2, x3 = gen1
    y1, y2 = gen2
    hom = Homomorphism(alg1, alg2, [y1**2, y2**2, y1*y2])
    print(hom(x1*x2+x3))

if TEST_3:
    alg = pr.PolyAlg(('x', 'u', 'v'), pr.Rational, pr.monomial_ordering('lex'))
    x, u, v  = alg.generators()
    f1 = x ** 3 - x -u
    f2 = x ** 2 - v
    ans = alg.Groebner_Basis([f1, f2])
    g: pr.Polynomial = x ** 5
    print(g.normal_form(ans))
    print(ans)

if TEST_4:
    varlist = tuple(j+'_'+str(i) for j in ['a', 'b'] for i in range(6))
    print(varlist)
    alg = pr.PolyAlg(varlist, pr.Rational, pr.monomial_ordering('lex'))
    a0 = alg.get_poly((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    a1 = alg.get_poly((0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    a2 = alg.get_poly((0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    a3 = alg.get_poly((0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    a4 = alg.get_poly((0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    a5 = alg.get_poly((0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0), pr.Rational(1))
    b0 = alg.get_poly((0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0), pr.Rational(1))
    b1 = alg.get_poly((0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0), pr.Rational(1))
    b2 = alg.get_poly((0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0), pr.Rational(1))
    b3 = alg.get_poly((0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0), pr.Rational(1))
    b4 = alg.get_poly((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0), pr.Rational(1))
    b5 = alg.get_poly((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), pr.Rational(1))
    f1 = a0 * a5 + b0 * b5
    f2 = a0 * a4 + a1 * a5 + b0 * b4 + b1 * b5
    f3 = a0 * a3 + a1 * a4 + a2 * a5 + b0 * b3 + b1 * b4 + b2 * b5
    f4 = a0 * a2 + a1 * a3 + a2 * a4 + a3 * a5 + a0 * b2 + b1 * b3 + b2 * b4 + b3 * b5
    s0 = a0 * a0 - a0
    s1 = a1 * a1 - a1
    s2 = a2 * a2 - a2
    s3 = a3 * a3 - a3
    s4 = a4 * a4 - a4
    s5 = a5 * a5 - a5
    t0 = b0 * b0 - b0
    t1 = b1 * b1 - b1
    t2 = b2 * b2 - b2
    t3 = b3 * b3 - b3
    t4 = b4 * b4 - b4
    t5 = b5 * b5 - b5
    ans = alg.Groebner_Basis([s0,s1,s2,s3,s4,s5,t0,t1,t2,t3,t4,t5,f1,f2,f3,f4])
    print(ans)