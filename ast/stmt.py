from abc import ABC, abstractmethod


class StmtVisitor():
    def visit_block(expr): raise NotImplementedError
    def visit_expression(expr): raise NotImplementedError
    def visit_function(expr): raise NotImplementedError
    def visit_if(expr): raise NotImplementedError
    def visit_print(expr): raise NotImplementedError
    def visit_return(expr): raise NotImplementedError
    def visit_var(expr): raise NotImplementedError
    def visit_while(expr): raise NotImplementedError


class Stmt(ABC):
    @abstractmethod
    def accept(self):
        raise NotImplementedError


class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block(self)


class Expression(Stmt):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression(self)


class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function(self)


class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if(self)


class Print(Stmt):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print(self)


class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return(self)


class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var(self)


class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while(self)


