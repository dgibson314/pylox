from abc import ABC, abstractmethod


class ExprVisitor():
    def visit_binary(expr): raise NotImplementedError
    def visit_grouping(expr): raise NotImplementedError
    def visit_literal(expr): raise NotImplementedError
    def visit_unary(expr): raise NotImplementedError


class Expr(ABC):
    @abstractmethod
    def accept(self):
        raise NotImplementedError


class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary(self)


class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping(self)


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary(self)


