

from .Clause import Clause


class Like(Clause):

    def __init__(self, column, value):
        super().__init__()

        self.__column = column
        self.__value = value

    @property
    def column(self):
        return self.__column

    @property
    def value(self):
        return self.__value

    def get_not_clause(self):
        from .NotLike import NotLike
        return NotLike(column=self.column, value=self.value)
