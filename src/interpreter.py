import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(THIS_DIR, "..")
AST_DIR = os.path.join(BASE_DIR, "pylox_ast")

for path in [BASE_DIR, AST_DIR]:
    if path not in sys.path:
        sys.path.append(path)

from pylox_ast.expr import ExprVisitor
from pylox_ast.stmt import StmtVisitor
from src.environment import Environment
from src.exceptions import RuntimeException, Return
from src.lox_callable import LoxCallable, ClockCallable, LoxFunction
from src.lox_token import Token
from src.token_type import TokenType as TT


class Interpreter(ExprVisitor, StmtVisitor):
    _globals = Environment()
    _globals.define("clock", ClockCallable())

    def __init__(self, runtime):
        self.runtime = runtime
        self.environment = self._globals
        self.locals = {}

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as error:
            self.runtime.runtime_error(error)

    def visit_literal(self, expr):
        return expr.value

    def visit_logical(self, expr):
        """
        Since Lox is dynamically typed, we allow operands of any type and use
        truthiness to determine what each operand represents. We apply similar
        reasoning to the result. Instead of promising to literally return `true`
        or `false`, the logic operator returns the results of the operands 
        themselves.
        Example:
            > print "hi" or 2;  // "hi"
            > print nil or "yes"; // "yes"
        """
        left = self.evaluate(expr.left)

        # Short circuit on OR statements where the lhs is true
        if (expr.operator.type == TT.OR):
            if self.is_truthy(left):
                return left
        # Short circuit on AND statements where the lhs is false
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

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

    def check_zero_divisor(self, operator, right):
        if right == 0.0:
            raise RuntimeException(operator, "Cannot divide by zero.")

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
                self.check_zero_divisor(expr.operator, right)
                return left / right
            case TT.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case TT.PLUS:
                match left, right:
                    case (float(), float()) | (str(), str()):
                        return left + right
                    case _:
                        msg = "Operands must be two numbers or two string"
                        raise RuntimeException(expr.operator, msg)

    def visit_call(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeException(expr.paren,
                    f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return callee(self, arguments)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def execute_block(self, statements, new_env):
        """
        To execute code within a given scope, this method updates the interpreter's
        `environment` field, visits all the statements, then restores the previous value.
        """
        prev_env = self.environment
        try:
            self.environment = new_env
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = prev_env

    def visit_block(self, stmt):
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))
        return None

    def visit_expression(self, stmt):
        self.evaluate(stmt.expression)
        return None

    def visit_function(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_if(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)
        return None

    def visit_print(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_return(self, stmt):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visit_var(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_while(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_variable(self, expr):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr):
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self._globals.get(name)

    def visit_assign(self, expr):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr, None)
        if distance:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)

        return value
    
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
            case bool():
                if obj:
                    return "true"
                return "false"
            case str():
                return f'"{str(obj)}"'
            case _:
                return str(obj)
