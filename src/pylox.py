import sys

from scanner import Scanner

class PyLox():
    def __init__(self, args):
        self.had_error = False

        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

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

        for token in tokens:
            print(token)



if __name__ == "__main__":
    pylox = PyLox(sys.argv)
