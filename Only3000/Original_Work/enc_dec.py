import random
import torch as tc
from functorch import vmap
import numpy as np
from system_trans import bin2dec

def lcs_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return n + m - 2 * dp[m][n]

def nearest_seg(seg, codetab):
    index = np.argmin([lcs_distance(seg, item) for item in codetab])
    return codetab[index]

def correction4sequence(sequence, codetab):
    ans_seq = ''
    i0 = 0
    while True:
        i1 = min([i0+12, len(sequence)])
        if abs(i1 - i0) < 11:
            break
        else:
            seg = sequence[i0: i1]
            if seg in codetab:
                ans_seq += seg
                i0 += 12
            else:
                ans_seq += nearest_seg(seg, codetab)
                if sequence[i1 - 1: i1 + 11] in codetab:
                    i0 = i1 - 1
                elif sequence[i1 + 1: i1 + 13] in codetab:
                    i0 = i1 + 1
                else:
                    i0 = i1
    return ans_seq


nuc_tab = ['A', 'T', 'G', 'C']
# 00 -> 0; 01 -> 1; 10 -> 2; 11 -> 3.
tabs = [['CTCCCCTCTTTA', 'CTCAAAAGAGCG', 'TGTGTGGGGATA', 'AGGAATTTCCCG'],
        ['ATAAAATATTTC', 'ATACCCCGCGAG', 'TGTGTGGGGCTC', 'CGGCCTTTAAAG'],
        ['CACCCCACAAAT', 'CACTTTTGTGCG', 'AGAGAGGGGTAT', 'TGGTTAAACCCG'],
        ['GTGGGGTGTTTA', 'GTGAAAACACGC', 'TCTCTCCCCATA', 'ACCAATTTGGGC'],
        ['GAGGGGAGAAAT', 'GAGTTTTCTCGC', 'ACACACCCCTAT', 'TCCTTAAAGGGC'],
        ['AGAAAAGAGGGT', 'AGATTTTCTCAC', 'GCGCGCCCCTGT', 'TCCTTGGGAAAC'],
        ['CGCCCCGCGGGA', 'CGCAAAATATCT', 'GTGTGTTTTAGA', 'ATTAAGGGCCCT'],
        ['TCTTTTCTCCCG', 'TCTGGGGAGATA', 'CACACAAAAGCG', 'GAAGGCCCTTTA']]

tabs_tensor = tc.tensor([[[nuc_tab.index(i) for i in c] for c in t] for t in tabs])

class Coding_Core():
    def __init__(self, level=11, index_unit=10, seq_len = 132,):
        self.total_unit = level
        self.index_unit = index_unit
        self.seq_len = seq_len

        self.tab_num = tc.tensor(tabs_tensor.shape[0]).item()
        self.bin_len = tc.log2(tc.tensor(tabs_tensor.shape[1])).type(tc.int8).item()
        self.nuc_len = tc.tensor(tabs_tensor.shape[2]).item()

        self.classified_seqs = [[] for i in range(self.tab_num)]

    def classify_header(self, seq):
        # Determine whether it is the sequence for the current header.
        s = abs(len(seq) - self.seq_len)
        return s <= 1

    def seq_num_per_tab(self):
        # Number of sequences in each code table.
        return 2 ** (self.bin_len * self.index_unit)

    def max_seq_num(self):
        # Maximum number of sequences
        return self.tab_num * self.seq_num_per_tab()

    def bin_vol_per_seq(self):
        # Binary storage limit per sequence
        return self.bin_len * self.info_unit()

    def bin_vol_per_tab(self):
        # Binary storage limit per code table
        return self.bin_vol_per_seq() * self.seq_num_per_tab()

    def max_bin_vol(self):
        # Binary storage limit
        return self.bin_vol_per_seq() * self.max_seq_num()

    def max_nuc_num(self):
        # Nucleotide number limit
        return self.seq_len * self.max_seq_num()

    def info_unit(self):
        return self.total_unit - self.index_unit

    def encoding_tab(self, seq: tc.tensor, tab_index: int) -> tc.tensor:
        """
        :param seq: (N, 1) It is sequence of nucleotide index, each index bit equal self.bin_len binary bits.
        :return: (N', seq_len)
        """
        assert (seq.shape[0] * self.bin_len) % self.bin_vol_per_seq() == 0, 'Need to padding 0.' + str(self.bin_vol_per_seq())
        assert (seq.shape[0] * self.bin_len) <= self.max_bin_vol(), 'Overflow.'
        m2tab_index = vmap(lambda x: tabs_tensor[tab_index][x][0],in_dims=0)
        ans = m2tab_index(seq) # each row is index of nucleotide unit, each column is index of nucleotide
        ans = ans.reshape(ans.shape[0]//self.info_unit(), ans.shape[1]*self.info_unit())
        index = tc.arange(0, ans.shape[0])
        index = (vmap(lambda x:tc.stack(tuple([x & (2 ** (2 * self.index_unit - i - 1)) for i in range(2 * self.index_unit)])).type(tc.bool)))(index)
        index = (vmap(lambda x:tc.stack(tuple([x[2 * i + 1] + 2 * x[2 * i] for i in range(self.index_unit)]))))(index)
        index = m2tab_index(index.reshape(index.shape[0]*index.shape[1],1))
        index = index.reshape(index.shape[0]//(self.index_unit), index.shape[1]*self.index_unit)
        ans = tc.concat((index,ans),dim=1)
        tail_num = self.seq_len - self.total_unit * self.nuc_len
        if tail_num != 0:
            tail = tc.tensor([2*(i%2) for i in range(tail_num)]).reshape(1,tail_num)
            tail = tail.repeat(ans.shape[0], 1)
            ans = tc.concat((ans,tail),dim=1)
        return ans

    def encoding(self, seq: tc.tensor) -> tc.tensor:
        """
        :param seq: (N,1) It is about index of each table
        :return:
        """
        assert seq.shape[0] * self.bin_len <= self.max_bin_vol(), 'Overflow.'
        k = self.bin_vol_per_tab() // self.bin_len
        for i in range(self.tab_num):
            print('tabnum:',i)
            in_bin = seq[i * k : i * k + k, :]
            if in_bin.shape[0] == 0:
                break
            if i == 0:
                ans = self.encoding_tab(in_bin, i)
            else:
                ans = tc.cat((ans, self.encoding_tab(in_bin,i)),dim=0)
        return ans

    def to_nuc_seqs(self, seqs: tc.tensor) -> list:
        # Turn digital sequences to nucleotide sequences
        seqs = seqs.tolist()
        ans = []
        for item in seqs:
            tmp=''
            for i in item:
                tmp+=nuc_tab[i]
            ans.append(tmp)
        return ans

    def nuc2bin4char(self, c, tab_index=0):
        # Correspondence of nucleotide units to binary units
        assert c in tabs[tab_index], "The nucleotide sequence ("+ c +") is not in the table " + str(tab_index) + '.'
        return tabs[tab_index].index(c)

    def nuc2bin4seq(self, seq, tab_index=0):
        # Nucleotide-binary sequence correspondence regarding sequences
        assert len(seq)%self.nuc_len==0, 'Wrong sequence length.'
        ans = []
        for i in range(len(seq)//self.nuc_len):
            start_pos = self.nuc_len * i
            end_pos = start_pos + self.nuc_len
            ans += [self.nuc2bin4char(seq[start_pos: end_pos], tab_index)]
        return ans

    def index_nuc_len(self):
        # The nucleotide area for index
        return self.index_unit * self.nuc_len

    def collecte_seq(self, seq: str):
        if abs(len(seq) - self.seq_len) <=1 :
            # It is belong to this head

            # Determine which code table
            ans = [0 for i in range(self.tab_num)]
            in_tab = False
            for i in range(len(seq) // self.nuc_len):
                for j in range(self.tab_num):
                    for bias in range(-1, 2):
                        start = i * self.nuc_len + bias
                        end = start + self.nuc_len
                        seg = seq[start:end]
                        if seg in tabs[j]:
                            ans[j] += 1
                            in_tab = True
                            break
                    if in_tab:
                        in_tab = False
                        break
            ind = np.argmax(ans)

            # Unify the length
            if self.seq_len - len(seq) == 1:
                seq = seq + 'A'
            elif self.seq_len - len(seq) == -1:
                seq = seq[:-1]
            else:
                seq = seq
            # Do correction
            corrected_seq = correction4sequence(seq, tabs[ind])
            nuc_index = corrected_seq[:self.index_nuc_len()]
            nuc_info = corrected_seq[self.index_nuc_len():]
            bin_index = self.nuc2bin4seq(nuc_index, ind)
            bin_info = self.nuc2bin4seq(nuc_info, ind)
            self.classified_seqs[ind].append(bin_index+bin_info)

    def decoding(self):
        seqs = []
        for item in self.classified_seqs:
            if item != []:
                tc_seq = tc.tensor(item)
                index = tc_seq[:, :self.index_unit]
                info = tc_seq[:, self.index_unit:]
                index = vmap(lambda x: sum([x[i] * 4**(self.index_unit - i - 1) for i in range(self.index_unit)]))(index )
                # info = vmap(lambda x: tc.stack(tuple([x[i//self.bin_len]& (2**(self.bin_len - (i%self.bin_len)-1)) for i in range(self.info_unit() * self.bin_len)])).type(tc.bool),in_dims=0)(info)
                info = info.tolist()
                info = sorted(info, key=lambda x: index[info.index(x)])
                sorted_info = tc.tensor(info)
                seqs.append(sorted_info)
        if seqs!=[]:
            ans = [tc.cat(seqs,dim=0).reshape(-1)]
        else:
            ans = []
        return ans

class Coding_Cluster():
    def __init__(self, ind_unit=[[1],[1,1,3,3],[3,3 ,3,3]]):
        self.cluster = [Coding_Core(level=11, index_unit=ind_unit[0][0],seq_len=132),
                        Coding_Core(level=10, index_unit=ind_unit[1][0], seq_len=120),
                        Coding_Core(level=10, index_unit=ind_unit[1][1], seq_len=123),
                        Coding_Core(level=10, index_unit=ind_unit[1][2], seq_len=126),
                        Coding_Core(level=10, index_unit=ind_unit[1][3], seq_len=129),
                        Coding_Core(level=9, index_unit=ind_unit[2][0], seq_len=108),
                        Coding_Core(level=9, index_unit=ind_unit[2][1], seq_len=111),
                        Coding_Core(level=9, index_unit=ind_unit[2][2], seq_len=114),
                        Coding_Core(level=9, index_unit=ind_unit[2][3], seq_len=117),]

    def max_seq_num(self):
        # Maximum number of sequence total.
        return sum([item.max_seq_num() for item in self.cluster])

    def max_nuc_num(self):
        # Maximum number of nucleotide
        return sum([item.max_nuc_num() for item in self.cluster])

    def max_vol_num(self):
        # Maximum number of nucleotide
        return sum([item.max_bin_vol() for item in self.cluster])

    def check_supp(self, sequence):
        # Returns the number of zeros to replenish
        n = len(sequence)
        for item in self.cluster:
            if n >= item.max_bin_vol()//item.bin_len:
                n -= item.max_bin_vol()//item.bin_len
            else:
                n = (item.bin_vol_per_seq()//item.bin_len - n % (item.bin_vol_per_seq()//item.bin_len))\
                    % (item.bin_vol_per_seq()//item.bin_len)
                break
        return n

    def do_encoding(self, index_sequence: tc.tensor) -> list:
        # Processing binary sequences into a list related to nucleotide sequences
        assert index_sequence.shape[0] <= self.max_vol_num(), 'Overflow'
        next_bin = index_sequence
        ans = []
        for header in self.cluster:
            length_per_group = header.max_bin_vol() // header.bin_len
            tmp_bin = next_bin[:length_per_group]
            next_bin = next_bin[length_per_group:]
            if tmp_bin.shape[0] == 0:
                break
            else:
                ans += header.to_nuc_seqs(header.encoding(tmp_bin))
        return ans

    def do_decoding(self, seqs):
        ans = []
        for seq in seqs:
            for core in self.cluster:
                core.collecte_seq(seq)
        for core in self.cluster:
            ans += core.decoding()
        res = ans[0]
        for item in ans[1:]:
            res = tc.cat((res,item))
        return res

def wet_process(source_dna_sequences):
    target_dna_sequences = []
    for index, source_dna_sequence in enumerate(source_dna_sequences):
        mutate_number = int(0.0150 * len(source_dna_sequence)) + (0 if random.random() > 0.5 else 1)
        insert_number = int(0.0075 * len(source_dna_sequence)) + (0 if random.random() > 0.5 else 1)
        delete_number = int(0.0075 * len(source_dna_sequence)) + (0 if random.random() > 0.5 else 1)

        target_dna_sequence = list(source_dna_sequence)
        while True:
            for _ in range(mutate_number):
                location = random.randint(0, len(target_dna_sequence) - 1)
                source = target_dna_sequence[location]
                target = random.choice(list(filter(lambda base: base != source, ["A", "C", "G", "T"])))
                target_dna_sequence[location] = target

            for _ in range(insert_number):
                location = random.randint(0, len(target_dna_sequence))
                target_dna_sequence.insert(location, random.choice(["A", "C", "G", "T"]))

            for _ in range(delete_number):
                location = random.randint(0, len(target_dna_sequence) - 1)
                del target_dna_sequence[location]

            if "".join(target_dna_sequence) != source_dna_sequence:
                target_dna_sequence = "".join(target_dna_sequence)
                break

            target_dna_sequence = list(source_dna_sequence)

        target_dna_sequences.append(target_dna_sequence)
    random.shuffle(target_dna_sequences)
    return target_dna_sequences

if __name__ == '__main__':
    import time

    A = Coding_Cluster()
    n = 40 + 20
    in_seq = tc.randint(0,3,[n],dtype=tc.int64).reshape(n,1)
    print(A.check_supp(in_seq))
    # in_seq = tc.tensor([2, 2, 2, 0, 2, 1, 0, 1, 1, 1, 0, 1, 0, 2, 1, 2, 0, 2, 1, 0, 0, 1, 1, 0]).reshape(n,1)
    x = A.do_encoding(in_seq)
    print(x)
    x = wet_process(x)
    print(x)
    y = A.do_decoding(x)

    in_seq = in_seq.reshape(-1)
    print(in_seq)
    print(y)
    print(y.shape,in_seq.shape )
    print(tc.all((y==in_seq)))
    

    # seq = A.to_nuc_seqs(x)
    # for i in seq:
    #     A.collecte_seq(i)
    # A.decoding()
    # # print(tabs_tensor[1])
    # unit = 10
    # # ind = vmap(lambda x: tc.tensor([ for i in range(u)]))(tc.arange(0,10))
    # # print(ind)
    # n = 16
    # # [[x & (2 ** (2 * unit - 2 * i - 1)), x & (2 ** (2 * unit - 2 * i - 2))] for i in range(unit)]
    # f = (vmap(lambda x:tc.stack(tuple([x & (2 ** (2 * unit - i - 1)) for i in range(2 * unit)])).type(tc.bool)))
    # f2 = (vmap(lambda x:tc.stack(tuple([x[2 * i + 1] + 2 * x[2 * i] for i in range(unit)]))))
    # x = tc.arange(0,10)
    # print(f(x))
    # print(f2(f(x)))
    pass