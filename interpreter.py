from expr import *
from token import Token
from token_type import TokenType as TT


class RuntimeException(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Interpreter(ExprVisitor):
    def __init__(self, runtime):
        self.runtime = runtime

    def interpret(self, expr):
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except RuntimeException as error:
            self.runtime.runtime_error(error)

    def visit_literal(self, expr):
        return expr.value

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary(self, expr):
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TT.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right
            case TT.BANG:
                return not self.is_truthy(right)

    def check_number_operand(self, operator, right):
        match right:
            case float(): return
            case _: raise RuntimeException(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        match left, right:
            case float(), float(): return
            case _: raise RuntimeException(operator, "Operands must be numbers.")

    def visit_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TT.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TT.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TT.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TT.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TT.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TT.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TT.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            case TT.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return left / right
            case TT.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case TT.PLUS:
                match left, right:
                    case float(), float():
                        return left + right
                    case str(), str():
                        return left + right
                    case _:
                        print(f"Type of left: {type(left)}")
                        print(f"Type of right: {type(right)}")
                        msg = "Operands must be two numbers or two string"
                        raise RuntimeException(expr.operator, msg)

    def evaluate(self, expr):
        return expr.accept(self)
    
    @staticmethod
    def is_truthy(value):
        match value:
            case None:
                return False
            case bool():
                return value
            case _:
                return True

    @staticmethod
    def is_equal(x, y):
        match x, y:
            case None, None:
                return True
            case None, _:
                return False
            case _, _:
                return x == y

    @staticmethod
    def stringify(obj):
        match obj:
            case None:
                return "nil"
            case float():
                text = str(obj)
                if text.endswith(".0"):
                    text = text[:-2]
                return text
            case _:
                return f'"{str(obj)}"'

def interpret(expr):
    match expr:
        case Literal():
            return expr.value
        case Grouping():
            return interpret(expr.expression)
        case Unary():
            right = interpret(expr.right)
            match expr.operator.type:
                case TT.MINUS:
                    return -right
                case TT.BANG:
                    return (not is_truthy(right))
        case Binary():
            left = interpret(expr.left)
            right = interpret(expr.right)
            match expr.operator.type:
                case TT.GREATER:
                    return left > right
                case TT.GREATER_EQUAL:
                    return left >= right
                case TT.LESS:
                    return left < right
                case TT.LESS_EQUAL:
                    return left <= right
                case TT.BANG_EQUAL:
                    return not is_equal(left, right)
                case TT.EQUAL_EQUAL:
                    return is_equal(left, right)
                case TT.MINUS:
                    return left - right
                case TT.SLASH:
                    return left / right
                case TT.STAR:
                    return left * right
                case TT.PLUS:
                    match left, right:
                        case float(), float() | str(), str():
                            return left + right
                        case _:
                            # TODO: handle better
                            print("Can't add different types!")
                            return None


def is_truthy(value):
    if value is None: return False
    if isinstance(value, bool): return value
    return True


def is_equal(x, y):
    if (x is None and b is None): return True
    if x is None: return False
    return x == y
