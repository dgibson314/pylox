from src.exceptions import RuntimeException, Return
from src.lox_token import Token


class Environment():
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def __str__(self):
        return f"{self.values} |> {self.enclosing}"

    def define(self, name, value):
        self.values[name] = value

    def get_at(self, distance, name):
        if isinstance(name, Token):
            return self.ancestor(distance).values[name.lexeme]
        return self.ancestor(distance).values[name]

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance):
        """
        Walks a fixed number of hops up the parent chain and
        returns the environment there.
        """
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env

    def get(self, name):
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        # If variable isn't found in this environment, we try the enclosing one
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name, value):
        if name.lexeme in self.values.keys():
            self.define(name.lexeme, value)
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
