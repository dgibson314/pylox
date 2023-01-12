from abc import ABC, abstractmethod


class StmtVisitor():
    def visit_block(expr): raise NotImplementedError
    def visit_expression(expr): raise NotImplementedError
    def visit_print(expr): raise NotImplementedError
    def visit_var(expr): raise NotImplementedError


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


class Print(Stmt):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print(self)


class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var(self)


