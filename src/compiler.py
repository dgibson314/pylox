from collections import namedtuple
from enum import Enum
import pdb

from lox_chunk import Chunk
from lox_chunk import OpCode as OP
from lox_value import Value
from tokens import TokenType as TT

PREC_NONE = 0
PREC_ASSIGNMENT = 1
PREC_OR = 2
PREC_AND = 3
PREC_EQUALITY = 4
PREC_COMPARISON = 5
PREC_TERM = 6
PREC_FACTOR = 7
PREC_UNARY = 8
PREC_CALL = 9
PREC_PRIMARY = 10

ParseRule = namedtuple("ParseRule", ["prefix", "infix", "precedence"])

class PrattParser():
   
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

        self.index = -1
        self.current = None
        self.had_error = False
        self.panic_mode = False

        self.chunk = Chunk()

        self.parse_rules = {
            TT.LEFT_PAREN:      ParseRule(self.grouping, None, PREC_NONE),
            TT.RIGHT_PAREN:     ParseRule(None, None, PREC_NONE),
            TT.LEFT_BRACE:      ParseRule(None, None, PREC_NONE),
            TT.RIGHT_BRACE:     ParseRule(None, None, PREC_NONE),
            TT.COMMA:           ParseRule(None, None, PREC_NONE),
            TT.DOT:             ParseRule(None, None, PREC_NONE),
            TT.MINUS:           ParseRule(self.unary, self.binary, PREC_TERM),
            TT.PLUS:            ParseRule(None, self.binary, PREC_TERM),
            TT.SEMICOLON:       ParseRule(None, None, PREC_NONE),
            TT.SLASH:           ParseRule(None, self.binary, PREC_FACTOR),
            TT.STAR:            ParseRule(None, self.binary, PREC_FACTOR),
            TT.BANG:            ParseRule(self.unary, None, PREC_NONE),
            TT.BANG_EQUAL:      ParseRule(None, self.binary, PREC_EQUALITY),
            TT.EQUAL:           ParseRule(None, None, PREC_NONE),
            TT.EQUAL_EQUAL:     ParseRule(None, self.binary, PREC_EQUALITY),
            TT.GREATER:         ParseRule(None, self.binary, PREC_COMPARISON),
            TT.GREATER_EQUAL:   ParseRule(None, self.binary, PREC_COMPARISON),
            TT.LESS:            ParseRule(None, self.binary, PREC_COMPARISON),
            TT.LESS_EQUAL:      ParseRule(None, self.binary, PREC_COMPARISON),
            TT.IDENTIFIER:      ParseRule(self.variable, None, PREC_NONE),
            TT.STRING:          ParseRule(self.string, None, PREC_NONE),
            TT.ELSE:            ParseRule(None, None, PREC_NONE),
            TT.FALSE:           ParseRule(self.literal, None, PREC_NONE),
            TT.FOR:             ParseRule(None, None, PREC_NONE),
            TT.IF:              ParseRule(None, None, PREC_NONE),
            TT.NIL:             ParseRule(self.literal, None, PREC_NONE),
            TT.OR:              ParseRule(None, None, PREC_NONE),
            TT.NUMBER:          ParseRule(self.number, None, PREC_NONE),
            TT.RETURN:          ParseRule(None, None, PREC_NONE),
            TT.THIS:            ParseRule(None, None, PREC_NONE),
            TT.TRUE:            ParseRule(self.literal, None, PREC_NONE),
            TT.VAR:             ParseRule(None, None, PREC_NONE),
            TT.EOF:             ParseRule(None, None, PREC_NONE),
        }

    def compile(self):
        self.advance()

        while not self.match(TT.EOF):
            self.declaration()

        self.end_compiler()
        return self.chunk

    def advance(self):
        if self.current and self.current._type == TT.EOF:
            return self.error("Unexpected EOF")
        self.previous = self.current
        self.index += 1
        self.current = self.tokens[self.index]
        if self.current == TT.ERROR:
            self.error_at_current(self.current.lexeme)

    def match(self, token_type):
        if self.current._type != token_type:
            return False
        if self.current._type == TT.EOF:
            return True
        self.advance()
        return True

    def consume(self, token_type, message):
        if self.current._type == token_type:
            self.advance()
            return

        self.error_at_current(message)

    def error_at_current(self, message):
        self.error_at(self.current, message)

    def error(self, message):
        self.error_at(self.tokens[self.index-2], message)

    def error_at(self, token, message):
        if self.panic_mode:
            return
        self.panic_mode = True

        print(f"[line {token.line}] Error", end="")

        if token._type == TT.EOF:
            print(" at end", end="")
        else:
            print(f" at {token.lexeme}", end="")

        print(f": {message}")

        self.had_error = True

    def emit_byte(self, op):
        self.chunk.write(op, self.previous.line)

    def emit_bytes(self, op1, op2):
        self.emit_byte(op1)
        self.emit_byte(op2)

    def emit_return(self):
        self.emit_byte(OP.RETURN)

    def emit_constant(self, value):
        constant_index = self.chunk.add_constant(value)
        self.emit_bytes(OP.CONSTANT, constant_index)

    def end_compiler(self):
        self.emit_return()

    def binary(self):
        tt_type = self.previous._type

        # Compile the right operand
        precedence = self.parse_rules[tt_type].precedence
        rule = self.parse_rules[tt_type]
        self.parse_precedence(rule.precedence + 1)

        match tt_type:
            case TT.BANG_EQUAL:    self.emit_bytes(OP.EQUAL, OP.NOT)
            case TT.EQUAL_EQUAL:   self.emit_byte(OP.EQUAL)
            case TT.GREATER:       self.emit_byte(OP.GREATER)
            case TT.GREATER_EQUAL: self.emit_bytes(OP.LESS, OP.NOT)
            case TT.LESS:          self.emit_byte(OP.LESS)
            case TT.LESS_EQUAL:    self.emit_bytes(OP.GREATER, OP.NOT)
            case TT.PLUS:          self.emit_byte(OP.ADD)
            case TT.MINUS:         self.emit_byte(OP.SUBTRACT)
            case TT.STAR:          self.emit_byte(OP.MULTIPLY)
            case TT.SLASH:         self.emit_byte(OP.DIVIDE)
            case _:
                raise Exception("Unreachable binary operator type")

    def literal(self):
        match self.previous._type:
            case TT.FALSE: self.emit_byte(OP.FALSE)
            case TT.NIL:   self.emit_byte(OP.NIL)
            case TT.TRUE:  self.emit_byte(OP.TRUE)
            case _:
                raise Exception("Unreachable literal token type")

    def grouping(self):
        self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")

    def expression(self):
        self.parse_precedence(PREC_ASSIGNMENT)

    def define_variable(self, global_idx):
        self.emit_bytes(OP.DEFINE_GLOBAL, global_idx)

    def var_declaration(self):
        global_idx = self.parse_variable("Expect variable name.")

        if self.match(TT.EQUAL):
            self.expression()
        else:
            self.emit_byte(OP.NIL)

        self.consume(TT.SEMICOLON, "Expect ';' after variable declaration.")

        self.define_variable(global_idx)

    def expression_statement(self):
        self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        self.emit_byte(OP.POP)

    def print_statement(self):
        self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        self.emit_byte(OP.PRINT)

    def synchronize(self):
        self.panic_mode = False

        # Skip tokens until we reach something that looks like a statement boundary
        while self.current._type != TT.EOF:
            if self.previous._type == TT.SEMICOLON:
                return
            match self.current._type:
                case TT.CLASS \
                   | TT.FUN \
                   | TT.VAR \
                   | TT.FOR \
                   | TT.IF \
                   | TT.WHILE \
                   | TT.PRINT \
                   | TT.RETURN:
                    return
                case _: pass
            self.advance()

    def declaration(self):
        if self.match(TT.VAR):
            self.var_declaration()
        else:
            self.statement()

        if self.panic_mode:
            self.synchronize()

    def statement(self):
        if self.match(TT.PRINT):
            self.print_statement()
        else:
            self.expression_statement()

    def number(self):
        # Number tokens store the number as a `float` in the `literal` field
        value = Value(self.previous.literal)
        self.emit_constant(value)

    def string(self):
        self.emit_constant(Value(self.previous.literal))

    def variable(self, can_assign):
        self.named_variable(self.previous, can_assign)

    def named_variable(self, tok_name, can_assign):
        arg_idx = self.identifier_constant(tok_name)

        if can_assign and self.match(TT.EQUAL):
            self.expression()
            self.emit_bytes(OP.SET_GLOBAL, arg_idx)
        else:
            self.emit_bytes(OP.GET_GLOBAL, arg_idx)

    def unary(self):
        tt_type = self.previous._type

        # Compile the operand
        self.parse_precedence(PREC_UNARY)

        # Emit the operator instruction
        match tt_type: 
            case TT.BANG: self.emit_byte(OP.NOT)
            case TT.MINUS: self.emit_byte(OP.NEGATE)
            case _:
                # Unreachable
                return

    def parse_precedence(self, precedence):
        self.advance()
        prefix_rule = self.parse_rules[self.previous._type].prefix
        if prefix_rule == None:
            self.error("Expect expression.")
            return

        can_assign = precedence <= PREC_ASSIGNMENT

        if prefix_rule == self.variable:
            prefix_rule(can_assign)
        else:
            prefix_rule()

        while (precedence <= self.parse_rules[self.current._type].precedence):
            self.advance()
            infix_rule = self.parse_rules[self.previous._type].infix
            infix_rule()

        if can_assign and self.match(TT.EQUAL):
            self.error("Invalid assignment target.")

    def identifier_constant(self, tok_name):
        value = Value(tok_name.lexeme)
        constant_index = self.chunk.add_constant(value)
        return constant_index

    def parse_variable(self, message):
        self.consume(TT.IDENTIFIER, message)
        return self.identifier_constant(self.previous)
