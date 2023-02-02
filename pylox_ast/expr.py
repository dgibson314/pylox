from abc import ABC, abstractmethod


class ExprVisitor():
    def visit_assign(expr): raise NotImplementedError
    def visit_binary(expr): raise NotImplementedError
    def visit_call(expr): raise NotImplementedError
    def visit_get(expr): raise NotImplementedError
    def visit_grouping(expr): raise NotImplementedError
    def visit_literal(expr): raise NotImplementedError
    def visit_logical(expr): raise NotImplementedError
    def visit_set(expr): raise NotImplementedError
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


class Call(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call(self)


class Get(Expr):
    def __init__(self, object_, name):
        self.object_ = object_
        self.name = name

    def accept(self, visitor):
        return visitor.visit_get(self)


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


class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical(self)


class Set(Expr):
    def __init__(self, object_, name, value):
        self.object_ = object_
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set(self)


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


