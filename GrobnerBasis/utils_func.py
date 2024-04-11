def type_check(other, required_type):
    if not isinstance(other, required_type):
        raise TypeError("Must be a " + str(required_type) + '.')

def source_ring_check(base1, base2):
    if base1 != base2:
        raise TypeError("They must be have same source.")