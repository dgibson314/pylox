from collections import namedtuple
from dataclasses import dataclass
from enum import IntEnum
import pdb

from lox_chunk import Chunk
from lox_chunk import OpCode as OP
from lox_object import Object, ObjString, ObjFunction
from lox_value import Value
from tokens import TokenType as TT
from tokens import Token

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

@dataclass
class ParserLocation:
    current: Token = None
    previous: Token = None

@dataclass
class Scope:
    _locals: list
    scope_depth: int = 0

@dataclass
class Local:
    name: Token
    depth: int
    initialized: bool

class FunctionType(IntEnum):
    FUNCTION = 0
    SCRIPT = 1

class PrattParser():
   
    def __init__(self, function_type, scanner, location=ParserLocation()):
        self.function_type = function_type
        self.scanner = scanner
        self.loc = location

        self.had_error = False
        self.panic_mode = False

        self.scope = Scope([], 0)

        # Compiler implicitly claims stack slot zero for internal use
        self.add_local(Token(None, "", None, None))

        self._function = ObjFunction()
        if self.function_type != FunctionType.SCRIPT:
            self._function.name = self.loc.previous.lexeme

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
            TT.OR:              ParseRule(None, self.or_, PREC_OR),
            TT.AND:             ParseRule(None, self.and_, PREC_AND),
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

        return self.end_compiler()

    @property
    def chunk(self):
        return self._function.chunk

    def advance(self):
        self.loc.previous = self.loc.current

        while True:
            self.loc.current = self.scanner.scan_token()
            if self.loc.current is not TT.ERROR:
                print(self.loc.current)
                break
            self.error_at_current(self.loc.current.lexeme)

    def match(self, token_type):
        if self.loc.current._type != token_type:
            return False
        if self.loc.current._type == TT.EOF:
            return True
        self.advance()
        return True

    def consume(self, token_type, message):
        if self.loc.current._type == token_type:
            self.advance()
            return

        self.error_at_current(message)

    def error_at_current(self, message):
        self.error_at(self.loc.current, message)

    def error(self, message):
        self.error_at(self.loc.previous, message)

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
        self.chunk.write(op, self.loc.previous.line)

    def emit_bytes(self, op1, op2):
        self.emit_byte(op1)
        self.emit_byte(op2)

    def emit_loop(self, loop_start):
        self.emit_byte(OP.LOOP)

        # +1 to take into account size of OP.LOOP's operand
        offset = len(self.chunk.code) - loop_start + 1

        self.emit_byte(offset)

    def emit_jump(self, op):
        """
        Emits a bytecode instruction and writes a placeholder operand for the jump
        offset.
        Returns the offset of the emitted instruction in the chunk.
        """
        self.emit_byte(op)
        self.emit_byte(None)
        return len(self.chunk.code) - 1

    def emit_return(self):
        self.emit_byte(OP.RETURN)

    def emit_constant(self, value):
        constant_index = self.chunk.add_constant(value)
        self.emit_bytes(OP.CONSTANT, constant_index)

    def patch_jump(self, offset):
        # -1 to adjust for the bytecode for the jump offset itself
        jump = len(self.chunk.code) - offset - 1
        self.chunk.code[offset] = jump

    def end_compiler(self):
        self.emit_return()
        return self._function

    def begin_scope(self):
        self.scope.scope_depth += 1

    def end_scope(self):
        self.scope.scope_depth -= 1

        while self.scope._locals and self.scope._locals[-1].depth > self.scope.scope_depth:
            self.emit_byte(OP.POP)
            self.scope._locals.pop()

    def binary(self):
        tt_type = self.loc.previous._type

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
        match self.loc.previous._type:
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

    def block(self):
        while self.loc.current._type != TT.RIGHT_BRACE and self.loc.current._type != TT.EOF:
            self.declaration()
        self.consume(TT.RIGHT_BRACE, "Expect '}' after block.")

    def fun_declaration(self):
        global_idx = self.parse_variable("Expect function name.")

        # Mark the function declaration's variable "initialized" as soon as we compile
        # the name so that it can be referenced in the function's body without generating
        # an error.
        if self.scope.scope_depth > 0:
            self.scope._locals[-1].initialized = True

        self.function(FunctionType.FUNCTION)

        self.define_variable(global_idx)

    def function(self, function_type):
        ic = PrattParser(function_type, self.scanner)
        ic.begin_scope()

        ic.loc = self.loc

        ic.consume(TT.LEFT_PAREN, "Expect '(' after function name.")
        if ic.loc.current._type != TT.RIGHT_PAREN:
            # TODO: this is a straightforward implementation of the `do-while` loop
            # from CLox. Should clean this up.
            ic._function.arity += 1
            constant_idx = ic.parse_variable("Expect parameter name.")
            ic.define_variable(constant_idx)
            while ic.match(TT.COMMA):
                ic._function.arity += 1
                constant_idx = ic.parse_variable("Expect parameter name.")
                ic.define_variable(constant_idx)

        ic.consume(TT.RIGHT_PAREN, "Expect ')' after parameters.")
        ic.consume(TT.LEFT_BRACE, "Expect '{' before function body.")

        ic.block()

        nested_function = ic.end_compiler()
        constant_index = self.chunk.add_constant(Value(nested_function))
        self.emit_bytes(OP.CONSTANT, constant_index)

    def define_variable(self, global_idx):
        if self.scope.scope_depth > 0:
            self.scope._locals[-1].initialized = True
            return
        self.emit_bytes(OP.DEFINE_GLOBAL, global_idx)

    def or_(self):
        else_jump = self.emit_jump(OP.JUMP_IF_FALSE)
        end_jump = self.emit_jump(OP.JUMP)

        self.patch_jump(else_jump)
        self.emit_byte(OP.POP)

        self.parse_precedence(PREC_OR)
        self.patch_jump(end_jump)

    def and_(self):
        end_jump = self.emit_jump(OP.JUMP_IF_FALSE)

        self.emit_byte(OP.POP)
        self.parse_precedence(PREC_AND)

        self.patch_jump(end_jump)

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

    def for_statement(self):
        self.begin_scope()
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(TT.SEMICOLON):
            # No initializer
            pass
        elif self.match(TT.VAR):
            self.var_declaration()
        else:
            self.expression_statement()

        # Condition expression for exit
        loop_start = len(self.chunk.code)
        exit_jump = -1
        if not self.match(TT.SEMICOLON):
            self.expression()
            self.consume(TT.SEMICOLON, "Expect ';' after loop condition.")

            # Jump out of loop if condition is false
            exit_jump = self.emit_jump(OP.JUMP_IF_FALSE)
            # Pop condition expression off stack
            self.emit_byte(OP.POP)

        if not self.match(TT.RIGHT_PAREN):
            body_jump = self.emit_jump(OP.JUMP)

            increment_start = len(self.chunk.code)
            self.expression()
            self.emit_byte(OP.POP)
            self.consume(TT.RIGHT_PAREN, "Expect ')' after for clauses.")

            self.emit_loop(loop_start)
            loop_start = increment_start
            self.patch_jump(body_jump)

        self.statement()
        self.emit_loop(loop_start)

        if exit_jump != -1:
            self.patch_jump(exit_jump)
            self.emit_byte(OP.POP)

        self.end_scope()

    def if_statement(self):
        # The OP.POP instructions are to handle cleaning up the condition value
        # on the stack.
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'if'.")
        self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after condition.")

        then_jump = self.emit_jump(OP.JUMP_IF_FALSE)
        self.emit_byte(OP.POP)
        self.statement()

        else_jump = self.emit_jump(OP.JUMP)

        self.patch_jump(then_jump)
        self.emit_byte(OP.POP)

        if self.match(TT.ELSE):
            self.statement()
        self.patch_jump(else_jump)

    def print_statement(self):
        self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        self.emit_byte(OP.PRINT)

    def while_statement(self):
        # Keep track of the start of statement; we'll jump back here after evaluating
        # the body of the loop
        loop_start = len(self.chunk.code)

        self.consume(TT.LEFT_PAREN, "Expect '(' after 'while'.")
        self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after condition.")

        exit_jump = self.emit_jump(OP.JUMP_IF_FALSE)
        self.emit_byte(OP.POP)
        self.statement()

        self.emit_loop(loop_start)

        self.patch_jump(exit_jump)
        self.emit_byte(OP.POP)

    def synchronize(self):
        self.panic_mode = False

        # Skip tokens until we reach something that looks like a statement boundary
        while self.loc.current._type != TT.EOF:
            if self.loc.previous._type == TT.SEMICOLON:
                return
            match self.loc.current._type:
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
        if self.match(TT.FUN):
            self.fun_declaration()
        elif self.match(TT.VAR):
            self.var_declaration()
        else:
            self.statement()

        if self.panic_mode:
            self.synchronize()

    def statement(self):
        if self.match(TT.PRINT):
            self.print_statement()
        elif self.match(TT.IF):
            self.if_statement()
        elif self.match(TT.FOR):
            self.for_statement()
        elif self.match(TT.WHILE):
            self.while_statement()
        elif self.match(TT.LEFT_BRACE):
            self.begin_scope()
            self.block()
            self.end_scope()
        else:
            self.expression_statement()

    def number(self):
        # Number tokens store the number as a `float` in the `literal` field
        value = Value(self.loc.previous.literal)
        self.emit_constant(value)

    def string(self):
        interned = ObjString(self.loc.previous.literal)
        self.emit_constant(Value(interned))
        #self.emit_constant(Value(self.loc.previous.literal))

    def variable(self, can_assign):
        self.named_variable(self.loc.previous, can_assign)

    def named_variable(self, name, can_assign):
        get_op = OP.GET_GLOBAL
        set_op = OP.SET_GLOBAL

        arg = self.resolve_local(self.scope, name)
        if arg != -1:
            get_op = OP.GET_LOCAL
            set_op = OP.SET_LOCAL
        else:
            arg = self.identifier_constant(name)

        if can_assign and self.match(TT.EQUAL):
            self.expression()
            self.emit_bytes(set_op, arg)
        else:
            self.emit_bytes(get_op, arg)

    def resolve_local(self, scope, name):
        for index, local in reversed(list(enumerate(scope._locals))):
            if local.name.lexeme == name.lexeme:
                # var a = a;
                if local.initialized == False:
                    self.error("Can't read local variable in its own initializer.")
                return index
        return -1

    def unary(self):
        tt_type = self.loc.previous._type

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
        prefix_rule = self.parse_rules[self.loc.previous._type].prefix
        if prefix_rule == None:
            self.error("Expect expression.")
            return

        can_assign = precedence <= PREC_ASSIGNMENT

        if prefix_rule == self.variable:
            prefix_rule(can_assign)
        else:
            prefix_rule()

        while (precedence <= self.parse_rules[self.loc.current._type].precedence):
            self.advance()
            infix_rule = self.parse_rules[self.loc.previous._type].infix
            infix_rule()

        if can_assign and self.match(TT.EQUAL):
            self.error("Invalid assignment target.")

    def identifier_constant(self, tok_name):
        value = Value(tok_name.lexeme)
        constant_index = self.chunk.add_constant(value)
        return constant_index

    def add_local(self, name):
        # Locals are uninitialized when first declared
        local = Local(name, self.scope.scope_depth, False)
        self.scope._locals.append(local)

    def declare_variable(self):
        # Global variables are implicitly declared.
        if self.scope.scope_depth == 0:
            return

        var_name = self.loc.previous

        # It's an error to have two variables with the same name in the same local scope
        for local in self.scope._locals[::-1]:
            if local.depth != -1 and local.depth < self.scope.scope_depth:
                break
            if var_name == local.name:
                self.error("Already variable with this name in this scope.")

        self.add_local(self.loc.previous)

    def parse_variable(self, message):
        self.consume(TT.IDENTIFIER, message)

        self.declare_variable()
        if self.scope.scope_depth > 0:
            return 0

        return self.identifier_constant(self.loc.previous)
