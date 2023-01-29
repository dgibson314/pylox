import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(THIS_DIR, "..")
AST_DIR = os.path.join(BASE_DIR, "pylox_ast")

for path in [BASE_DIR, AST_DIR]:
    if path not in sys.path:
        sys.path.append(path)


from pylox_ast.expr import *
from token import Token
from token_type import TokenType as TT

from ast_printer import pretty_printer, parenthesize


def rpn(expr):
    match expr:
        case Literal():
            return "nil" if expr.value is None else str(expr.value)
        case Binary():
            return rpn(expr.left) + " " + rpn(expr.right) + " " + expr.operator.lexeme
        case Grouping():
            return rpn(expr.expression)
        case _:
            raise NotImplementedError


if __name__ == "__main__":
    expression = \
        Binary(
            Grouping(
                Binary(
                    Literal(1),
                    Token(TT.PLUS, "+", None, 1),
                    Literal(2)
                )
            ),
            Token(TT.STAR, "*", None, 1),
            Grouping(
                Binary(
                    Literal(4),
                    Token(TT.MINUS, "-", None, 1),
                    Literal(3),
                )
            )
        )

    ex2 = \
        Binary(
            Literal(1),
            Token(TT.PLUS, "+", None, 1),
            Literal(2)
        )

    print(rpn(expression))