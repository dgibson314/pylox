import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(THIS_DIR, "..")
AST_DIR = os.path.join(BASE_DIR, "pylox_ast")

for path in [BASE_DIR, AST_DIR]:
    if path not in sys.path:
        sys.path.append(path)


import pylox_ast.expr as Expr
import pylox_ast.stmt as Stmt

from src.lox_token import Token
from src.token_type import TokenType as TT


class ParserException(Exception):
    pass


class Parser():
    """
    EXPRESSION GRAMMAR
    ------------------
    program        → declaration* EOF
    declaration    → funDecl | varDecl | statement
    funDecl        → "fun" function
    function       → IDENTIFIER "(" parameters? ")" block
    parameters     → IDENTIFIER ( "," IDENTIFIER )*
    varDecl        → "var" IDENTIFIER ( "=" expression )? ";"
    statement      → exprStmt | forStmt | ifStmt | printStmt | returnStmt | whileStmt | block
    exprStmt       → expression ";"
    forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                     expression? ";"
                     expression? ")" statement
    ifStmt         → "if" "(" expression ")" statement ( "else" statement )?
    printStmt      → "print" expression ";"
    returnStmt     → "return" expression? ";"
    whileStmt      → "while" "(" expression ")" statement
    block          → "{" declaration* "}"
    expression     → assignment
    assignment     → IDENTIFIER "=" assignment | logic_or
    logic_or       → logic_and ( "or" logic_and )*
    logic_and      → equality ( "and" equality )*
    equality       → comparison ( ( "!=" | "==" ) comparison )*
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    term           → factor ( ( "-" | "+" ) factor )*
    factor         → unary ( ( "/" | "*" ) unary )*
    unary          → ( "!" | "-" ) unary | call
    call           → primary ( "(" arguments? ")" )*
    arguments      → expression ( "," expression )*
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
        declaration -> funDecl | varDecl | statement
        """
        try:
            if self.match_types(TT.FUN):
                return self.function("function")
            if self.match_types(TT.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserException as e:
            self.synchronize()
            return None

    def statement(self):
        """
        statement -> exprStmt | forStmt| ifStmt | printStmt | returnStmt | whileStmt | block
        """
        if self.match_types(TT.FOR):
            return self.for_statement()
        if self.match_types(TT.IF):
            return self.if_statement()
        if self.match_types(TT.PRINT):
            return self.print_statement()
        if self.match_types(TT.RETURN):
            return self.return_statement()
        if self.match_types(TT.WHILE):
            return self.while_statement()
        elif self.match_types(TT.LEFT_BRACE):
            return Stmt.Block(self.block_statement())
        return self.expression_statement()

    def for_statement(self):
        """
        forStmt -> "for" "(" ( varDecl | exprStmt | ";" )
                   expression? ";"
                   expression? ")" statement
        Inside the parentheses we have 3 clauses:
        1. The first clause is the iniitializer. We allow a variable declaration, in which case
            the variable is scoped to the rest of the `for` loop - the other two clauses and body.
        2. The condition. 
        3. The increment.
        Any of these clauses can be omitted.
        """
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match_types(TT.SEMICOLON):
            pass
        elif self.match_types(TT.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TT.SEMICOLON):
            condition = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TT.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after 'for' clauses.")

        body = self.statement()

        # The increment, if there is one, executes after the body in each iteration of the loop
        if increment:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition is None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        # If there's an initializer, it runs once before the entire loop
        if initializer:
            body = Stmt.Block([initializer, body])

        return body

    def if_statement(self):
        """
        ifStmt -> "if" "(" expression ")" statement ( "else" statement )?
        """
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after 'if' condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match_types(TT.ELSE):
            else_branch = self.statement()
        return Stmt.If(condition, then_branch, else_branch)

    def print_statement(self):
        """
        printStmt -> "print" expression ";"
        """
        value = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def return_statement(self):
        """
        returnStmt -> "return" expression? ";"
        """
        keyword = self.previous()
        value = None
        if not self.check(TT.SEMICOLON):
            value = self.expression()

        self.consume(TT.SEMICOLON, "Expect ';' after return value.")
        return Stmt.Return(keyword, value)

    def var_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match_types(TT.EQUAL):
            initializer = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def while_statement(self):
        """
        whileStmt = "while" "(" expression ")" statement
        """
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return Stmt.While(condition, body)

    def expression_statement(self):
        """
        exprStmt -> expression ";"
        """
        expr = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def function(self, kind):
        name = self.consume(TT.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TT.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TT.RIGHT_PAREN):
            parameters.append(self.consume(TT.IDENTIFIER, "Expect parameter name."))
            while self.match_types(TT.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TT.IDENTIFIER, "Expect parameter name."))
        self.consume(TT.RIGHT_PAREN, "Expect ')' after parameters.")

        # Consume '{' before calling `block_statement()`. That's bc `block_statement()` assumes
        # the brace token has already been matched.
        self.consume(TT.LEFT_BRACE, "Expect '{' before " + kind + " body")
        body = self.block_statement()
        return Stmt.Function(name, parameters, body)

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
        assignment -> IDENTIFIER "=" assignment | logic_or
        """
        expr = self._or()

        if self.match_types(TT.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assign(expr.name, value)
            self.error(equals, "Invalid assignment target.")

        return expr

    def _or(self):
        expr = self._and()
        while self.match_types(TT.OR):
            operator = self.previous()
            right = self._and()
            expr = Expr.Logical(expr, operator, right)
        return expr

    def _and(self):
        expr = self.equality()
        while self.match_types(TT.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)
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
        unary -> ( "!" | "-" ) unary | call
        """
        if self.match_types(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.call()

    def call(self):
        """
        call -> primary ( "(" arguments? ")" )*
        arguments -> expression ( "," expression )*
        """
        expr = self.primary()
        while True:
            if self.match_types(TT.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TT.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match_types(TT.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren = self.consume(TT.RIGHT_PAREN, "Expect ')' after arguments.")
        return Expr.Call(callee, paren, arguments)

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
