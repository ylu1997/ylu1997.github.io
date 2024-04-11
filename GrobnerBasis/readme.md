# File Descriptions

## 1. Field

### Description
`Field.py` contains classes and functions related to mathematical fields.

### Content
- `gcd(a, b)`: This function calculates the greatest common divisor (GCD) of two integers `a` and `b` using the Euclidean algorithm.
- `Rational` class: This class represents rational numbers and provides various arithmetic operations for rational numbers.
  
## 2. PolynomialRing

### Description
`PolynomialRing.py` contains classes and functions related to polynomial rings and operations on polynomials.

### Content
- `lex_ord(v1, v2)`: This function defines the lexicographic order for vectors `v1` and `v2`.
- `grlex_ord(v1, v2)`: This function defines the graded lexicographic order for vectors `v1` and `v2`.
- `grelex_ord(v1, v2)`: This function defines the graded reverse lexicographic order for vectors `v1` and `v2`.
- `monomial_ordering(order_type='lex')`: This function returns a monomial ordering function based on the specified order type.
- `Monomial` class: This class represents a monomial and provides various operations on monomials, including multiplication, division, comparison, etc.
- `Term` class: This class represents a term, which is a monomial multiplied by a coefficient. It inherits from the `Monomial` class and provides additional operations such as addition, subtraction, etc.
- `Polynomial` class: This class represents a polynomial and provides operations such as addition, subtraction, multiplication, division, etc.
