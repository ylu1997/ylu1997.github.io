def lexicographical_order(index1, index2):
    """
    index1 > index2 -> 1
    index1 == index2 -> 0
    index1 < index2 -> -1
    :param index1:
    :param index2:
    :return:
    """
    if len(index1) == len(index2):
        for i in range(len(index1)):
            i1 = index1[i]
            i2 = index2[i]
            if i1 > i2:
                return 1
            if i1 < i2:
                return -1
        return 0
    else:
        raise ValueError("Different length of two indices")
