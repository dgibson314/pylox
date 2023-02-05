from abc import ABC, abstractmethod
import time

from src.environment import Environment
from src.exceptions import Return


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
        return float(round(time.time() * 1000))
    def __str__(self):
        return "<native fn>"


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(enclosing=self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self):
        return len(self.declaration.params)

    def __call__(self, interpreter, arguments):
        environment = Environment(enclosing=self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as ret:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return ret.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
