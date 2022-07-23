from enum import Enum


class CEnum(Enum):
    def __str__(self):
        """For use in parsers"""
        return self.value

    @property
    def repr(self):
        """For printing only"""
        return f"{self.__class__.__name__}.{self.value}"
