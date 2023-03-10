import os
import sys

from src.ast_printer import AstPrinter
from src.interpreter import Interpreter
from src.lox_token import Token
from src.parser import Parser
from src.resolver import Resolver
from src.scanner import Scanner
from src.token_type import TokenType

class Lox():
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run_file(self, path):
        with open(path, "r") as f:
            lines = f.readlines()
            program = ''.join(lines)
            self.run(program)

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
        statements = parser.parse()

        # Stop if there was a syntax error
        if self.had_error: return

        resolver = Resolver(self.interpreter, self)
        resolver.resolve(statements)

        # Stop if there was a resolution error
        if self.had_error: return
        
        self.interpreter.interpret(statements)

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
