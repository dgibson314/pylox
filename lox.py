import sys


class Lox():
    def __init__(self):
        self.had_error = False

    def run_file(self, path):
        with open(path, "r") as f:
            self.run(f.readlines())

            if self.had_error:
                sys.exit(65)

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            self.had_error = False

    def run(self, program):
        scanner = Scanner(program)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    def error(self, line, message):
        self.report(line, "", message)

    def report(self, line, where, message):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

if __name__ == "__main__":
    lox = Lox()
    if len(sys.argv) > 2:
        print("Usage: jlox [script]")
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()
