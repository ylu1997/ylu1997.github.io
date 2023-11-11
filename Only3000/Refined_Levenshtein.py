# The edit tuple is (substitution, insertion, deletion, is edit)
# Binary edit code: [substitution_bit, insertion_bit, deletion_bit, is_edit_bit]

#####################################CPU Algorithm#######################################
def deter_int_bit(num: int) -> int:
    """
    Used to determine the minimum number of digits of an integer.
    :param num: Input number.
    :return: The minimum number of digits of input number.
    """
    ans = 1
    n = num
    while True:
        n = n // 2
        if n == 0:
            break
        ans += 1
    return ans

def bit_info(restriction: list) -> tuple:
    """
    Returns the number of binary numbers used to represent substitution, insertions, and deletions
    :param restriction: Type of error [substitution, insertion and deletion]
    :return: Number of substitution, insertion and deletion.
    """
    sub = restriction[0]
    indel = restriction[1]
    bit_num_4_sub = deter_int_bit(sub)
    bit_num_4_ins = deter_int_bit(indel)
    bit_num_4_del = bit_num_4_ins
    return bit_num_4_sub, bit_num_4_ins, bit_num_4_del

def num_of_int8(required_num: int) -> int:
    """
    The int8 type is used to hold the index of the edit record, because we need only record the boolean value.
    The total number of bits should be greater than all possible edit records.
    :param required_num: Total number of edit records that need to be represented.
    :return: Minimum number of int8 required.
    """
    ans = 0
    while True:
        if ans * 8 >= required_num:
            return ans
        else:
            ans += 1

def get_ith_bool_val(record_list: list, index: int) -> int:
    """
    Gets the binary value of the index position
    :param record_list: The array of positions (i, j) of the dp array
    :param index: Index to the feasible
    :return: The binary value at the index position is
    """
    index_list = index // 8
    index_digit = index % 8
    return (record_list[index_list] // 2 ** (index_digit)) % 2

def assign_ith_bool_1(record_list: list, index: int):
    """
    Assign the index bit to 1
    :param record_list: The array of positions (i, j) of the dp array
    :param index: Index to the feasible
    :return: None
    """
    index_list = index // 8
    index_digit = index % 8
    record_list[index_list] = record_list[index_list] | (2 ** index_digit)

def from_edit_to_num(num_sub: int, num_ins: int, num_del: int, indel_limit: int) -> int:
    """
    Converts the edit record to the corresponding number
    :param num_sub: The number of substitution.
    :param num_ins: The number of insertion.
    :param num_del: The number of deletion.
    :param indel_limit: The limit of indel
    :return: Encoded number.
    """
    ans = num_del + num_ins * (indel_limit + 1) + num_sub * (indel_limit + 1) ** 2
    return ans

def dp_initialization(len_seq: int, indel_limit: int, num_int: int) -> list:
    """
    Initializes the dynamic programming matrix.
    :param len_seq: Length of sequence.
    :param indel_limit: Limit of indel.
    :param num_int: Number of int8.
    :return: Dynamic programming matrix.
    """
    ans = [[[0 for ___ in range(num_int)] for __ in range(len_seq + 1)]
           for _ in range(len_seq + 1)]
    assign_ith_bool_1(ans[0][0], from_edit_to_num(0, 0, 0, indel_limit))
    for i in range(1, indel_limit + 1):
        assign_ith_bool_1(ans[0][i], from_edit_to_num(0, i, 0, indel_limit))
    for i in range(1, indel_limit + 1):
        assign_ith_bool_1(ans[i][0], from_edit_to_num(0, 0, i, indel_limit))
    return ans

def from_number_to_edit(edit_digit: int, indel_limit: int) -> tuple:
    """
    Converts the corresponding number to the edit record.
    :param edit_digit: Encoded number
    :param indel_limit: The limit of indel
    :return: (substitution, insertion, deletion)
    """
    num_del = edit_digit % (indel_limit + 1)
    num_ins = (edit_digit // (indel_limit + 1)) % (indel_limit + 1)
    num_sub = edit_digit // ((indel_limit + 1) ** 2)
    return (num_sub, num_ins, num_del)

def update_dp(dp: list, s1: str, s2: str, i: int, j: int, record_num: int, indel_limit: int):
    """
    Update the dp matrix.
    On the one hand, this method can obtain reachability information.
    On the other hand, it can avoid the use of dynamic memory, and facilitate GPU acceleration.
    :param dp: Dynamic programming matrix.
    :param s1: First string.
    :param s2: Second string.
    :param i: Row index.
    :param j: Column index
    :param record_num: Total record number
    :param indel_limit: Limit of indel
    :return: None.
    """
    if s1[i - 1] == s2[j - 1]:
        dp[i][j] = dp[i - 1][j - 1]
    else:
        for k in range(record_num):
            num_sub, num_ins, num_del = from_number_to_edit(k, indel_limit)
            if num_sub > 0:
                k_s = from_edit_to_num(num_sub - 1, num_ins, num_del, indel_limit)
                v_s = get_ith_bool_val(dp[i - 1][j - 1], k_s)
                if v_s == 1:
                    assign_ith_bool_1(dp[i][j], k)
                    continue
            if num_ins > 0:
                k_i = from_edit_to_num(num_sub, num_ins - 1, num_del, indel_limit)
                v_i = get_ith_bool_val(dp[i][j - 1], k_i)
                if v_i == 1:
                    assign_ith_bool_1(dp[i][j], k)
                    continue
            if num_del > 0:
                k_d = from_edit_to_num(num_sub, num_ins, num_del - 1, indel_limit)
                v_d = get_ith_bool_val(dp[i - 1][j], k_d)
                if v_d == 1:
                    assign_ith_bool_1(dp[i][j], k)
                    continue


def refined_levenshtein(seq1: str, seq2: str, restriction: list,) -> bool:
    """
    This function consider the sequence with same length.
    Check if one of them can reach the other in certain restriction.
    :param seq1: First input sequence
    :param seq2: Second input sequence
    :param restriction: [Substitution, Insertion and deletion]
    :return: Reachable or not.
    """
    assert isinstance(seq1, str) and isinstance(seq2, str), "Two sequence must be both string." \
                                                            " Type of the first string is: %s," \
                                                            " Type of the second string is: %s" \
                                                            % (str(type(seq1)), str(type(seq2)))
    assert len(restriction) == 2, "Input of restriction is wrong. Its length must be 2 but not %d" % (len(restriction))
    assert isinstance(restriction[0], int) and isinstance(restriction[1], int), "Two elements of restriction must be integer." \
                                                                                " The first is: %s," \
                                                                                " The second is: %s" \
                                                                                % (str(type(restriction[0])), str(type(restriction[1])))
    n = len(seq1)
    m = len(seq2)
    assert n == m, 'Different length of two sequence.' \
                   ' The first one is: %d,' \
                   ' The second one is: %d.' \
                   % (n, m)

    mutation_limit = restriction[0]
    indel_limit = restriction[1]
    edit_limit = (mutation_limit + 1) * (indel_limit + 1) ** 2

    require_num_int8 = num_of_int8(edit_limit)

    dp = dp_initialization(n, indel_limit, require_num_int8)
    for i in range(1, n + 1):
        for j in range(-indel_limit, indel_limit + 1):
            id_row = i
            id_col = j + i
            if id_row > 0 and id_row < n + 1 and id_col > 0 and id_col < n + 1 :
                update_dp(dp, seq1, seq2, id_row, id_col, edit_limit, indel_limit)
    for item in dp[-1][-1]:
        if item !=0:
            return True
    return False

#########################################################################################

#####################################GPU Algorithm#######################################

#########################################################################################
