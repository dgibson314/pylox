from expr import *
from token import Token
from token_type import TokenType as TT


class AstPrinter(ExprVisitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary(self, bin_expr):
        return self.parenthesize(bin_expr.operator.lexeme, bin_expr.left, bin_expr.right)

    def visit_grouping(self, group_expr):
        return self.parenthesize("group", group_expr.expression)

    def visit_literal(self, lit_expr):
        return "nil" if lit_expr.value is None else str(lit_expr.value)

    def visit_unary(self, un_expr):
        return self.parenthesize(un_expr.operator.lexeme, un_expr.right)

    def parenthesize(self, name, *exprs):
        result = f"({name}"

        for expr in exprs:
            result += " "
            result += expr.accept(self)

        result += ")"
        return result


if __name__ == "__main__":
    expression = \
        Binary(
            Unary(
                Token(TT.MINUS, "-", None, 1),
                Literal(123)
            ),
            Token(TT.STAR, "*", None, 1),
            Grouping(
                Literal(45.67)
            )
        )

    print(AstPrinter().print(expression))
