class RuntimeException(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Return(RuntimeException):
    def __init__(self, value):
        super().__init__(None, None)
        self.value = value
