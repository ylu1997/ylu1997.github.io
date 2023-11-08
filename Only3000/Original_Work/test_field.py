from utils import accessibility_rest, read_code_table, seq_code2nuc, filter_condition
import random
import numpy as np
from multiprocessing import  Process, Queue, cpu_count
import os
import time

def seq_generate(n: int):
    seq = ''.join([random.choice(['A','G','C','T']) for _ in range(n)])
    return seq

def check_distance(ans, step):
    item0 = ans[step]
    for item1 in ans[:step]:
        if accessibility_rest(item0, item1,[4,2,2]):
            return False
    return True

def para_filt_scope(selected_codes, scope, queue):
    ans = []
    is_append = True
    iter_num = 0
    for item in scope:
        for item2 in selected_codes:
            flag = accessibility_rest(item, item2, [4,2,2])
            if flag:
                is_append = False
                break
        iter_num += 1
        # if iter_num % 100 == 0:
        #     print('Process ID:%d. Work:%d / %d. AcceNum: %d'%(os.getpid(), iter_num, len(scope), len(ans)))
        if is_append:
            ans.append(item)
        is_append = True
    queue.put(ans)

def get_next_scope(selected, tmp_scope):
    result = []
    p = cpu_count() - 1

    scope = tmp_scope
    queue = Queue()
    p_num = p if len(scope) >= p else len(scope)
    block_size = np.ceil(len(scope) / p_num)
    work_scopr = [scope[i * int(block_size): min((i + 1) * int(block_size), len(balanced_codes))] for i in range(p_num)]
    jobs = []
    for i in range(p_num):
        p = Process(target=para_filt_scope, args=(selected, work_scopr[i], queue))
        jobs.append(p)
        p.start()

    for i in jobs:
        while i.is_alive():
            while False == queue.empty():
                result += queue.get()
                time.sleep(2)

    for p in jobs:
        p.join()
    return  result

def permutation4nuc(tab, per):
    ans = []
    for item in tab:
         ans.append(''.join([per[i] for i in item]))
    return ans

code_file_name = 'nuc.txt'
balanced_codes = read_code_table(code_file_name)

def shift_reachable(tab1, tab2):
    for item1 in tab1:
        for item2 in tab2:
            if accessibility_rest(item1, item2, [0,1,1]):
                return False
    return True

if __name__ == '__main__':
    if True:
        per_idx = [(0, 1, 2, 3), (1, 0, 3, 2), (1, 2, 3, 0), (1, 3, 0, 2), (2, 0, 3, 1), (2, 3, 0, 1), (2, 3, 1, 0),
                   (3, 0, 1, 2)]
        per_idx = [(0,1,2,3),(3,2,1,0), (0,2,1,3),(3,1,2,0),(1,0,3,2),(2,3,0,1),]
        nuc = ['A', 'G', 'C', 'T']
        tab = ['TCTTCTTCCG', 'TCCGCAGAAT', 'GAGACCTCTA', 'ATAAGGTGGC']
        per_dict = [{nuc[i]: nuc[item[i]] for i in range(4)} for item in per_idx]
        tabs = [permutation4nuc(tab, item) for item in per_dict]
        for i in range(len(tabs)):
            for j in range(1+i,len(tabs)):
                tab1 = tabs[i]
                tab2 = tabs[j]
                print(shift_reachable(tab1, tab2), i,j)
        print(tabs)
        for tab in tabs:
            for item in tab:
                if filter_condition([nuc.index(i) for i in item], 2) == False:
                    print(tab)
                    break
        pass
    if False:
        tab = ['TCTTCTTCCG', 'TCCGCAGAAT', 'GAGACCTCTA', 'ATAAGGTGGC']
        d = {'A':'T','T':'A','G':'C','C':'G'}
        tab2 = [''.join([d[i] for i in item]) for item in tab]
        tab += tab2
        tab = ['AGCCCTT',
               'TTAGGAC']
        print(tab2)
        for i in range(len(tab)):
            for j in range(i+1,len(tab)):
                if accessibility_rest(tab[i],tab[j],[4,2,2]):
                    print(tab[i],tab[j],i,j)

        print(len(tab))

    if False:
        paths = [[[balanced_codes[-1]], balanced_codes[:-1]]]
        while True:
            if paths == []:break
            item = paths.pop()
            path = item[0]
            scope = item[1]
            if scope == []:continue
            paths.append([path[:-1] + [scope[-1]], scope[:-1]])

            new_scope = get_next_scope(path, scope)

            if new_scope != []:
                new_path = path + [new_scope[-1]]
                new_scope = new_scope[:-1]
                paths.append([new_path, new_scope])
            else:
                print(new_path)
    if False:
        result = []
        selected = [balanced_codes[0],'ATGGCGCTTA']
        p = 7
        scope = balanced_codes
        queue = Queue()
        p_num = p if len(scope) >= p else len(scope)
        block_size = np.ceil(len(scope) / p_num)
        work_scopr = [scope[i*int(block_size): min((i+1)*int(block_size), len(balanced_codes))] for i in range(p_num)]
        jobs = []
        for i in range(p_num):
            p = Process(target=para_filt_scope, args=(selected, work_scopr[i], queue))
            jobs.append(p)
            p.start()

        for i in jobs:
            while i.is_alive():
                while False == queue.empty():
                    result+=queue.get()
                    time.sleep(2)

        for p in jobs:
            p.join()

        # result = [queue.get() for i in range(p_num)]
        # print(queue.get())

    if False:
        # balanced_codes = balanced_codes[:7500]
        index_count = [0, 7540, 0, 0]
        wr = [[0, len(balanced_codes)], [0, len(balanced_codes)], [0, len(balanced_codes)], [0, len(balanced_codes)]]
        step = 0

        iter_num = 0
        while True:
            if index_count[0] >= wr[0][1]:
                break
            else:
                if step == 0:
                    step += 1
                elif step > 0 and step < len(index_count):
                    if index_count[step] < wr[step][1]:
                        if check_distance([balanced_codes[i] for i in index_count], step):
                            step += 1
                        else:
                            index_count[step] += 1
                            for i in range(step, len(index_count)):
                                index_count[i] = index_count[step]

                    else:
                        # index_count[step] = wr[step][0]
                        step -= 1
                        index_count[step] += 1
                        for i in range(step, len(index_count)):
                            index_count[i] = index_count[step]
                else:
                    print(index_count)
                    found = True
                    break
            if iter_num % 500 ==0:
                print(index_count)
            iter_num += 1