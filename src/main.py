import sys

from chunk import Chunk
from chunk import OpCode as OP
from pylox import PyLox

if __name__ == "__main__":
    chunk = Chunk()
    chunk.code.append(OP.OP_RETURN)
    chunk.disassemble("test chunk")
