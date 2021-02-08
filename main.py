import numpy as np

f = open("inputs", 'r')

obj = []
const = []
rhs = []
const_ineq = []
var_const = []
all_vars = []
for idx, line in enumerate(f):
    if idx == 0:
        strs = line.split()
        num_vars, num_const = int(strs[0]), int(strs[1])
        obj = np.zeros(num_vars + 2 * num_const)
        const = np.zeros((num_const, num_vars))
        rhs = np.zeros(num_const)
        var_const = np.zeros(num_vars)
    elif idx == 1:
        strs = line.split()
        for i in range(num_vars):
            var_const[i] = int(strs[i])
    elif idx == 2:
        strs = line.split()
        for i in range(num_vars):
            obj[i] = float(strs[i])
    elif idx == 3:
        if line.strip() == 'min':
            obj = -1 * obj
    else:
        strs = line.split()
        for col in range(num_vars):
            const[idx - 4, col] = float(strs[col])
        const_ineq.append(strs[-2])
        rhs[idx - 4] = float(strs[-1])

for index, val in enumerate(var_const):
    if val == 0:
        num_vars = num_vars + 1
        obj = np.insert(obj, index + 1, -1 * obj[index])
        ratio = np.zeros((num_const, 1))
        const1 = const[:, :index + 1]
        const2 = const[:, index + 1:]
        const = np.concatenate((const1, ratio, const2), axis=1)
        for i in range(num_const):
            const[i, index + 1] = -1 * const[i, index]

rhs = np.array([rhs])
slack = np.identity(num_const)
artif = np.zeros((num_const, num_const))

big_matrix = np.concatenate((const, slack, artif, rhs.T), axis=1)
Cb = np.zeros(num_const)
num_rows, num_cols = big_matrix.shape
cz = np.zeros(num_cols)
z = np.zeros(num_cols)
i = 0
M = 9999

# checking for negative values on rhs
for index, _rhs in enumerate(rhs[0]):
    if _rhs < 0:
        big_matrix[index, :] = -1 * big_matrix[index, :]
        if const_ineq[index] == '>=':
            const_ineq[index] = '<='
        if const_ineq[index] == '<=':
            const_ineq[index] = '>='

for index, val in enumerate(const_ineq):
    if val == '==':
        big_matrix[index, num_vars + index] = 0
    elif val == '>=':
        big_matrix[index, -num_const - 1 + index] = 1
        big_matrix[index, num_vars + index] = -1
        obj[-num_const + index] = -M
        Cb[index] = -M

iter = 0

for column in big_matrix.T:
    z[i] = np.dot(column, Cb)
    i += 1
for i in range(len(obj)):
    cz[i] = obj[i] - z[i]

_in = []
out = []
while (True):
    # finding pivot element
    pivot_col = int(np.where(cz > 0)[0][0])
    # var going in

    if pivot_col in range(num_vars):
        var_in = 'x'
    elif pivot_col in range(num_vars, num_vars + num_const):
        var_in = 's'
    else:
        var_in = 'a'
    ratio = []
    for i in range(num_rows):
        if big_matrix[i][pivot_col] > 0:
            ratio.append(big_matrix[i][-1] / big_matrix[i][pivot_col])
        else:
            ratio.append(-1)

    if (all(i < 0 for i in ratio)):
        print('Unbounded')
        break
    else:
        pivot_row = int(np.where(ratio == min([i for i in ratio if i >= 0]))[0][0])
    # var going out
    if Cb[pivot_row] == -M:
        var_out = 'a'
    elif Cb[pivot_row] != 0:
        var_out = 'x'
    else:
        var_out = 's'
    # gauss elim
    pivot = big_matrix[pivot_row][pivot_col]
    print(f'{var_in}_{pivot_col % 3 + 1} going in {var_out}_{pivot_row % 3 + 1} going out.')
    _in.append(f'{var_in}_{pivot_col % num_vars + 1}')
    out.append(f'{var_out}_{pivot_row % num_vars + 1}')
    Cb[pivot_row] = obj[pivot_col]
    big_matrix[pivot_row, :] = big_matrix[pivot_row, :] / pivot

    for i in range(num_rows):
        if i != pivot_row:
            mult = big_matrix[i][pivot_col]
            big_matrix[i, :] = big_matrix[i, :] - mult * big_matrix[pivot_row, :]
    i = 0

    for column in big_matrix.T:
        z[i] = np.dot(column, Cb)
        i += 1
    for i in range(len(obj)):
        cz[i] = obj[i] - z[i]

    if (all(i <= 0 for i in cz) or all(i != 0 for i in Cb)):
        print(f'finished in {iter + 1} iterations. max value is = {z[-1]}')
        print(f'final values : {big_matrix[:, -1]}, in: {_in}, out: {out}.')
        break
    iter += 1
