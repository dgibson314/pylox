from collections import namedtuple
from enum import Enum
import pdb

from lox_chunk import Chunk
from lox_chunk import OpCode as OP
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
            TT.BANG:            ParseRule(None, None, PREC_NONE),
            TT.BANG_EQUAL:      ParseRule(None, None, PREC_NONE),
            TT.EQUAL:           ParseRule(None, None, PREC_NONE),
            TT.EQUAL_EQUAL:     ParseRule(None, None, PREC_NONE),
            TT.GREATER:         ParseRule(None, None, PREC_NONE),
            TT.GREATER_EQUAL:   ParseRule(None, None, PREC_NONE),
            TT.LESS:            ParseRule(None, None, PREC_NONE),
            TT.NUMBER:          ParseRule(self.number, None, PREC_NONE),
            TT.RETURN:          ParseRule(None, None, PREC_NONE),
            TT.EOF:             ParseRule(None, None, PREC_NONE),
        }

    def compile(self):
        self.advance()
        self.expression()
        self.match(TT.EOF, "Expect end of expression.")
        self.end_compiler()
        return self.chunk

    def advance(self):
        self.previous = self.current
        self.index += 1
        self.current = self.tokens[self.index]
        if self.current == TT.ERROR:
            self.error_at_current(self.current.lexeme)

    def match(self, token_type, message):
        if self.current._type != token_type:
            self.error_at_current(message)

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

        print(f"[line {token.line} Error", end="")

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
            case TT.PLUS:   self.emit_byte(OP.ADD)
            case TT.MINUS:  self.emit_byte(OP.SUBTRACT)
            case TT.STAR:   self.emit_byte(OP.MULTIPLY)
            case TT.SLASH:  self.emit_byte(OP.DIVIDE)
            case _:
                raise Exception("Unreachable binary operator type")

    def grouping(self):
        self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")

    def expression(self):
        self.parse_precedence(PREC_ASSIGNMENT)

    def number(self):
        # Number tokens store the number as a `float` in the `literal` field
        value = self.previous.literal
        self.emit_constant(value)

    def unary(self):
        tt_type = self.previous._type

        # Compile the operand
        self.parse_precedence(PREC_UNARY)

        # Emit the operator instruction
        match tt_type: 
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
        prefix_rule()

        while (precedence <= self.parse_rules[self.current._type].precedence):
            self.advance()
            infix_rule = self.parse_rules[self.previous._type].infix
            infix_rule()
