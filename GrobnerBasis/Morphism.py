import PolynomialRing as pr
from utils_func import type_check, source_ring_check

class Homomorphism:
    def __init__(self, source_alg: pr.PolyAlg, target_alg: pr.PolyAlg, morphism_im: list):
        self.s_alg = source_alg
        self.t_alg = target_alg
        self.image = morphism_im
        for item in self.image:
            source_ring_check(item.base_ring, self.t_alg)
        if len(self.image) != self.s_alg.deg_len:
            raise ValueError("Morphism is not well defined.")

    def __call__(self, s_poly: pr.Polynomial):
        return s_poly(*self.image)