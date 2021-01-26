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

nr_decision_vars = int(input('number of decision variables: '))
nr_const = int(input('number of constraints: '))
obj = np.zeros(nr_decision_vars+2*nr_const)
const = np.zeros((nr_const, nr_decision_vars))

for i in range(nr_decision_vars):
	obj[i] = input(f'obj fun coef {i+1}: ')
print(obj)
const_ineq = np.empty(nr_const, dtype=str)

for row in range(nr_const):
	for col in range(nr_decision_vars):
		const[row,col] = float(input(f'constraint {row+1}, coef {col+1}: '))
	const_ineq[row] = input(' = , < , > : ')

rhs = np.zeros(nr_const)
for i in range(nr_const):
	rhs[i] = int(input(f'rhs for const {i+1}: '))
rhs = np.array([rhs])

slack = np.identity(nr_const)
art = np.zeros((nr_const,nr_const))

big_matrix = np.concatenate((const, slack, art, rhs.T), axis = 1)
Cb = np.zeros(nr_const)
num_rows, num_cols = big_matrix.shape
cz = np.zeros(num_cols)
z = np.zeros(num_cols)
i = 0
M = 9999

#checking for negative values on rhs
for _rhs in rhs[0]:
	if _rhs < 0:
		index = int(np.where(rhs == _rhs)[0])
		big_matrix[index, :] = -1*big_matrix[index, :]
		if const_ineq[index] == '>':
			const_ineq[index] = '<'
		if const_ineq[index] == '<':
			const_ineq[index] = '>'

i = 0
j = 0
for val in const_ineq:
	if val == '=':
		index = int(np.where(const_ineq == val)[0][i])
		big_matrix[index, nr_decision_vars+row] == 0
		i += 1
	elif val == '>':
		index = int(np.where(const_ineq == val)[0][j])
		big_matrix[index, -nr_const-1+index] = 1
		big_matrix[index, nr_decision_vars+index] = -1
		obj[-nr_const+index] = -M
		Cb[index] = -M
		j += 1
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
	
	if pivot_col in range(nr_decision_vars):
		var_in = 'x'
	elif pivot_col in range(nr_decision_vars, nr_decision_vars+nr_const):
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
	_in.append(f'{var_in}_{pivot_col%3+1}')
	out.append(f'{var_out}_{pivot_row%3+1}')
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
