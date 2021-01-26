import numpy as np

# inputs:
# number of decision variables
# number of constraints
# --- size of the obj function array =  # of d.v + # of const. x2
# --- size of the const matrix = # of const, #of d.v
# obj fun coefs - fills the obj
# constraint coefs - fills the const matrix
# rhs array size = # of constraints
# concatenate, then checks.
f = open("inputs", 'r')

obj = []
const = []
rhs = []
const_ineq = []

for idx, line in enumerate(f):
	if idx == 0:
		strs = line.split()
		num_vars, num_const = int(strs[0]), int(strs[1])
		obj = np.zeros(num_vars+2*num_const)
		const = np.zeros((num_const, num_vars))
		const_ineq = np.empty(num_const, dtype=str)
		rhs = np.zeros(num_const)
	elif idx == 1:
		strs = line.split()
		for i in range(num_vars):
			obj[i] = float(strs[i])
	else:
		strs = line.split()
		for col in range(num_vars):
			const[idx-2,col] = float(strs[col])
		const_ineq[idx-2] = strs[-2]
		rhs[idx-2] = float(strs[-1])


rhs = np.array([rhs])
const_ineq = np.array(const_ineq)		

# num_vars = int(input('number of decision variables: '))
# num_const = int(input('number of constraints: '))
# obj = np.zeros(num_vars+2*num_const)
# const = np.zeros((num_const, num_vars))

# for i in range(num_vars):
# 	obj[i] = input(f'obj fun coef {i+1}: ')

#const_ineq = np.empty(num_const, dtype=str)

# for row in range(num_const):
# 	for col in range(num_vars):
# 		const[row,col] = float(input(f'constraint {row+1}, coef {col+1}: '))
# 	const_ineq[row] = input(' = , < , > : ')

# rhs = np.zeros(num_const)
# for i in range(num_const):
# 	rhs[i] = int(input(f'rhs for const {i+1}: '))
# rhs = np.array([rhs])

slack = np.identity(num_const)
artif = np.zeros((num_const,num_const))

big_matrix = np.concatenate((const, slack, artif, rhs.T), axis = 1)
Cb = np.zeros(num_const)
num_rows, num_cols = big_matrix.shape
cz = np.zeros(num_cols)
z = np.zeros(num_cols)
i = 0
M = 9999

#checking for negative values on rhs
for index, _rhs in enumerate(rhs[0]):
	if _rhs < 0:
		big_matrix[index, :] = -1*big_matrix[index, :]
		if const_ineq[index] == '>':
			const_ineq[index] = '<'
		if const_ineq[index] == '<':
			const_ineq[index] = '>'


for index, val in enumerate(const_ineq):
	if val == '=':
		big_matrix[index, num_vars+row] == 0
	elif val == '>':
		big_matrix[index, -num_const-1+index] = 1
		big_matrix[index, num_vars+index] = -1
		obj[-num_const+index] = -M
		Cb[index] = -M
	
iter = 0 

for column in big_matrix.T:
	z[i] = np.dot(column, Cb)
	i +=1
for i in range(len(obj)):
	cz[i] = obj[i]-z[i]

#need to keep track of what variables are going in/out
_in = []
out = []
while (True):
    #finding pivot element
	pivot_col = int(np.where(cz == max(cz))[0][0])
	#var going in
	
	if pivot_col in range(num_vars):
		var_in = 'x'
	elif pivot_col in range(num_vars, num_vars+num_const):
		var_in = 's'
	else:
		var_in = 'a'
	temp = []
	for i in range(num_rows):
		if big_matrix[i][pivot_col] > 0:
			temp.append(big_matrix[i][-1]/big_matrix[i][pivot_col])
		else: 
			temp.append(9999)
	pivot_row = int(np.where(temp == min(temp))[0][0])
	#var going out
	if Cb[pivot_row] == -M:
		var_out = 'a'
	elif Cb[pivot_row] != 0:
		var_out = 'x'
	else:
		var_out = 's'
	#gauss elim
	pivot = big_matrix[pivot_row][pivot_col]
	print(f'{var_in}_{pivot_col%3+1} going in {var_out}_{pivot_row%3+1} going out.')
	_in.append(f'{var_in}_{pivot_col%num_vars+1}')
	out.append(f'{var_out}_{pivot_row%num_vars+1}')
	Cb[pivot_row] = obj[pivot_col]
	big_matrix[pivot_row, :] = big_matrix[pivot_row, :]/pivot

	for i in range(num_rows):
		if i != pivot_row:
			mult = big_matrix[i][pivot_col]
			big_matrix[i, :] = big_matrix[i, :] - mult*big_matrix[pivot_row, :]
	i = 0
	
	for column in big_matrix.T:
		z[i] = np.dot(column, Cb)
		i +=1
	for i in range(len(obj)):
		cz[i] = obj[i]-z[i]


	
	if (all(i <= 0 for i in cz) or all(i !=0 for i in Cb)):
		print(f'finished in {iter+1} iterations. max value is = {z[-1]}')	
		print(f'final values : {big_matrix[:,-1]}, in: {_in}, out: {out}.')
		break
	iter += 1
