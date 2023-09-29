from enum import Enum
import operator

from chunk import OpCode as OP

InterpretResult = Enum("InterpretResult", [
    "INTERPRET_OK", "INTERPRET_COMPILE_ERROR", "INTERPRET_RUNTIME_ERROR"
])

BIN_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}

class VM():
    def __init__(self, chunk):
        self.chunk = chunk
        self.ip = None
        self.stack = []

    def interpret(self):
        self.ip = 0
        return self.run()

    def read_op(self):
        op = self.chunk.code[self.ip]
        self.ip += 1
        return op

    def read_constant(self):
        index = self.read_op()
        return self.chunk.constants[index]

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def _binary_op(self, op_char):
        op = BIN_OPS[op_char]
        b = self.pop()
        a = self.pop()
        c = op(a, b)
        self.push(c)

    def run(self):
        while True:
            instruction = self.read_op()
            match instruction:
                case OP.CONSTANT:
                    constant = self.read_constant()
                    self.push(constant)
                case OP.ADD:
                    self._binary_op("+")
                case OP.SUBTRACT:
                    self._binary_op("-")
                case OP.MULTIPLY:
                    self._binary_op("*")
                case OP.DIVIDE:
                    self._binary_op("/")
                case OP.NEGATE:
                    self.push(-self.pop())
                case OP.RETURN:
                    print(self.pop())
                    return InterpretResult.INTERPRET_OK
                case _:
                    print("Unknown opcode {instruction}")
                    return InterpretResult.INTERPRET_RUNTIME_ERROR
