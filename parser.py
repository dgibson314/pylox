import expr as Expr

from token import Token
from token_type import TokenType as TT


class ParserException(Exception):
    pass


class Parser():
    """
    EXPRESSION GRAMMAR
    ------------------
    expression     → equality ;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           → factor ( ( "-" | "+" ) factor )* ;
    factor         → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary
                   | primary ;
    primary        → NUMBER | STRING | "true" | "false" | "nil"
                   | "(" expression ")" ;
    """
    def __init__(self, runtime, tokens):
        self.runtime = runtime
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParserException:
            return None

    def expression(self):
        """
        expression -> equality
        """
        return self.equality()

    def equality(self):
        """
        equality -> comparison ( ( "!=" | "==" ) comparison )*
        """
        expr = self.comparison()

        while self.match_types(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def comparison(self):
        """
        comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )*
        """
        expr = self.term()

        while self.match_types(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self):
        """
        term -> factor ( ( "-" | "+" ) factor )*
        """
        expr = self.factor()

        while self.match_types(TT.MINUS, TT.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self):
        """
        factor -> unary ( ( "/" | "*" ) unary )*
        """
        expr = self.unary()

        while self.match_types(TT.SLASH, TT.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self):
        """
        unary -> ( "!" | "-" ) unary | primary
        """
        if self.match_types(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self):
        """
        primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")"
        """
        if self.match_types(TT.FALSE): return Expr.Literal(False)
        if self.match_types(TT.TRUE):  return Expr.Literal(True)
        if self.match_types(TT.NIL):   return Expr.Literal(None)

        if self.match_types(TT.NUMBER, TT.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match_types(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)

        self.error(self.peek(), "Expect expression.")

    def consume(self, token_type, message):
        if self.check(token_type): 
            return self.advance()

        self.error(self.peek(), message)

    def error(self, token, message):
        self.runtime.parse_error(token, message)
        raise ParserException

    def synchronize(self):
        """
        Disards tokens until it thinks it's found a statement boundary.
        """
        self.advance()

        while not self.at_end():
            if self.previous().type is TT.SEMICOLON: return

            match self.peek().type:
                case TT.CLASS | TT.FUN | TT.VAR | TT.FOR | TT.IF | TT.WHILE | \
                     TT.PRINT | TT.RETURN:
                    return

            self.advance()

    def match_types(self, *types):
        """
        Checks if the current token has any of the given types.
        If so, it consumes the token and returns True.
        Else, returns False.
        """
        for tt_type in types:
            if self.check(tt_type):
                self.advance()
                return True
        return False

    def check(self, tt_type):
        if self.at_end():
            return False
        return self.peek().type == tt_type

    def advance(self):
        """
        Consumes the current token and returns it.
        """
        if not self.at_end():
            self.current += 1
        return self.previous()

    def at_end(self):
        return self.peek().type == TT.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
