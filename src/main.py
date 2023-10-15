import sys

from lox_chunk import Chunk
from lox_chunk import OpCode as OP
from vm import VM

if __name__ == "__main__":
    chunk = Chunk()
    constant = chunk.add_constant(1.2)
    chunk.write(OP.CONSTANT, 123)
    chunk.write(constant, 123)
    chunk.write(OP.NEGATE, 123)

    c2 = chunk.add_constant(2.5)
    chunk.write(OP.CONSTANT, 123)
    chunk.write(c2, 123)

    chunk.write(OP.ADD, 123)

    chunk.write(OP.RETURN, 123)

    chunk.disassemble("test chunk")

    vm = VM(chunk)
    vm.interpret(chunk)
