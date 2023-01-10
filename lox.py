import sys

from ast_printer import AstPrinter
from interpreter import Interpreter
from parser import Parser
from scanner import Scanner
from token import Token
from token_type import TokenType

class Lox():
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run_file(self, path):
        with open(path, "r") as f:
            self.run(f.readlines())

            if self.had_error:
                sys.exit(65)
            if self.had_runtime_error:
                sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
                if not line:
                    break
                self.run(line)
                self.had_error = False
            except EOFError:
                break

    def run(self, program):
        scanner = Scanner(self, program)
        tokens = scanner.scan_tokens()

        parser = Parser(self, tokens)
        expression = parser.parse()

        if self.had_error: return
        
        self.interpreter.interpret(expression)

    def error(self, line, message):
        self.report(line, "", message)

    def runtime_error(self, error):
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True

    def parse_error(self, token, message):
        if token.type is TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", message)

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
