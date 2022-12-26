# TODO: make simple function and use name: transactional
class Transactional:
    def __init__(self) -> None:
        self.__transactional__ = True

    def __call__(self, cls: type):
        cls.__transactional__ = self.__transactional__

        return cls
