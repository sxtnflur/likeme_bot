from enum import auto, Enum


class PaymentTypeEnum(int, Enum):
    avatar = auto()
    generations = auto()

    avatar_simple = auto()
    avatar_portrait = auto()