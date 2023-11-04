from enum import Enum

OpCode = Enum("OpCode", [
    "CONSTANT",
    "NIL",
    "TRUE",
    "FALSE",
    "EQUAL",
    "POP",
    "GET_LOCAL",
    "SET_LOCAL",
    "GET_GLOBAL",
    "SET_GLOBAL",
    "DEFINE_GLOBAL",
    "GREATER",
    "LESS",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "DIVIDE",
    "NOT",
    "NEGATE",
    "PRINT",
    "JUMP",
    "JUMP_IF_FALSE",
    "LOOP",
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
        print(f"{op.name}\t{constant}  {value.value}")
        return offset + 2

    def byte_instruction(self, op, offset):
        slot = self.code[offset + 1]
        print(f"{op.name} {slot}")
        return offset + 2

    def jump_instruction(self, op, sign, offset):
        jump = self.code[offset + 1]
        print(f"{op.name} {offset} {offset + 2 + sign * jump}")
        return offset + 2

    def disassemble_instruction(self, offset):
        print(f"{str(offset).zfill(4)} ", end="")

        op = self.code[offset]
        match op:
            case OpCode.JUMP \
               | OpCode.JUMP_IF_FALSE:
                return self.jump_instruction(op, 1, offset)

            case OpCode.LOOP:
                return self.jump_instruction(op, -1, offset)

            case OpCode.GET_LOCAL \
               | OpCode.SET_LOCAL:
                return self.byte_instruction(op, offset)

            case OpCode.CONSTANT \
               | OpCode.GET_GLOBAL \
               | OpCode.SET_GLOBAL \
               | OpCode.DEFINE_GLOBAL :
                return self.constant_instruction(op, offset)

            case OpCode.NEGATE \
               | OpCode.RETURN \
               | OpCode.FALSE \
               | OpCode.POP \
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
               | OpCode.PRINT \
               | OpCode.NOT:
                return self.simple_instruction(op, offset)

            case _:
                print(f"Unknown opcode {op}")
                return offset + 1

    def disassemble(self, name="<script>"):
        print(f"== {name} ==")

        offset = 0
        while (offset < len(self.code)):
            offset = self.disassemble_instruction(offset)

    def debug_constants(self):
        for constant in self.constants:
            print(constant)

