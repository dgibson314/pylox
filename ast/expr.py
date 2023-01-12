from abc import ABC, abstractmethod


class ExprVisitor():
    def visit_assign(expr): raise NotImplementedError
    def visit_binary(expr): raise NotImplementedError
    def visit_grouping(expr): raise NotImplementedError
    def visit_literal(expr): raise NotImplementedError
    def visit_unary(expr): raise NotImplementedError
    def visit_variable(expr): raise NotImplementedError


class Expr(ABC):
    @abstractmethod
    def accept(self):
        raise NotImplementedError


class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign(self)


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


class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable(self)


