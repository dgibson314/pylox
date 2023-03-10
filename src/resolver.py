from enum import Enum, auto

from pylox_ast.expr import ExprVisitor
from pylox_ast.stmt import StmtVisitor


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter, runtime):
        self.interpreter = interpreter
        self.runtime = runtime
        # Each element in the stack is a dict representing a single block scope.
        # Keys are variable names, values are bools.
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve(self, x):
        match x:
            case list():
                for stmt in x:
                    self.resolve(stmt)
            case _:
                x.accept(self)

    def resolve_function(self, function, ftype):
        # Keep track of whether we're inside a function declaration
        cached_ftype = self.current_function
        self.current_function = ftype

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()
        self.current_function = cached_ftype

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if self.scopes:
            if name.lexeme in self.scopes[-1]:
                self.runtime.error(name, "Already a variable with this name in this scope.")
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

    def visit_class(self, stmt):
        cached_ctype = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                self.runtime.error(stmt.superclass.name, "A class can't inherit from itself.")

            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass:
            self.end_scope()

        self.current_class = cached_ctype

    def visit_expression(self, stmt):
        self.resolve(stmt.expression)

    def visit_function(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_print(self, stmt):
        self.resolve(stmt.expression)

    def visit_return(self, stmt):
        if self.current_function is FunctionType.NONE:
            self.runtime.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.current_function is FunctionType.INITIALIZER:
                self.runtime.error(stmt.keyword, "Can't return a value from an initializer")
            self.resolve(stmt.value)

    def visit_var(self, var):
        self.declare(var.name)
        if var.initializer:
            self.resolve(var.initializer)
        self.define(var.name)

    def visit_while(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_variable(self, expr):
        if self.scopes and (self.scopes[-1].get(expr.name.lexeme, None) is False):
            self.runtime.error(expr.name, "Can't read local variable in its own initializer")
        self.resolve_local(expr, expr.name)

    def visit_assign(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call(self, expr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)

    def visit_get(self, expr):
        self.resolve(expr.object_)

    def visit_grouping(self, expr):
        self.resolve(expr.expression)

    def visit_literal(self, expr):
        return None

    def visit_logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_set(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object_)

    def visit_super(self, expr):
        if self.current_class == ClassType.NONE:
            self.runtime.error(expr.keyword, "Can't user 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            self.runtime.error(expr.keyword, "Can't user 'super' in a class with no superclass.")
        self.resolve_local(expr, expr.keyword)

    def visit_this(self, expr):
        if self.current_class is ClassType.NONE:
            self.runtime.error(expr.keyword, "Can't use 'this' outside of a class.")
            return None

        self.resolve_local(expr, expr.keyword)

    def visit_unary(self, expr):
        self.resolve(expr.right)
