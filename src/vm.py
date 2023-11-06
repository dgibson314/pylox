from enum import Enum
import operator
import pdb

from compiler import PrattParser
from lox_chunk import OpCode as OP
from lox_object import Object
from lox_value import Value
from scanner import Scanner

InterpretResult = Enum("InterpretResult", [
    "OK", "COMPILE_ERROR", "RUNTIME_ERROR"
])

BIN_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "<": operator.lt,
    ">": operator.gt
}

class VM():
    def __init__(self):
        self.ip = 0
        self.stack = []
        self.globals = {}

    def interpret(self, source):
        self.ip = 0
        scanner = Scanner(source)
        compiler = PrattParser(scanner)
        self.chunk = compiler.compile()

        if compiler.had_error:
            return InterpretResult.COMPILE_ERROR

        return self.run()

    def read_op(self):
        op = self.chunk.code[self.ip]
        self.ip += 1
        return op

    def runtime_error(self, message):
        print(message)

        line = self.chunk.lines[self.ip - 1]
        print(f"[line {line}] in script")

    def read_constant(self):
        index = self.read_op()
        return self.chunk.constants[index]

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self, distance):
        index = -1 - distance
        return self.stack[index]

    def concatenate(self):
        b = self.pop().value
        a = self.pop().value
        c = Value(a + b)
        self.push(c)

    def _binary_op(self, op_char):
        if self.peek(0).is_number() and self.peek(1).is_number():
            op = BIN_OPS[op_char]
            b = self.pop().value
            a = self.pop().value
            c = Value(op(a, b))
            self.push(c)
        else:
            self.runtime_error("Operands must be numbers.")
            return InterpretResult.RUNTIME_ERROR

    def run(self):
        """
        Returns tuple of (InterpretResult, result)
        """
        self.chunk.disassemble()
        while True:
            instruction = self.read_op()
            match instruction:
                case OP.CONSTANT:
                    constant = self.read_constant()
                    self.push(constant)

                case OP.NIL:
                    self.push(Value(None))

                case OP.TRUE:
                    self.push(Value(True))

                case OP.FALSE:
                    self.push(Value(False))

                case OP.POP:
                    self.pop()

                case OP.GET_LOCAL:
                    slot = self.read_op()
                    self.push(self.stack[slot])

                case OP.SET_LOCAL:
                    slot = self.read_op()
                    self.stack[slot] = self.peek(0)

                case OP.GET_GLOBAL:
                    name = self.read_constant()
                    value = self.globals.get(name, None)
                    if value is None:
                        self.runtime_error(f"Undefined variable '{name.value}'")
                        return InterpretResult.RUNTIME_ERROR
                    self.push(value)

                case OP.SET_GLOBAL:
                    name = self.read_constant()
                    if name not in self.globals.keys():
                        self.runtime_error(f"Undefined variable '{name.value}'")
                        return InterpretResult.RUNTIME_ERROR
                    self.globals[name] = self.peek(0)

                case OP.DEFINE_GLOBAL:
                    name = self.read_constant()
                    self.globals[name] = self.peek(0)
                    self.pop()

                case OP.EQUAL:
                    b = self.pop()
                    a = self.pop()
                    self.push(Value(a == b))

                case OP.GREATER:
                    self._binary_op(">")
                case OP.LESS:
                    self._binary_op("<")
                case OP.SUBTRACT:
                    self._binary_op("-")
                case OP.MULTIPLY:
                    self._binary_op("*")
                case OP.DIVIDE:
                    self._binary_op("/")

                case OP.ADD:
                    if self.peek(0).is_string() and self.peek(1).is_string():
                        self.concatenate()
                    elif self.peek(0).is_number() and self.peek(1).is_number():
                        self._binary_op("+")
                    else:
                        self.runtime_error("Operands must be two numbers or two string")
                        return InterpretResult.RUNTIME_ERROR

                case OP.NOT:
                    old_val = self.pop()
                    new_val = Value(not(old_val.is_falsey()))
                    self.push(new_val)

                case OP.NEGATE:
                    if not self.peek(0).is_number():
                        self.runtime_error("Operand must be a number.")
                        return InterpretResult.RUNTIME_ERROR
                    self.push(Value(-self.pop().value))

                case OP.PRINT:
                    print(self.pop())

                case OP.JUMP:
                    offset = self.read_op()
                    self.ip += offset

                case OP.JUMP_IF_FALSE:
                    offset = self.read_op()
                    if self.peek(0).is_falsey():
                        self.ip += offset

                case OP.LOOP:
                    offset = self.read_op()
                    self.ip -= offset

                case OP.RETURN:
                    # TODO: now that we've implemented print statements, should we just
                    # be returning the InterpretStatus?
                    return InterpretResult.OK

                case _:
                    print("Unknown opcode {instruction}")
                    return InterpretResult.RUNTIME_ERROR
