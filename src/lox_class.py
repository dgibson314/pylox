from src.lox_callable import LoxCallable


class LoxClass(LoxCallable):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __call__(self, interpreter, arguments):
        return LoxInstance(self)

    def arity(self):
        return 0


class LoxInstance():
    def __init__(self, klass):
        self.klass = klass

    def __str__(self):
        return f"{self.klass.name} instance"
