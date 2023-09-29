from enum import Enum

OpCode = Enum("OpCode", [
    "OP_RETURN"
])

class Chunk():
    def __init__(self):
        self.code = []
        self.lines = []
        self.constants = []

    @staticmethod
    def simple_instruction(op, offset):
        print(op.name)
        return offset + 1

    def disassemble_instruction(self, offset):
        op = self.code[offset]
        match op:
            case OpCode.OP_RETURN:
                return self.simple_instruction(op, offset)
            case _:
                print(f"Unknown opcode {op}")
                return offset + 1

    def disassemble(self, name):
        print(f"== {name} ==")

        offset = 0
        while (offset < len(self.code)):
            offset = self.disassemble_instruction(offset)
