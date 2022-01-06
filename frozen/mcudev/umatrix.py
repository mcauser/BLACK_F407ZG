# File from https://github.com/iyassou/umatrix
__version__ = "1.1.2"

eye = lambda order: matrix(*[[int(i==j) for j in range(order)] for i in range(order)])
fill = lambda x, order, num_cols=None: matrix(*[[x]*(num_cols if num_cols is not None else order)]*order)
zeros = lambda order, num_cols=None: fill(0, order, num_cols)
ones = lambda order, num_cols=None: fill(1, order, num_cols)

_round = lambda v,p=0: round(v,p) if not isinstance(v,complex) else round(v.real,p)+round(v.imag,p)*1j
typecheck = lambda val: isinstance(val, int) or isinstance(val, float) or isinstance(val, complex)

class matrix:
	def __init__(self, *content, are_rows=True):
		assert all([typecheck(x) for y in content for x in y]), "Not all coefficients are of type int, float, or complex."
		assert all([len(entry) == len(content[0]) for entry in content]), "Given {} do not have the same length.".format("rows" if are_rows else "columns")
		self.rows = list(content) if are_rows else [[col[i] for col in content] for i in range(len(content[0]))]
	def __repr__(self):
		rows = self.rows
		shape = len(rows), len(rows[0])
		pretty_print = max([len(str(x)) for y in rows for x in y]) if shape[0] > 1 else 1
		r = "matrix( "
		for i in range(shape[0]):
			r += "["
			for j in range(shape[1]):
				r += (pretty_print-len(str(rows[i][j])))*" "+str(rows[i][j]) + ",\t"*(j!=shape[1]-1)
			r += "],\n\t" if i != shape[0]-1 else "]"
		return r + " )"
	def __str__(self):
		rows = self.rows
		shape = len(rows), len(rows[0])
		pretty_print = max([len(str(x)) for y in rows for x in y]) if shape[0] > 1 else 1
		s = "["
		for i in range(shape[0]):
			if i:
				s += " "
			for j in range(shape[1]):
				s += (pretty_print-len(str(rows[i][j])))*" "+str(rows[i][j]) + ",\t"*(j!=shape[1]-1)
			s += ",\n" if i != shape[0]-1 else "]"
		return s
	@property
	def cols(self):
		return [[row[i] for row in self.rows] for i in range(len(self.rows[0]))]
	@property
	def shape(self):
		return len(self.rows), len(self.rows[0])
	def reshape(self, m, n=None, inplace=False):
		shape = len(self.rows), len(self.rows[0])
		flat = [self.rows[i][j] for i in range(shape[0]) for j in range(shape[1])]
		assert (m if n is None else m*n) == shape[0]*shape[1], "Shape {} is not compatible with current shape {}.".format((1,m) if n is None else (m,n), shape)
		if not inplace:
			return matrix(flat) if n is None else matrix(*[flat[i*n:i*n+n] for i in range(m)])
		self.rows = [flat] if n is None else [flat[i*n:i*n+n] for i in range(m)]
	def apply(self, func, inplace=False):
		assert callable(func), "First argument must be a callable function with an int, float, or complex return."
		rows = self.rows
		if not inplace:
			return matrix(*[[func(rows[i][j]) for j in range(len(rows[0]))] for i in range(len(rows))])
		for i in range(len(rows)):
			for j in range(len(rows[0])):
				self.rows[i][j] = func(rows[i][j])
	def copy(self):
		return matrix(*[[self.rows[i][j] for j in range(len(self.rows[0]))] for i in range(len(self.rows))])
	def round(self, places=0, inplace=False):
		if not inplace:
			rows = self.rows
			return matrix(*[[_round(rows[i][j],places) for j in range(len(rows[0]))] for i in range(len(rows))])
		for i in range(len(rows)):
			for j in range(len(rows[0])):
				self.rows[i][j] = _round(rows[i][j],places)
	def __eq__(self, other):
		assert isinstance(other, matrix), "Cannot compare matrix and {}.".format(type(other))
		rows = self.rows
		shape = len(rows), len(rows[0])
		if shape != other.shape:
			return False
		for i in range(shape[0]):
			for j in range(shape[1]):
				if rows[i][j] != other.rows[i][j]:
					return False
		return True
	def __ne__(self, other):
		return not self.__eq__(other)
	def __pos__(self):
		return self.copy()
	def __neg__(self):
		return matrix(*[[-self.rows[i][j] for j in range(len(self.rows[0]))] for i in range(len(self.rows))])
	def __add__(self, other):
		assert isinstance(other, matrix), "Cannot add matrix and {}.".format(type(other))
		rows = self.rows
		shape = len(rows), len(rows[0])
		assert shape == other.shape
		return matrix(*[[rows[i][j]+other.rows[i][j] for j in range(shape[1])] for i in range(shape[0])])
	def __radd__(self, other):
		return self.__add__(other)
	def __iadd__(self, other):
		self = self.__add__(other)
		return self
	def __sub__(self, other):
		assert isinstance(other, matrix), "Cannot subtract {} from matrix.".format(type(other))
		rows = self.rows
		shape = len(rows), len(rows[0])
		assert shape == other.shape
		return matrix(*[[rows[i][j]-other.rows[i][j] for j in range(shape[1])] for i in range(shape[0])])
	def __rsub__(self, other):
		return other.__sub__(self)
	def __isub__(self, other):
		self = self.__sub__(other)
		return self
	def __mul__(self, other):
		assert isinstance(other, matrix) or typecheck(other), "Cannot multiply matrix and {}.".format(type(other))
		rows = self.rows
		if isinstance(other, matrix):
			assert len(rows[0]) == len(other.rows), "Incompatible matrix sizes {} and {}.".format(self.shape, other.shape)
			return matrix(*[[sum([k for k in map(lambda x,y: x*y, row, col)]) for col in other.cols] for row in rows])
		return matrix(*[[rows[i][j]*other for j in range(len(rows[0]))] for i in range(len(rows))])
	def __rmul__(self, other):
		return other.__mul__(self) if isinstance(other, matrix) else self.__mul__(other)
	def __imul__(self, other):
		self = self.__mul__(other)
		return self
	def __pow__(self, exponent):
		assert isinstance(exponent, int), "Exponent must be an int, cannot be {}.".format(type(exponent))
		if exponent < 0:
			return self.copy() if not exponent%2 else self.inverse()
		if not exponent:
			return eye(self.order)
		result = self.copy()
		for i in range(1, exponent):
			result *= self
		return result
	def __abs__(self):
		return self.det
	def __getitem__(self, *args):
		if isinstance(args[0], tuple):
			a00, a01, rows = args[0][0], args[0][1], self.rows
			if isinstance(a00, slice):
				if isinstance(a01, slice):
					return matrix(*[row[a01] for row in rows[a00]])
				return matrix(*[[row[a01]] for row in rows[a00]])
			elif isinstance(a01, slice):
				return matrix(*[row[a01] for row in [rows[a00]]])
			return matrix(*[[row[a01]] for row in [rows[a00]]])
		return self.rows[args[0]]
	def __setitem__(self, *args):
		sub = args[1]
		if isinstance(args[0], tuple):
			norm_slice = lambda s, rows: (s.start if s.start is not None else 0, s.stop if s.stop is not None else (len(self.rows) if rows else len(self.rows[0])), s.step if s.step is not None else 1)
			a00, a01 = args[0]
			a00_slice, a01_slice = [isinstance(x, slice) for x in [a00, a01]]
			if a00_slice:
				a00_iter = norm_slice(a00, True)
			if a01_slice:
				a01_iter = norm_slice(a01, False)
			if a00_slice:
				if a01_slice:
					assert all([len(s) == (a01_iter[1]-a01_iter[0])//a01_iter[2] for s in sub])
					assert all([typecheck(x) for y in sub for x in y])
					for i in range(*a00_iter):
						for j in range(*a01_iter):
							self.rows[i][j] = sub[(i//a00_iter[2])-a00_iter[0]][(j//a01_iter[2])-a01_iter[0]]
				else:
					assert len(sub) == (a00_iter[1]-a00_iter[0]+1)//a00_iter[2]
					assert all([typecheck(x) for x in sub])
					for i in range(*a00_iter):
						self.rows[i][a01] = sub[(i-a00_iter[0])//a00_iter[2]]
			elif a01_slice:
				assert len(sub) == (a01_iter[1]-a01_iter[0]+1)//a01_iter[2]
				assert all([typecheck(x) for x in sub])
				for j in range(*a01_iter):
					self.rows[a00][j] = sub[(j-a01_iter[0])//a01_iter[2]]
		else:
			check = len(self.rows) - (args[0].start if isinstance(args[0], slice) else 0)
			assert len(sub) == check, "Replacement has length {}, should be {}".format(len(sub), check)
			assert all([typecheck(x) for y in sub for x in y] if isinstance(args[0], slice) else [typecheck(x) for x in sub])
			self.rows[args[0]] = sub
	@property
	def order(self):
		return len(self.rows)
	@property
	def is_square(self):
		return len(self.rows) == len(self.rows[0])
	@property
	def transpose(self):
		return matrix(*[[self.rows[i][j] for i in range(len(self.rows))] for j in range(len(self.rows[0]))])
	@property
	def trace(self):
		rows = self.rows
		order = len(rows)
		assert order == len(rows[0]), "Matrix must be square."
		return sum([rows[i][i] for i in range(order)])
	@property
	def det(self):
		rows = self.rows
		order = len(rows)
		assert order == len(rows[0]), "Matrix must be square."
		if order == 1:
			return rows[0][0]
		elif order == 2:
			a,b,c,d = [rows[i][j] for i in range(2) for j in range(2)]
			return a*d - b*c
		elif order == 3:
			a,b,c,d,e,f,g,h,i = [rows[i][j] for i in range(3) for j in range(3)]
			return a*e*i+d*h*c+g*b*f - g*e*c-a*h*f-d*b*i
		elif order == 4:
			a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p = [rows[i][j] for i in range(4) for j in range(4)]
			return a*(f*k*p+j*o*h+n*g*l - n*k*h-f*o*l-j*g*p) - b*(e*k*p+i*o*h+m*g*l - m*k*h-e*o*l-i*g*p) + c*(e*j*p+i*n*h+m*f*l - m*j*h-e*n*l-i*f*p) - d*(e*j*o+i*n*g+m*f*k - m*j*g-e*n*k-i*f*o)
		raise NotImplementedError("Can't handle matrices > 4x4.")
	@property
	def inverse(self):
		rows = self.rows
		order = len(rows)
		assert order == len(rows[0]), "Matrix must be square."
		if order == 1:
			x = rows[0][0]
			assert x, "Matrix is singular."
			return matrix([1/x])
		elif order == 2:
			a,b,c,d = [rows[i][j] for i in range(2) for j in range(2)]
			det = a*d-b*c
			assert det, "Matrix is singular."
			return matrix([d/det,-b/det],[-c/det,a/det])
		elif order == 3:
			a,b,c,d,e,f,g,h,i = [rows[i][j] for i in range(3) for j in range(3)]
			det = a*e*i+d*h*c+g*b*f - g*e*c-a*h*f-d*b*i
			assert det, "Matrix is singular."
			return matrix([(e*i-f*h)/det,(-b*i+c*h)/det,(b*f-c*e)/det],
						  [(-d*i+f*g)/det,(a*i-c*g)/det,(-a*f+c*d)/det],
						  [(d*h-e*g)/det,(-a*h+b*g)/det,(a*e-b*d)/det])
		elif order == 4:
			a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p = [rows[i][j] for i in range(4) for j in range(4)]
			M00, _M01, M02, _M03 = f*k*p+j*o*h+n*g*l-n*k*h-f*o*l-j*g*p, -e*k*p-i*o*h-m*g*l+m*k*h+e*o*l+i*g*p, e*j*p+i*n*h+m*f*l-m*j*h-e*n*l-i*f*p, -e*j*o-i*n*g-m*f*k+m*j*g+e*n*k+i*f*o
			det = a*M00 + b*_M01 + c*M02 + d*_M03
			assert det, "Matrix is singular"
			return matrix([M00/det, (-b*k*p-j*o*d-n*c*l+n*k*d+b*o*l+j*c*p)/det, (b*g*p+f*o*d+n*c*h-n*g*d-b*o*h-f*c*p)/det, (-b*g*l-f*k*d-j*c*h+j*g*d+b*k*h+f*c*l)/det],
						  [_M01/det, (a*k*p+i*o*d+m*c*l-m*k*d-a*o*l-i*c*p)/det, (-a*g*p-e*o*d-m*c*h+m*g*d+a*o*h+e*c*p)/det, (a*g*l+e*k*d+i*c*h-i*g*d-a*k*h-e*c*l)/det],
						  [M02/det, (-a*j*p-i*n*d-m*b*l+m*j*d+a*n*l+i*b*p)/det, (a*f*p+e*n*d+m*b*h-m*f*d-a*n*h-e*b*p)/det, (-a*f*l-e*j*d-i*b*h+i*f*d+a*j*h+e*b*l)/det],
						  [_M03/det, (a*j*o+i*n*c+m*b*k-m*j*c-a*n*k-i*b*o)/det, (-a*f*o-e*n*c-m*b*g+m*f*c+a*n*g+e*b*o)/det, (a*f*k+e*j*c+i*b*g-i*f*c-a*j*g-e*b*k)/det])
		raise NotImplementedError("Can't handle matrices > 4x4.")
	def is_eigenvalue(self, value):
		return not (self - value*eye(self.order)).det
	def is_eigenvector(self, vector, value):
		assert isinstance(vector, tuple) or isinstance(vector, list) or isinstance(vector, matrix)
		if isinstance(vector, matrix):
			assert vector.shape == (len(self.rows), 1)
		else:
			assert len(vector) == len(self.rows)
			vector = matrix(vector, are_rows=False)
		return self*vector == vector*value
