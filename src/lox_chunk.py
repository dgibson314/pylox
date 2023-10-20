from enum import Enum

OpCode = Enum("OpCode", [
    "CONSTANT",
    "NIL",
    "TRUE",
    "FALSE",
    "EQUAL",
    "GREATER",
    "LESS",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "DIVIDE",
    "NOT",
    "NEGATE",
    "RETURN",
])

class Chunk():
    def __init__(self):
        self.code = []
        self.lines = []
        self.constants = []

    def add_constant(self, value):
        self.constants.append(value)
        return len(self.constants) - 1

    def write(self, opcode, line):
        self.code.append(opcode)
        self.lines.append(line)

    @staticmethod
    def simple_instruction(op, offset):
        print(op.name)
        return offset + 1

    def constant_instruction(self, op, offset):
        constant = self.code[offset + 1]
        value = self.constants[constant]
        print(f"{op.name} {constant} ", end="")
        print(value.value)
        return offset + 2

    def disassemble_instruction(self, offset):
        print(f"{str(offset).zfill(4)} ", end="")

        op = self.code[offset]
        match op:
            case OpCode.CONSTANT:
                return self.constant_instruction(op, offset)
            case OpCode.NEGATE \
               | OpCode.RETURN \
               | OpCode.FALSE \
               | OpCode.ADD \
               | OpCode.EQUAL \
               | OpCode.GREATER \
               | OpCode.LESS \
               | OpCode.SUBTRACT \
               | OpCode.MULTIPLY \
               | OpCode.DIVIDE \
               | OpCode.NIL \
               | OpCode.TRUE \
               | OpCode.DIVIDE \
               | OpCode.NOT:
                return self.simple_instruction(op, offset)
            case _:
                print(f"Unknown opcode {op}")
                return offset + 1

    def disassemble(self, name="test"):
        print(f"== {name} ==")

        offset = 0
        while (offset < len(self.code)):
            offset = self.disassemble_instruction(offset)