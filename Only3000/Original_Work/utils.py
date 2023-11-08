import numpy as np
import numba as nb
import numba.cuda as cuda
import random
import math

from functools import reduce
import operator

################ Original Levenshtein Algorithm ##############################
def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    # for item in dp:
    #     print(item, )
    return dp[m][n]
#############################################################################

################ Modified Algorithm  ########################################
def ij2x(i, j):
    return j + 1

def ij2y(i, j):
    return i - j + 1

def xy2i(x, y):
    return x + y - 2

def xy2j(x, y):
    return x - 1

def dp_get(dp, x, y):
    if x == 0:
        return y
    elif y == 0:
        return x
    else:
        return dp[xy2i(x, y)%3][xy2j(x, y)]

def dp_assign(dp, x, y, val):
    dp[xy2i(x, y) % 3][xy2j(x, y)] = val

def dp_update(dp, x, y, flag):
    if flag:
        dp_assign(dp, x, y, dp_get(dp, x - 1, y - 1))
    else:
        val = min(dp_get(dp, x - 1, y),
                  dp_get(dp, x, y - 1),
                  dp_get(dp, x - 1, y - 1)) + 1
        dp_assign(dp, x, y, val)

def code_charAt(c_id, ith):
    return (c_id % (4 ** (ith + 1))) // (4 ** ith)

def mod_l_distance(w1, w2, n, ):
    dp = [[0 for j in range(n)] for i in range(3)]
    for i in range(2 * n - 1):
        if i <= n - 1:
            for j in range(i + 1):
                x = ij2x(i, j)
                y = ij2y(i, j)
                flag = w1[y - 1] == w2[x - 1]
                dp_update(dp, x, y, flag)
        else:
            for j in range(i - n + 1, n):
                x = ij2x(i, j)
                y = ij2y(i, j)
                flag = w1[y - 1] == w2[x - 1]
                dp_update(dp, x, y, flag)
        # print(dp)
    return dp[(2*n-2)%3][n-1]

#############################################################################

################ utils for Cuda Version #####################################
@cuda.jit(device=True)
def cu_ij2x(i, j):
    return j + 1

@cuda.jit(device=True)
def cu_ij2y(i, j):
    return i - j + 1

@cuda.jit(device=True)
def cu_xy2i(x, y):
    return x + y - 2

@cuda.jit(device=True)
def cu_xy2j(x, y):
    return x - 1

@cuda.jit(device=True)
def cu_dp_get(dp, x, y):
    if x == 0:
        return y
    elif y == 0:
        return x
    else:
        return dp[cu_xy2i(x, y)%3][cu_xy2j(x, y)]

@cuda.jit(device=True)
def cu_dp_assign(dp, x, y, val):
    dp[cu_xy2i(x, y) % 3][cu_xy2j(x, y)] = val

@cuda.jit(device=True)
def cu_dp_update(dp, x, y, flag):
    if flag:
        cu_dp_assign(dp, x, y, cu_dp_get(dp, x - 1, y - 1))
    else:
        val = min(cu_dp_get(dp, x - 1, y),
                  cu_dp_get(dp, x, y - 1),
                  cu_dp_get(dp, x - 1, y - 1)) + 1
        cu_dp_assign(dp, x, y, val)

#############################################################################

################ Generator tools ############################################

nuc2code = {'A':0,'G':1,'C':2,'T':3}
code2nuc = {0:'A',1:'G',2:'C',3:'T'}
def seq_nuc2code(seq: str) -> list:
    ans = []
    for i in seq:
        ans.append(nuc2code[i])
    return ans

def seq_code2nuc(code: list) -> str:
    ans = ''
    for i in code:
        ans += code2nuc[i]
    return ans

def read_code_table(file_path):
    with open(file_path, 'r') as file:
        code_table = [line.strip() for line in file]

    return code_table

def save_code_table(code_table, file_path):
    with open(file_path, 'w') as file:
        for code in code_table:
            file.write(code + '\n')


def filter_condition(codelist, duplicate=4):
    hist = [0,0,0,0]
    tag = 0
    if codelist[0] == codelist[1]:
        return False
    if codelist[-1] == codelist[-2]:
        return False
    for i in range(len(codelist)):
        hist[codelist[i]] += 1

        if i > 0:
            if codelist[i] == codelist[i-1]:
                tag+=1
            else:
                tag = 0
        if tag >= duplicate:
            return False
    if hist[1]+hist[2] != len(codelist)//2:
        return False
    return True


def convert_to_custom_base(n, bases):
    digits = []
    for i in range(len(bases)):
        base = bases[i]
        digit = n % base
        digits.append(digit)
        n //= base
    return digits[::-1]

def multiply_elements(lst):
    return reduce(operator.mul, lst)
#############################################################################

def wr(idt, step, index, gps, cr):
    ans = idt
    for i in range(step):
        ans //= gps[i]
    ans %= gps[step]

    size = int(np.ceil(cr / gps[step]))
    if index == 0:
        ans = ans * size
        print(ans, step, 'cpu')
    else:
        ans = min((ans + 1) * size, cr)
    return ans

@cuda.jit
def work_range(id_t, step, index, group_per_step, code_range):
    ans = id_t
    for i in range(step):
        ans //= group_per_step[i]
    ans %= group_per_step[step]
    size = int(math.ceil(code_range / group_per_step[step]))
    if index == 0:
        ans = ans * size
    else:
        ans = min((ans + 1) * size, code_range)
    return ans
#############################################################################

################ Optimized editing distance #################################
def cond_pass(shift, len1, len2, ind_x, ind_y, del_ins_num=1):
    assert shift == 1 or shift == -1, 'error input'
    assert abs(len1 - len2) <= del_ins_num and abs(shift) <= del_ins_num, 'edit error cannot match'
    if shift == 1:
        # Left align
        ans = (ind_x == 0 and ind_y == 0)
        if len1 == len2 + 1:
            # delete
            ans = ans or (ind_x == len1 - 2 and ind_y == 2) or (ind_x == len1 - 1 and ind_y != 0)
        elif len1 == len2:
            ans = ans or (ind_x == len1 - 1 and ind_y == 2)
        else:
            ans = ans
    if shift == -1:
        ans = (ind_x == len1 - 1 and ind_y == 2)
        if len1 == len2 + 1:
            ans = ans or (ind_x == 0 and ind_y != 2) or ( ind_x == 1 and ind_y == 0)
        elif len1 == len2:
            ans = ans or (ind_x == 0 and ind_y == 0)
        else:
            ans = ans
    return ans

def update_dp4common(dp, str1, str2, ind_x, ind_y) -> bool:
    if str1[ind_x] == str2[ind_y]:
        if ind_x != 0 and ind_y != 0:
            dp[ind_x][ind_y] = dp[ind_x - 1][ind_y - 1] + 1
        else:
            dp[ind_x][ind_y] = 1
        return True
    else:
        return False

def max_val_ij(dp, ind_x, ind_y, max_val, max_x, max_y, start1, start2):
    x = ind_x + start1
    y = ind_y + start2
    if dp[ind_x][ind_y] > max_val:
        max_val = dp[ind_x][ind_y]
        max_x = ind_x
        max_y = ind_y
    elif dp[ind_x][ind_y] == max_val:
        if abs(x - y) < abs(max_x - max_y):
            max_x = ind_x
            max_y = ind_y
    return max_val, max_x, max_y

def split_by_common(s1, s2, ind_i, ind_j, l, start1, start2):
    if l == 0:
        return [(), [(s1, s2), ()], [(start1, start2), ()]]
    else:
        seg1 = (ind_i - l + 1, ind_i + 1)
        seg2 = (ind_j - l + 1, ind_j + 1)
        ans = [(s1[seg1[0]:seg1[1]],), [(), ()], [(), ()]]
        if seg1[0] != 0 or seg2[0] != 0:
            ans[1][0] = (s1[: seg1[0]], s2[: seg2[0]])
            ans[2][0] = (start1, start2)
        if seg1[1] != len(s1) or seg2[1] != len(s2):
            ans[1][1] = (s1[seg1[1]: ], s2[seg2[1]: ])
            ans[2][1] = (start1 + ind_i + 1, start2 + ind_j + 1)
    return ans

def find_common_substring(s1: str, s2: str, org_len: int, start1: int=0, start2: int=0, shift_num: int=1):
    n = len(s1)
    m = len(s2)
    max_val = 0
    max_i = -1
    max_j = -1
    dp = np.zeros([n,m], np.int8)
    for i in range(n):
        for j in range(-shift_num, shift_num + 1):
            x = start1 + i
            y = start2 + i + j
            dp_row = i
            dp_col = i + j
            c1 = x >= 0 and y >= 0 and x < org_len and y < org_len
            c2 = dp_col >= 0 and dp_row >= 0 and dp_col < len(s2) and dp_row < len(s1)
            if c1 and c2:
                flag = update_dp4common(dp, s1, s2, dp_row, dp_col)
                if flag:
                    max_val, max_i, max_j = max_val_ij(dp, dp_row, dp_col, max_val, max_i, max_j, start1, start2)
    ans = split_by_common(s1, s2, max_i, max_j, max_val, start1, start2)
    return ans

def split_segment_same(str1, str2, shift_num=1):
    c1= str1
    c2 = str2
    L = len(c1)
    err_list = []
    work_list = [(c1, c2, 0, 0)]
    while True:
        if work_list == []:
            break
        item = work_list.pop()
        print(item,'xx')
        comm ,rest, starts = find_common_substring(item[0],item[1], L,item[2], item[3], shift_num)
        print(rest, starts)
        if comm == ():
            for item2 in rest:
                if item2 != ():
                    err_list.append(item2)
        else:
            for i in range(len(rest)):
                item2 = rest[i]
                if item2 != ():
                    if '' in item2:
                        err_list.append(item2)
                    else:
                        work_list.append((item2[0], item2[1], starts[i][0], starts[i][1]))
    return err_list

def calculate_error_type(s1, s2):
    err_list = split_segment_same(s1, s2)
    ans = [0, 0, 0] # mutation, insertion, deletion
    for item in err_list:
        if item[0] == '':
            ans[1] += len(item[1])
        else:
            if len(item[0]) == len(item[1]):
                ans[0] += len(item[0])
            elif len(item[0]) < len(item[1]):
                ans[0] += len(item[0])
                ans[1] += len(item[1]) - len(item[0])
            else:
                ans[0] += len(item[1])
                ans[2] += len(item[0]) - len(item[1])
    return ans

def wet_process4seq(seq, need_log = True):

    mutate_number = 2
    insert_number = 1
    delete_number = 1
    target_dna_sequence = seq
    error_log = [[],[],[]]
    for _ in range(mutate_number):
        location = random.randint(0, len(target_dna_sequence) - 1)
        error_log[0].append(location)
        source = target_dna_sequence[location]
        mutate_candidate = [i for i in ['A', 'G', 'C', 'T'] if i !=source]
        target_dna_sequence = target_dna_sequence[: location] + random.choice(mutate_candidate) + target_dna_sequence[location + 1:]

    for _ in range(insert_number):
        location = random.randint(0, len(target_dna_sequence))
        error_log[1].append(location)
        target_dna_sequence = target_dna_sequence[:location] + random.choice(["A", "C", "G", "T"]) + target_dna_sequence[location:]

    for _ in range(delete_number):
        location = random.randint(0, len(target_dna_sequence) - 1)
        error_log[2].append(location)
        target_dna_sequence = target_dna_sequence[:location] + target_dna_sequence[location + 1:]

    if need_log:
        print('Mutation location: ', error_log[0])
        print('Insertion location: ', error_log[1])
        print('Deletion location: ', error_log[2])
    return target_dna_sequence
#############################################################################

################ Accessibility under restrictions ###########################
def accessibility_rest(s1, s2, restriction=[4,2,2]) -> bool:
    # edit: [M I D]
    n = len(s1)
    m = len(s2)
    dp = [[[] for j in range(m+1)] for i in range(n+1)]
    for i in range(restriction[1]+1):
        dp[0][i].append([0,i,0])
    for j in range(1, restriction[2]+1):
        dp[j][0].append([0,0,j])

    for x in range(1, n + 1):
        for y in range(-restriction[1], restriction[1] + 1):
            i = x
            j = x+y
            if j >= 1 and j <= m:
                if s1[i - 1] == s2[j - 1]:
                    for item in dp[i - 1][j - 1]:
                        if item[0] <= restriction[0] and item[1] <= restriction[1] and item[2] <= restriction[2]:
                            dp[i][j].append(item)
                else:
                    for item in dp[i - 1][j - 1]:
                        n_item = [item[0] + 1, item[1], item[2]]
                        if n_item[0] <= restriction[0] and n_item[1] <= restriction[1] and n_item[2] <= restriction[2]:
                            dp[i ][j ].append(n_item)
                    for item in dp[i - 1][j]:
                        n_item = [item[0], item[1], item[2] + 1]
                        if n_item[0] <= restriction[0] and n_item[1] <= restriction[1] and n_item[2] <= restriction[2]:
                            dp[i][j].append(n_item)
                    for item in dp[i ][j - 1]:
                        n_item = [item[0], item[1] + 1, item[2]]
                        if n_item[0] <= restriction[0] and n_item[1] <= restriction[1] and n_item[2] <= restriction[2]:
                            dp[i][j].append(n_item)
    # for item in dp:
    #     print(item)
    # print(dp[-1][-1])
    return dp[-1][-1] != []

#############################################################################

################ Sequence Generation ########################################
def bin_seq_generation(n: int) -> str:
    ans = ''.join([str(np.random.randint(0, 2)) for _ in range(n)])
    return ans

#############################################################################
if __name__ == '__main__':
    # gps = np.array([512, 512, 1, 1],dtype=np.int32)
    # idt = 512*63
    # print(idt)
    # print([wr(idt, i, 0, gps, 125928) for i in range(len(gps))])
    # print([wr(idt, i, 1, gps, 125928) for i in range(len(gps))])
    #.
    # CDL = 125928
    # cu_func4wr[2,2](cuda.to_device(gps))
    # T = ['TCTTTTCTCCCG', 'TCTGGGGAGATA', 'CACACAAAAGCG', 'GAAGGCCCTTTA']
    # x = 'CTTTTCTACCGA'
    #
    # for i in T:
    #     print(levenshtein_distance(x,i))

    # Test condition pass function
    if True:
        s1 = 'ACTCAT'
        s2 = 'AGCATG'
        print(accessibility_rest(s1,s2, [2,1,1]))

    if True:
        t1 = ['TCTTCTTCCG', 'TCCGCAGAAT', 'GATGTAAGGC', 'GAAGGCCTTA']
        t2 = ['TCTTCTTCCG', 'TCCGCAGAAT', 'GAGACCTCTA', 'ATAAGGTGGC']

        for _ in range(10000):
            item_index = random.randint(0,3)
            seg1 = t1[item_index]
            seg2 = wet_process4seq(seg1, False)
            ans = 0
            for i in range(4):
                item = t1[i]

                if accessibility_rest(item, seg2, [2,1,1]):
                    ans = i
            if ans != item_index:
                print(seg1, seg2)

    if False:
        inputs = [[1, 10, 10, i ,j ] for i in range(10) for j in range(3)]
        inputs = inputs+[[2, 10, 9, 1,2]]
        inputs = inputs + [[-1, 5, 5, i, j] for i in range(5) for j in range(3)]
        inputs = inputs + [[-1, 5, 6, i, j] for i in range(5) for j in range(3)] +[[-1, 5, 4, i, j] for i in range(5) for j in range(3)]
        for item in inputs:
            try:
               result = cond_pass(item[0],item[1],item[2],item[3],item[4])
            except AssertionError as e:
                print(str(e) + ',error is ', item)
            else:
                print(result, item, item[3], item[3] + item[4] - 1)
    if False:
        s1 = ''.join([random.choice(['A','G','C','T']) for i in range(10)])
        s2 = wet_process4seq(s1)
        find_common_substring(s1, s2[:-1], len(s1), 0, 0, 1)

    if False:
        s1 = ''.join([random.choice(['A','G','C','T']) for i in range(10)])
        s2 = wet_process4seq(s1)

        s1 = 'GGGATTTAAA'
        s2 = 'AGGTATAAAA'
        print('s1:',s1, ' s2:',s2)
        print(find_common_substring(s1, s2, len(s1),0,0,1),' cm substring')
        print(split_segment_same(s1,s2))
        # print(calculate_error_type(s1,s2))
        print(levenshtein_distance(s1,s2))
        # print(find_common_substring('GCG','AG', len(s1), 7, 8, 1))

    if False:
        s1 = ''.join([random.choice(['A', 'G', 'C', 'T']) for i in range(10)])
        s2 = wet_process4seq(s1)
        # s1 = 'AGAAGAAGGC'
        # s2 = 'AGAAGGCACA'
        print(s1, s2)
        accessibility_rest(s1,s2, [4,2,2])

    # w1 = '1213310311'
    # w2 = '1301131230'
    # print(w1,w2)
    # print(levenshtein_distance(w1, w2))
    # print(mod_l_distance(w1, w2, len(w1)))
