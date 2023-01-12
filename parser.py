import ast.expr as Expr
import ast.stmt as Stmt

from token import Token
from token_type import TokenType as TT


class ParserException(Exception):
    pass


class Parser():
    """
    EXPRESSION GRAMMAR
    ------------------
    program        → declaration* EOF
    declaration    → varDecl | statement
    varDecl        → "var" IDENTIFIER ( "=" expression )? ";"
    statement      → exprStmt | printStmt | block
    block          → "{" declaration* "}"
    exprStmt       → expression ";"
    printStmt      → "print" expression ";"
    expression     → assignment
    assignment     → IDENTIFIER "=" assignment | equality
    equality       → comparison ( ( "!=" | "==" ) comparison )*
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    term           → factor ( ( "-" | "+" ) factor )*
    factor         → unary ( ( "/" | "*" ) unary )*
    unary          → ( "!" | "-" ) unary
                   | primary
    primary        → NUMBER | STRING | "true" | "false" | "nil"
                   | "(" expression ")" | IDENTIFIER
    """
    def __init__(self, runtime, tokens):
        self.runtime = runtime
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """
        program -> statement* EOF
        """
        statements = []
        while not self.at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        """
        declaration -> varDecl | statement
        """
        try:
            if self.match_types(TT.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserException as e:
            self.synchronize()
            return None

    def statement(self):
        """
        statement -> exprStmt | printStmt
        """
        if self.match_types(TT.PRINT):
            return self.print_statement()
        elif self.match_types(TT.LEFT_BRACE):
            return Stmt.Block(self.block_statement())
        return self.expression_statement()

    def print_statement(self):
        """
        printStmt -> "print" expression ";"
        """
        value = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def var_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match_types(TT.EQUAL):
            initializer = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def expression_statement(self):
        """
        exprStmt -> expression ";"
        """
        expr = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def block_statement(self):
        """
        """
        statements = []
        while ((not self.check(TT.RIGHT_BRACE)) and (not self.at_end())):
            statements.append(self.declaration())
        self.consume(TT.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self):
        """
        assignment -> IDENTIFIER "=" assignment | equality
        """
        expr = self.equality()

        if self.match_types(TT.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assign(expr.name, value)
            self.error(equals, "Invalid assignment target.")

        return expr

    def expression(self):
        """
        expression -> assignment
        """
        return self.assignment()

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

        if self.match_types(TT.IDENTIFIER):
            return Expr.Variable(self.previous())

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
