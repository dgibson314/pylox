from src.exceptions import RuntimeException
from src.lox_callable import LoxCallable


class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def __call__(self, interpreter, arguments):
        instance = LoxInstance(self)

        # Look for an "init" method. If we find one, immediately bind
        # and invoke it just like a normal method call
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance)(interpreter, arguments)

        return instance

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name):
        return self.methods.get(name, None)


class LoxInstance():
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return f"{self.klass.name} instance"

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeException(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value
