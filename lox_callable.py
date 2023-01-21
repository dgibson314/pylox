from abc import ABC, abstractmethod
import time

from environment import Environment
from exceptions import Return


class LoxCallable(ABC):
    @abstractmethod
    def arity(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter, arguments):
        raise NotImplementedError


class ClockCallable(LoxCallable):
    def arity(self):
        return 0
    def __call__(self, interpreter, arguments):
        # Returns current time in seconds
        return round(time.time() * 1000)
    def __str__(self):
        return "<native fn>"


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def __call__(self, interpreter, arguments):
        environment = Environment(enclosing=self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as ret:
            return ret.value

        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
