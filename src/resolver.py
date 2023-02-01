from pylox_ast.expr import ExprVisitor
from pylox_ast.stmt import StmtVisitor


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter, runtime):
        self.interpreter = interpreter
        self.runtime = runtime
        # Each element in the stack is a dict representing a single block scope.
        # Keys are variable names, values are bools.
        self.scopes = []

    def resolve(self, x):
        match x:
            case list():
                for stmt in x:
                    self.resolve(stmt)
            case _:
                x.accept(self)

    def resolve_function(self, function):
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if self.scopes:
            self.scopes[-1][name.lexeme] = False

    def define(self, name):
        if self.scopes:
            self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return

    def visit_block(self, block):
        """
        A block statement introduces a new scope for the statements it contains
        """
        self.begin_scope()
        self.resolve(block.statements)
        self.end_scope()
        return None

    def visit_expression(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visit_function(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt)
        return None

    def visit_if(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)
        return None

    def visit_print(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visit_return(self, stmt):
        if stmt.value:
            self.resolve(stmt.value)
        return None

    def visit_var(self, var):
        self.declare(var.name)
        if var.initializer:
            self.resolve(var.initializer)
        self.define(var.name)
        return None

    def visit_while(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_variable(self, expr):
        if self.scopes and (self.scopes[-1].get(expr.name.lexeme, None) is False):
            self.runtime.error(expr.name, "Can't read local variable in its own initializer")
        self.resolve_local(expr, expr.name)
        return None

    def visit_assign(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_call(self, expr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)
        return None

    def visit_grouping(self, expr):
        self.resolve(expr.expression)
        return None

    def visit_literal(self, expr):
        return None

    def visit_logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_unary(self, expr):
        self.resolve(expr.right)
        return None



