from enum import Enum


class Positions(Enum):
    UNDEFINED = 0
    ADMIN = 1
    MECHANIC = 2
    ACCOUNTANT = 3


class User:
    id = -1
    login = ''
    position = Positions.UNDEFINED
