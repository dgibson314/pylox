import sys

from vm import VM, InterpretResult

vm = VM()

def run_file(path):
    with open(path, "r") as f:
        program = f.read()
        result = vm.interpret(program)

        if result == InterpretResult.COMPILE_ERROR:
            sys.exit(65)
        elif result == InterpretResult.RUNTIME_ERROR:
            sys.exit(70)

def run_prompt():
    while True:
        try:
            line = input("> ")
            if not line:
                break
            vm.interpret(line)
        except EOFError:
            return

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()
