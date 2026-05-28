from values import LoxValue


class ReturnSignal(Exception):
    def __init__(self, value: LoxValue) -> None:
        self.value = value
