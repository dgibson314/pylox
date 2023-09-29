import sys

from chunk import Chunk
from chunk import OpCode as OP
from pylox import PyLox
from vm import VM

if __name__ == "__main__":
    chunk = Chunk()
    constant = chunk.add_constant(1.2)
    chunk.write(OP.CONSTANT, 123)
    chunk.write(constant, 123)
    chunk.write(OP.NEGATE, 123)

    chunk.write(OP.RETURN, 123)

    chunk.disassemble("test chunk")

    vm = VM(chunk)
    vm.interpret()
