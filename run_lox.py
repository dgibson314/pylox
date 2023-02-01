import sys

from src.lox import Lox


if __name__ == "__main__":
    lox = Lox()
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()
