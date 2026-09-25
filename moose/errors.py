# MooseSyntaxError, MooseRuntimeError: carry a message and a source line number.


class MooseError(Exception):
    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line


class MooseSyntaxError(MooseError):
    pass


class MooseRuntimeError(MooseError):
    pass
