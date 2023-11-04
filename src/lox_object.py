from abc import ABC, abstractmethod
from enum import Enum

OBJ_STRING = 1

class Object(ABC):
    instances = []

    def __init__(self, obj_type):
        self.obj_type = obj_type
        Object.instances.append(self)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

class ObjString(Object):
    def __init__(self, chars):
        super().__init__(OBJ_STRING)
        self.chars = chars
        self.hash = hash(chars)

    def __str__(self):
        return self.chars

    def __eq__(self, other):
        if not isinstance(other, ObjString):
            return False
        return self.hash == other.hash

    def __add__(self, other):
        if not isinstance(other, ObjString):
            raise TypeError
        return ObjString(self.chars + other.chars)
