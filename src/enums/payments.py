from enum import auto, Enum


class PaymentTypeEnum(int, Enum):
    any = auto()
    avatar = auto()
    generations = auto()