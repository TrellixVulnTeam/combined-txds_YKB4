from collections import defaultdict
from sympy import Add, diff, lambdify, Eq, simplify, expand  

def is_constant(expr, vars):
    for symbol in expr.free_symbols:
        if symbol in vars:
            return False
    return True

def is_linear(expr, vars):
    if is_constant(expr, vars):
        return False

    for x in vars:
        for y in vars:
            try: 
                if not Eq(diff(expr, x, y), 0):
                    return False
            except TypeError:
                return False
    return True 

def get_linear_term(expr, vars):
    if not is_linear(expr, vars):
        raise Exception("Expression is not linear")

    result = None
    for symbol in expr.free_symbols:
        if symbol in vars:
            result = symbol
    return result

def linearize_expr(expr, variables):
    kth_sum = -expr
    Y_components = {}

    for variable in variables:
        derivative = diff(expr, variable) 
        Y_components[variable] = derivative
        kth_sum += derivative * variable
    
    return (kth_sum, Y_components)

def split_expr(eqn, vars):
    eqn = expand(eqn)

    constant_expr = 0
    variable_expr_dict = defaultdict(lambda:0)

    if isinstance(eqn, Add):
        expressions = eqn.args
    else:
        expressions = [eqn]

    for expr in expressions:
        if is_constant(expr, vars):
            constant_expr += -expr
        elif is_linear(expr, vars):
            term = get_linear_term(expr, vars)
            variable_expr_dict[term] += diff(expr, term)
        else:
            (J_expr, Y_expr_dict) =  linearize_expr(expr, vars)

            constant_expr += J_expr
            for key, value in Y_expr_dict.items():
                variable_expr_dict[key] += value
    
    return (constant_expr, variable_expr_dict)

def return_zero(*args):
    return 0

class DerivativeEntry:
    def __init__(self, derivative_var, derivative, constant_expr, variable_exprs, lambda_inputs) -> None:
        self.derivative_var = derivative_var
        self.derivative = derivative
        self.constant_expr = constant_expr
        self.variable_exprs = variable_exprs

        if constant_expr != 0:
            self.constant_eval = lambdify(lambda_inputs, constant_expr)
        else:
            self.constant_eval = return_zero

        self.variable_evals = {}
        for var, derivative in variable_exprs.items():
            self.variable_exprs[var] = derivative
            if derivative != 0:
                self.variable_evals[var] = lambdify(lambda_inputs, derivative)

    def evaluate(self, *args):
        yield (None, self.constant_eval(*args))

        for (variable, func) in self.variable_evals.items():
            yield(variable, func(*args))

class LagrangeHandler:
    def __init__(self, lagrange, constant_symbols, primal_symbols, dual_symbols) -> None:
        self.lagrange = lagrange
        self.constants = constant_symbols
        self.primals = primal_symbols
        self.duals = dual_symbols

        self.variables = self.primals + self.duals

        self.derivatives = {}

        lambda_inputs = self.constants + self.variables

        for first_order in self.variables:
            derivative = diff(lagrange, first_order)

            constant_expr, variable_exprs = split_expr(derivative, self.variables)

            self.derivatives[first_order] = DerivativeEntry(first_order, derivative, constant_expr, variable_exprs, lambda_inputs)

    def evaluate_primals(self, constant_vals, primal_vals, dual_vals):
        values = constant_vals + primal_vals + dual_vals
        return self.__evaluate_set(self.duals, values)

    def evaluate_duals(self, constant_vals, primal_vals, dual_vals):
        values = constant_vals + primal_vals + dual_vals
        return self.__evaluate_set(self.primals, values)

    def __evaluate_set(self, target_derivatives, values):
        components = []

        for variable in target_derivatives:
            entry = self.derivatives[variable]

            for (secondary_variable, result) in entry.evaluate(*values):
                components.append((variable, secondary_variable, result))
        
        return components
