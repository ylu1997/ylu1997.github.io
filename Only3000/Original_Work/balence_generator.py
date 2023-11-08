from utils import multiply_elements, convert_to_custom_base, filter_condition, save_code_table


path_code_table = 'nuc1.txt'
base = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
p = multiply_elements(base)
nucleo = ['A', 'G', 'C', 'T']

ans = []

print('Start generation.')
for i in range(p):
    tmp = convert_to_custom_base(i, base)
    if filter_condition(tmp,duplicate=2):
        tmp = ''.join([nucleo[i] for i in tmp])
        # print(tmp)
        ans.append(tmp)
print('Total number of code: ',len(ans))
print('-----------------------------------------')

print('Saving the code as: ',path_code_table)
save_code_table(ans, path_code_table)
print('Finished!')
print('-----------------------------------------')
