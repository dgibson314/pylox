class Value():
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False

        if self.value is None and other.value is None:
            return True

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        if self.value is None:
            return "nil"
        if self.value is True:
            return "true"
        if self.value is False:
            return "false"
        return str(self.value)

    def is_bool(self):
        return isinstance(self.value, bool)

    def is_number(self):
        return isinstance(self.value, float)

    def is_string(self):
        return isinstance(self.value, str)

    def is_falsey(self):
        return self.value is None or self.value is False


class Function():
    def __init__(self, obj, arity, chunk, name):
        self.obj = obj
        self.arity = arity
        self.chunk = chunk
        self.name = name
