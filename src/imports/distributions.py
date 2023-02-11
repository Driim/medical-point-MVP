# flake8: noqa: S311
from random import randint


def get_level_ou_amount() -> int:
    # TODO: implement using normal distribution between 1 and 30
    return randint(1, 30)


def get_subtree_depth() -> int:
    # TODO: implement using normal distribution between 2 and 5
    return randint(2, 5)


def get_amount_of_outlets() -> int:
    # TODO: implement using normal distribution between 10 and 500
    return randint(10, 500)


def get_amount_of_devices() -> int:
    # TODO: implement using normal distribution between 10 and 100
    return randint(10, 100)


def get_amount_of_workers() -> int:
    # TODO: implement using normal distribution between 1k and 100k
    return randint(1000, 100000)
