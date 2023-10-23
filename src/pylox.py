import sys

from compiler import PrattParser
from scanner import Scanner
from vm import VM, InterpretResult

vm = VM()

class PyLox():
    def __init__(self):
        self.had_error = False

    def run_file(self, path):
        with open(path, "r") as f:
            program = f.read()
            self.run(program)

        if self.had_error:
            sys.exit(65)

    def run_prompt(self):
        while (True):
            try:
                line = input("> ")
                if not line:
                    break
                self.run(line)
                self.had_error = False

            except EOFError:
                return

    def error(self, line, message):
        self.report(line, "", message)

    def report(self, line, where, message):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def run(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        #for token in tokens:
            #print(token)

        compiler = PrattParser(tokens)
        chunk = compiler.compile()

        if compiler.had_error:
            return None

        return vm.interpret(chunk)


if __name__ == "__main__":
    pylox = PyLox()

    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        pylox.run_file(sys.argv[1])
    else:
        pylox.run_prompt()
